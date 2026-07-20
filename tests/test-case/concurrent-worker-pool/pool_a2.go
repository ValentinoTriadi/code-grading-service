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
