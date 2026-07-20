package pool

import "sync"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	out := make([]R, len(inputs))

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job)

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
