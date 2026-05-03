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
