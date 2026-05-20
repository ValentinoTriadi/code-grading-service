// Test harness for the Concurrent Worker Pool case (P6).
//
// IMPORTANT: this file is named with a leading underscore on purpose. The Go
// toolchain ignores files that start with "_" or ".", so this harness can sit
// in the same directory as every pool_*.go submission without clashing — each
// submission also declares `package pool` and defines `ParallelMap`, and they
// cannot all be compiled together.
//
// run_cases.py copies this file (renamed to pool_test.go) into a fresh temp
// module alongside exactly ONE submission and runs `go test -race` there.
//
// Your editor / gopls may flag `ParallelMap` as undefined while this file sits
// here alone. That is expected and harmless — the symbol is supplied by
// whichever submission run_cases.py pairs it with at run time.
//
// The tests are deliberately behavioural: they check observable output
// (values, order, length), bounded concurrency, and goroutine cleanup, so they
// hold against every implementation strategy in the dataset (indexed jobs,
// two-channel fan-in, semaphore, errgroup, static partitioning, pipeline).
package pool

import (
	"runtime"
	"sync/atomic"
	"testing"
	"time"
)

// --- helpers ---------------------------------------------------------------

// seq returns []int{0, 1, ..., n-1}.
func seq(n int) []int {
	s := make([]int, n)
	for i := range s {
		s[i] = i
	}
	return s
}

// settle gives goroutines spawned by an earlier test time to wind down before
// the goroutine-leak baseline is measured.
func settle(d time.Duration) {
	deadline := time.Now().Add(d)
	for time.Now().Before(deadline) {
		runtime.GC()
		time.Sleep(20 * time.Millisecond)
	}
}

// waitGoroutines polls the live goroutine count until it drops to <= target or
// the deadline passes, then returns the last observed count.
func waitGoroutines(target int, d time.Duration) int {
	deadline := time.Now().Add(d)
	n := runtime.NumGoroutine()
	for n > target && time.Now().Before(deadline) {
		time.Sleep(20 * time.Millisecond)
		runtime.GC()
		n = runtime.NumGoroutine()
	}
	return n
}

// --- correctness -----------------------------------------------------------

// TestBasicCorrectnessAndOrder is the core check: every out[i] must be
// fn(inputs[i]). Catches missing Wait (caller sees zero values), wrong logic,
// and output that does not line up with the input index.
func TestBasicCorrectnessAndOrder(t *testing.T) {
	inputs := seq(200)
	got := ParallelMap(inputs, 8, func(x int) int { return x*3 + 1 })
	if len(got) != len(inputs) {
		t.Fatalf("len(out)=%d, want %d", len(got), len(inputs))
	}
	for i := range inputs {
		if want := inputs[i]*3 + 1; got[i] != want {
			t.Fatalf("out[%d]=%d, want %d (wrong result, or output not aligned to input index)", i, got[i], want)
		}
	}
}

// TestOrderUnderJitter forces completion order to differ from input order:
// earlier inputs sleep longer, so they finish last. An implementation that
// appends results in completion order (or iterates a map) fails here while
// still passing TestBasicCorrectnessAndOrder.
func TestOrderUnderJitter(t *testing.T) {
	const n = 60
	inputs := seq(n)
	fn := func(x int) int {
		time.Sleep(time.Duration(n-x) * time.Millisecond) // input 0 is slowest
		return x * x
	}
	got := ParallelMap(inputs, 8, fn)
	if len(got) != n {
		t.Fatalf("len(out)=%d, want %d", len(got), n)
	}
	for i := range inputs {
		if got[i] != i*i {
			t.Fatalf("out[%d]=%d, want %d — output follows completion order, not input order", i, got[i], i*i)
		}
	}
}

// TestWorkersNonPositive checks that workers <= 0 is treated as workers = 1.
// An implementation that spawns zero workers hangs here (caught as a timeout).
func TestWorkersNonPositive(t *testing.T) {
	inputs := seq(50)
	for _, w := range []int{0, -1, -100} {
		got := ParallelMap(inputs, w, func(x int) int { return x + 7 })
		if len(got) != len(inputs) {
			t.Fatalf("workers=%d: len(out)=%d, want %d", w, len(got), len(inputs))
		}
		for i := range inputs {
			if got[i] != inputs[i]+7 {
				t.Fatalf("workers=%d: out[%d]=%d, want %d", w, i, got[i], inputs[i]+7)
			}
		}
	}
}

// TestWorkersExceedInputs checks the workers > len(inputs) case still produces
// correct output (the no-leak side of this case is covered by TestNoGoroutineLeak).
func TestWorkersExceedInputs(t *testing.T) {
	inputs := seq(5)
	got := ParallelMap(inputs, 500, func(x int) int { return x * 10 })
	if len(got) != len(inputs) {
		t.Fatalf("len(out)=%d, want %d", len(got), len(inputs))
	}
	for i := range inputs {
		if got[i] != i*10 {
			t.Fatalf("out[%d]=%d, want %d", i, got[i], i*10)
		}
	}
}

// TestEmptyInput checks empty input does not panic and returns an empty slice.
func TestEmptyInput(t *testing.T) {
	got := ParallelMap([]int{}, 8, func(x int) int { return x })
	if len(got) != 0 {
		t.Fatalf("empty input: len(out)=%d, want 0", len(got))
	}
}

// TestSingleElement is the smallest non-empty case.
func TestSingleElement(t *testing.T) {
	got := ParallelMap([]int{42}, 4, func(x int) int { return x + 1 })
	if len(got) != 1 || got[0] != 43 {
		t.Fatalf("got %v, want [43]", got)
	}
}

// TestGenericStringToInt exercises the [T, R] generics with T != R, so an
// implementation accidentally specialised to int does not slip through.
func TestGenericStringToInt(t *testing.T) {
	inputs := []string{"a", "bb", "ccc", "dddd", "eeeee"}
	got := ParallelMap(inputs, 3, func(s string) int { return len(s) })
	want := []int{1, 2, 3, 4, 5}
	if len(got) != len(want) {
		t.Fatalf("len(out)=%d, want %d", len(got), len(want))
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("out[%d]=%d, want %d", i, got[i], want[i])
		}
	}
}

// TestConcurrencyBounded verifies the pool actually runs in parallel AND never
// runs more than `workers` calls to fn at once. peak > workers means a weak or
// missing cap; peak < 2 means the work was effectively serialised.
func TestConcurrencyBounded(t *testing.T) {
	const n, workers = 60, 4
	var cur, peak int64
	fn := func(x int) int {
		c := atomic.AddInt64(&cur, 1)
		for { // CAS the running peak upward
			p := atomic.LoadInt64(&peak)
			if c <= p || atomic.CompareAndSwapInt64(&peak, p, c) {
				break
			}
		}
		time.Sleep(8 * time.Millisecond)
		atomic.AddInt64(&cur, -1)
		return x
	}
	got := ParallelMap(seq(n), workers, fn)
	if len(got) != n {
		t.Fatalf("len(out)=%d, want %d", len(got), n)
	}
	for i := 0; i < n; i++ {
		if got[i] != i {
			t.Fatalf("out[%d]=%d, want %d", i, got[i], i)
		}
	}
	if p := atomic.LoadInt64(&peak); p > workers {
		t.Errorf("peak concurrency %d exceeds workers=%d (over-spawning / weak cap)", p, workers)
	} else if p < 2 {
		t.Errorf("peak concurrency %d — fn was effectively serialised, no real parallelism", p)
	}
}

// TestNoGoroutineLeak must run last: it measures the live goroutine count
// before and after exercising the two leak-prone paths (workers >> inputs, and
// empty input). A correct implementation returns to its baseline.
func TestNoGoroutineLeak(t *testing.T) {
	settle(400 * time.Millisecond)
	before := runtime.NumGoroutine()

	_ = ParallelMap(seq(8), 256, func(x int) int { return x }) // 248 surplus workers must exit
	_ = ParallelMap([]int{}, 64, func(x int) int { return x }) // empty path must not park goroutines

	if after := waitGoroutines(before, 2*time.Second); after > before {
		t.Errorf("goroutine leak: %d goroutines before, %d after — surplus workers or the empty-input path were not cleaned up", before, after)
	}
}
