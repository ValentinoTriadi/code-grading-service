package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	if workers > len(inputs) {
		workers = len(inputs)
	}

	out := make([]R, len(inputs))
	if len(inputs) == 0 {
		return out
	}

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				out[j.idx] = fn(j.val)
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
