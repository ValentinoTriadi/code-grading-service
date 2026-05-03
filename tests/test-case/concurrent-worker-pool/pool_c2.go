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
