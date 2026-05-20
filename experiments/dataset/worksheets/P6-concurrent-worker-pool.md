# P6 — Concurrent Worker Pool
_hard · go · 23 submissions_

## Description

Implement `func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R` that processes the inputs concurrently using `workers` goroutines while preserving input order — `out[i]` must be the result of applying `fn` to `inputs[i]`. Treat `workers <= 0` as `workers = 1`. When `workers > len(inputs)`, only `len(inputs)` goroutines should be spawned. The function must not deadlock, leak goroutines, or panic on empty input. `fn` is safe to call concurrently.

## Rubric

- **Correctness (35)** — Output preserves input order (`out[i]` corresponds to `inputs[i]`). Treats `workers <= 0` as `workers = 1`. Spawns at most `len(inputs)` goroutines. Does not panic on empty input. Compiles.
- **Concurrency Safety (35)** — No data races (`go test -race` clean). No goroutine leaks when `workers > len(inputs)` or on empty input. No deadlock on capacity-zero channels. Does not capture the loop variable by reference in goroutines. Synchronization is correct — every goroutine that is spawned is also waited for.
- **Efficiency (15)** — Actually parallelises — does not serialise behind a single mutex on the result slice when indexed writes are already race-free. Channel and slice capacities sized to avoid unnecessary blocking. Number of goroutines is bounded by `min(workers, len(inputs))`.
- **Code Quality (15)** — Idiomatic Go concurrency — channels and goroutines used cleanly, `sync.WaitGroup` for synchronization, no unnecessary external dependencies (e.g., pulling in `errgroup` when no errors are involved), no superfluous mutexes when indexed slice writes are race-free.

## Score sheet

| Submission | Correctness (35) | Concurrency Safety (35) | Efficiency (15) | Code Quality (15) | **Total** | Notes |
|---|---|---|---|---|---|---|
| pool_a1 |      |      |      |      |        |       |
| pool_a2 |      |      |      |      |        |       |
| pool_a3 |      |      |      |      |        |       |
| pool_b1 |      |      |      |      |        |       |
| pool_b2 |      |      |      |      |        |       |
| pool_b3 |      |      |      |      |        |       |
| pool_c1 |      |      |      |      |        |       |
| pool_c2 |      |      |      |      |        |       |
| pool_d1 |      |      |      |      |        |       |
| pool_e1 |      |      |      |      |        |       |
| pool_e2 |      |      |      |      |        |       |
| pool_e3 |      |      |      |      |        |       |
| pool_e4 |      |      |      |      |        |       |
| pool_e5 |      |      |      |      |        |       |
| pool_f1 |      |      |      |      |        |       |
| pool_f2 |      |      |      |      |        |       |
| pool_g1 |      |      |      |      |        |       |
| pool_g2 |      |      |      |      |        |       |
| pool_g3 |      |      |      |      |        |       |
| pool_h1 |      |      |      |      |        |       |
| pool_h2 |      |      |      |      |        |       |
| pool_i1 |      |      |      |      |        |       |
| pool_i2 |      |      |      |      |        |       |

## Submissions

### 1. `pool_a1`

```go
package pool

import "sync"

type job[T any] struct {
	idx int
	val T
}

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))
	jobs := make(chan job[T])

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				out[j.idx] = fn(j.val)
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job[T]{i, v}
	}
	// forgot to close(jobs)

	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 2. `pool_a2`

```go
package pool

import "sync"

type indexedJob[T any] struct {
	idx int
	val T
}

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))
	var mu sync.Mutex
	jobs := make(chan indexedJob[T], len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				r := fn(j.val)
				mu.Lock()
				out[j.idx] = r
				mu.Unlock()
			}
		}()
	}

	for i, v := range inputs {
		jobs <- indexedJob[T]{i, v}
	}
	close(jobs)
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 3. `pool_a3`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	if workers > len(inputs) {
		workers = len(inputs)
	}

	out := make([]R, len(inputs))
	if len(inputs) == 0 {
		return out
	}

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				out[j.idx] = fn(j.val)
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)

	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 4. `pool_b1`

