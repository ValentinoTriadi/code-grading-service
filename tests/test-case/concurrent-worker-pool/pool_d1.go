package pool

import "golang.org/x/sync/errgroup"

func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R {
	if workers <= 0 {
		workers = 1
	}
	out := make([]R, len(inputs))
	g := new(errgroup.Group)
	g.SetLimit(workers)

	for i, v := range inputs {
		i, v := i, v
		g.Go(func() error {
			out[i] = fn(v)
			return nil
		})
	}

	_ = g.Wait()
	return out
}
