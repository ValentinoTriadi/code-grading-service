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