```go
package pool

import "sync"

type ijob[T any] struct {
	idx int
	val T
}

type iresult[R any] struct {
	idx int
	val R
}

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	jobs := make(chan ijob[T], len(inputs))
	results := make(chan iresult[R], workers)

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				results <- iresult[R]{j.idx, fn(j.val)}
			}
		}()
	}

	for i, v := range inputs {
		jobs <- ijob[T]{i, v}
	}
	close(jobs)

	wg.Wait()

	out := make([]R, len(inputs))
	close(results)
	for r := range results {
		out[r.idx] = r.val
	}
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 5. `pool_b2`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	type job struct {
		idx int
		val T
	}
	type result struct {
		idx int
		val R
	}

	jobs := make(chan job, len(inputs))
	results := make(chan result, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				results <- result{j.idx, fn(j.val)}
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)

	out := make([]R, len(inputs))
	collectorDone := make(chan struct{})
	go func() {
		for r := range results {
			out[r.idx] = r.val
		}
		close(collectorDone)
	}()

	wg.Wait()
	close(results)
	<-collectorDone
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 6. `pool_b3`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	n := len(inputs)
	if workers <= 0 {
		workers = 1
	}
	if workers > n {
		workers = n
	}
	out := make([]R, n)
	if n == 0 {
		return out
	}

	type job struct {
		idx int
		val T
	}
	type result struct {
		idx int
		val R
	}
	jobs := make(chan job, n)
	results := make(chan result, n)

	var wg sync.WaitGroup
	wg.Add(workers)
	for w := 0; w < workers; w++ {
		go func() {
			defer wg.Done()
			for j := range jobs {
				results <- result{j.idx, fn(j.val)}
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)

	go func() {
		wg.Wait()
		close(results)
	}()

	for r := range results {
		out[r.idx] = r.val
	}
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 7. `pool_c1`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))
	sem := make(chan struct{}, workers)

	var wg sync.WaitGroup
	for i, v := range inputs {
		wg.Add(1)
		go func(idx int, val T) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()
			out[idx] = fn(val)
		}(i, v)
	}
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 8. `pool_c2`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	out := make([]R, len(inputs))
	tokens := make(chan struct{}, workers)

	var wg sync.WaitGroup
	for i, v := range inputs {
		tokens <- struct{}{}
		wg.Add(1)
		go func(idx int, val T) {
			defer wg.Done()
			defer func() { <-tokens }()
			out[idx] = fn(val)
		}(i, v)
	}
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 9. `pool_d1`

```go
package pool

