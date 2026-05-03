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
