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
