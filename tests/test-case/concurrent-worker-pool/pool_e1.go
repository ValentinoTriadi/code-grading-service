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
