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
	jobs := make(chan job)
	results := make([]chan R, len(inputs))
	for i := range results {
		results[i] = make(chan R)
	}

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range jobs {
				results[j.idx] <- fn(j.val)
			}
		}()
	}

	out := make([]R, len(inputs))
	for i := range inputs {
		out[i] = <-results[i]
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)
	wg.Wait()
	return out
}
