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
	out := make([]R, 0, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				_ = j.idx
				out = append(out, fn(j.val))
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)
	wg.Wait()
	return out
}
