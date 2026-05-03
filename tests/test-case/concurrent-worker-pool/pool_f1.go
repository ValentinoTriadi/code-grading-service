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
