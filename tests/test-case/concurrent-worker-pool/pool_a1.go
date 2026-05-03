package pool

import "sync"

type job[T any] struct {
	idx int
	val T
}

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))
	jobs := make(chan job[T])

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
		jobs <- job[T]{i, v}
	}
	// forgot to close(jobs)

	wg.Wait()
	return out
}
