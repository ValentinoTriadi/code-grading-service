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
