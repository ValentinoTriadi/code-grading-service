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