import "golang.org/x/sync/errgroup"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))
	g := new(errgroup.Group)
	g.SetLimit(workers)

	for i, v := range inputs {
		i, v := i, v
		g.Go(func() error {
			out[i] = fn(v)
			return nil
		})
	}

	_ = g.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 10. `pool_e1`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))
	var wg sync.WaitGroup

	for i, v := range inputs {
		wg.Add(1)
		go func() {
			defer wg.Done()
			out[i] = fn(v)
		}()
	}

	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 11. `pool_e2`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))
	out := make([]R, 0, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				_ = j.idx
				out = append(out, fn(j.val))
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 12. `pool_e3`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	type job struct {
		idx int
		val T
	}
	type result struct {
		idx int
		val R
	}
	jobs := make(chan job, len(inputs))
	results := make(chan result, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			defer close(results)
			for j := range jobs {
				results <- result{j.idx, fn(j.val)}
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)

	out := make([]R, len(inputs))
	for r := range results {
		out[r.idx] = r.val
	}
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 13. `pool_e4`

```go
package pool

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))
	out := make([]R, len(inputs))

	for w := 0; w < workers; w++ {
		go func() {
			for j := range jobs {
				out[j.idx] = fn(j.val)
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)

	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 14. `pool_e5`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job)
	results := make([]chan R, len(inputs))
	for i := range results {
		results[i] = make(chan R)
	}

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				results[j.idx] <- fn(j.val)
			}
		}()
	}

	out := make([]R, len(inputs))
	for i := range inputs {
		out[i] = <-results[i]
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 15. `pool_f1`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	jobs := make(chan T, len(inputs))
	var mu sync.Mutex
	out := make([]R, 0, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for v := range jobs {
				r := fn(v)
				mu.Lock()
				out = append(out, r)
				mu.Unlock()
			}
		}()
	}

	for _, v := range inputs {
		jobs <- v
	}
	close(jobs)
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 16. `pool_f2`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))
	resultMap := make(map[int]R, len(inputs))
	var mu sync.Mutex

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				r := fn(j.val)
				mu.Lock()
				resultMap[j.idx] = r
				mu.Unlock()
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)
	wg.Wait()

	out := make([]R, 0, len(inputs))
	for _, r := range resultMap {
		out = append(out, r)
	}
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 17. `pool_g1`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	if workers > len(inputs) {
		workers = len(inputs)
	}

	chunk := len(inputs) / workers
	out := make([]R, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			start := idx * chunk
			end := start + chunk
			if idx == workers-1 {
				end = len(inputs)
			}
			for i := start; i < end; i++ {
				out[i] = fn(inputs[i])
			}
		}(w)
	}
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 18. `pool_g2`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	out := make([]R, len(inputs))

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job)

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				out[j.idx] = fn(j.val)
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 19. `pool_g3`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))
	out := make([]R, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				j, ok := <-jobs
				if !ok {
					return
				}
				out[j.idx] = fn(j.val)
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 20. `pool_h1`

```go
package pool

import "sync"

func ParallelMap[T, R](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				out[j.idx] = fn(j.val)
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 21. `pool_h2`

```go
package pool

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				out[j.idx] = fn(j.val)
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 22. `pool_i1`

```go
package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	n := len(inputs)
	if workers <= 0 {
		workers = 1
	}
	if workers > n {
		workers = n
	}
	out := make([]R, n)
	if n == 0 {
		return out
	}

	chunkSize := (n + workers - 1) / workers
	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		start := w * chunkSize
		if start >= n {
			break
		}
		end := start + chunkSize
		if end > n {
			end = n
		}
		wg.Add(1)
		go func(s, e int) {
			defer wg.Done()
			for i := s; i < e; i++ {
				out[i] = fn(inputs[i])
			}
		}(start, end)
	}
	wg.Wait()
	return out
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 23. `pool_i2`

```go
package pool

import "sync"

type stage1Job[T any] struct {
	idx int
	val T
}

type stage2Result[R any] struct {
	idx int
	val R
}

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	n := len(inputs)
	if workers <= 0 {
		workers = 1
	}
	if workers > n {
		workers = n
	}
	out := make([]R, n)
	if n == 0 {
		return out
	}

	jobs := generator(inputs)
	results := workerPool(jobs, workers, fn)
	collect(results, out)
	return out
}

func generator[T any](inputs []T) <-chan stage1Job[T] {
	ch := make(chan stage1Job[T])
	go func() {
		defer close(ch)
		for i, v := range inputs {
			ch <- stage1Job[T]{i, v}
		}
	}()
	return ch
}

func workerPool[T, R any](jobs <-chan stage1Job[T], workers int, fn func(T) R) <-chan stage2Result[R] {
	out := make(chan stage2Result[R])
	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				out <- stage2Result[R]{j.idx, fn(j.val)}
			}
		}()
	}
	go func() {
		wg.Wait()
		close(out)
	}()
	return out
}

func collect[R any](results <-chan stage2Result[R], out []R) {
	for r := range results {
		out[r.idx] = r.val
	}
}
```

> Correctness: ____/35  Concurrency Safety: ____/35  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:
