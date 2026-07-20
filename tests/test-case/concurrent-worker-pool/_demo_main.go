// Flow driver for the Concurrent Worker Pool case (P6).
//
// IMPORTANT: this file name starts with an underscore on purpose. The Go
// toolchain ignores files beginning with "_" or ".", so it can live next to
// the 23 pool_*.go submissions without being compiled. run_cases.py copies it
// (renamed to main.go) into a throwaway module whose pool/ sub-package holds
// one submission, then builds and runs the program to watch it execute.
//
// Your editor / gopls may flag the "p6demo/pool" import as unresolved while
// this file sits here alone — expected and harmless; run_cases.py supplies the
// package at run time.
//
// fn is the only thing a caller of ParallelMap can observe, so the driver
// instruments it: every call is logged with a timestamp and the live worker
// count. That exposes the real flow — fan-out up to `workers`, completion
// order, and whether the final output stays aligned to the input order.
package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"p6demo/pool"
)

var (
	logMu   sync.Mutex
	start   time.Time
	running int64
	peak    int64
)

// logf prints one timestamped flow line. Held under logMu so lines from
// concurrently-running fn calls do not interleave mid-line.
func logf(format string, args ...any) {
	logMu.Lock()
	defer logMu.Unlock()
	stamp := fmt.Sprintf("+%dms", time.Since(start).Milliseconds())
	fmt.Printf("  %-9s %s\n", stamp, fmt.Sprintf(format, args...))
}

func resetCounters() {
	atomic.StoreInt64(&running, 0)
	atomic.StoreInt64(&peak, 0)
	start = time.Now()
}

// makeFn returns an identity fn that logs every call. idxOf recovers the input
// index from a value (scenario inputs are distinct integers); jitter sets how
// long the call for a given index sleeps.
func makeFn(idxOf map[int]int, jitter func(idx int) time.Duration) func(int) int {
	return func(x int) int {
		idx := idxOf[x]
		n := atomic.AddInt64(&running, 1)
		for { // raise the running peak to n
			p := atomic.LoadInt64(&peak)
			if n <= p || atomic.CompareAndSwapInt64(&peak, p, n) {
				break
			}
		}
		logf("fn(input[%d]=%d) start         [running %d]", idx, x, n)
		time.Sleep(jitter(idx))
		left := atomic.AddInt64(&running, -1)
		logf("fn(input[%d]=%d) -> %-3d done   [running %d]", idx, x, x, left)
		return x
	}
}

func indexOf(inputs []int) map[int]int {
	m := make(map[int]int, len(inputs))
	for i, v := range inputs {
		m[v] = i
	}
	return m
}

// orderPreserved reports whether out lines up with inputs. fn is the identity,
// so a correct ParallelMap yields out[i] == inputs[i].
func orderPreserved(inputs, out []int) bool {
	if len(out) != len(inputs) {
		return false
	}
	for i := range inputs {
		if out[i] != inputs[i] {
			return false
		}
	}
	return true
}

func yesNo(b bool) string {
	if b {
		return "YES"
	}
	return "NO"
}

// runScenario runs ParallelMap once with a fully instrumented fn and prints the
// timeline plus a summary. Earlier inputs sleep longer, so completion order
// deliberately differs from input order — an implementation that fills the
// output in completion order shows up as "order preserved: NO".
func runScenario(label string, inputs []int, workers int) {
	fmt.Printf("\n%s — inputs %v, workers %d\n", label, inputs, workers)
	resetCounters()
	jitter := func(idx int) time.Duration {
		return time.Duration(len(inputs)-idx) * 12 * time.Millisecond
	}
	var out []int
	func() {
		defer func() {
			if r := recover(); r != nil {
				fmt.Printf("  PANIC: %v\n", r)
			}
		}()
		out = pool.ParallelMap(inputs, workers, makeFn(indexOf(inputs), jitter))
	}()
	elapsed := time.Since(start).Milliseconds()
	fmt.Printf("  output : %v\n", out)
	fmt.Printf("  order preserved: %s    peak concurrency: %d    elapsed: %dms\n",
		yesNo(orderPreserved(inputs, out)), atomic.LoadInt64(&peak), elapsed)
}

// probe runs one edge case compactly — a single result line, no timeline.
func probe(label string, inputs []int, workers int) {
	quiet := func(x int) int { return x }
	var out []int
	status := ""
	func() {
		defer func() {
			if r := recover(); r != nil {
				status = fmt.Sprintf("PANIC: %v", r)
			}
		}()
		out = pool.ParallelMap(inputs, workers, quiet)
	}()
	if status != "" {
		fmt.Printf("  %-28s %s\n", label, status)
		return
	}
	fmt.Printf("  %-28s -> %-22s order preserved: %s\n",
		label, fmt.Sprintf("%v", out), yesNo(orderPreserved(inputs, out)))
}

func main() {
	// Headline: a full timeline of one realistic run.
	runScenario("primary flow", []int{10, 20, 30, 40, 50, 60}, 3)

	// Edge cases, one compact line each. A hang here (e.g. workers <= 0
	// treated as zero workers) leaves the primary timeline above intact.
	fmt.Println("\nedge probes")
	probe("empty input", []int{}, 3)
	probe("workers <= 0 (treat as 1)", []int{10, 20, 30, 40}, 0)
	probe("workers > inputs", []int{10, 20, 30}, 8)
}
