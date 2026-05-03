package pool

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}

	type job struct {
		idx int
		val T
	}
	jobs := make(chan job, len(inputs))
	out := make([]R, len(inputs))

	for w := 0; w < workers; w++ {
		go func() {
			for j := range jobs {
				out[j.idx] = fn(j.val)
			}
		}()
	}

	for i, v := range inputs {
		jobs <- job{i, v}
	}
	close(jobs)

	return out
}
