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

	type job struct {
		idx int
		val T
	}
	type result struct {
		idx int
		val R
	}
	jobs := make(chan job, n)
	results := make(chan result, n)

	var wg sync.WaitGroup
	wg.Add(workers)
	for w := 0; w < workers; w++ {
		go func() {
			defer wg.Done()
			for j := range jobs {
				results <- result{j.idx, fn(j.val)}
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)

	go func() {
		wg.Wait()
		close(results)
	}()

	for r := range results {
		out[r.idx] = r.val
	}
	return out
}
