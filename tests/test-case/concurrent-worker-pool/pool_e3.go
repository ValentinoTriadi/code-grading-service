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
	type result struct {
		idx int
		val R
	}
	jobs := make(chan job, len(inputs))
	results := make(chan result, len(inputs))

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			defer close(results)
			for j := range jobs {
				results <- result{j.idx, fn(j.val)}
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)

	out := make([]R, len(inputs))
	for r := range results {
		out[r.idx] = r.val
	}
	wg.Wait()
	return out
}
