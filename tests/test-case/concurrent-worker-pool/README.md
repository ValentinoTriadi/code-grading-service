# Concurrent Worker Pool — Test Cases

**Language:** Go
**Difficulty:** Hard

## Problem

Implement a generic concurrent worker pool that processes a slice of inputs in parallel using `workers` goroutines.

```go
package pool

// ParallelMap processes inputs concurrently using `workers` goroutines.
// The output slice MUST preserve the order of the input slice — that is,
// out[i] is the result of applying fn to inputs[i].
//
// Constraints:
//   - if workers <= 0, treat as workers = 1.
//   - fn may be slow, but is safe to call concurrently.
//   - the function must not deadlock, leak goroutines, or panic on empty input.
//   - if workers > len(inputs), only len(inputs) goroutines should be spawned.
func ParallelMap[T, R any](inputs []T, workers int, fn func(T) R) []R
```

This problem exercises:

- Goroutines, channels, and `sync.WaitGroup`
- **Order-preserving** parallel results (the classic gotcha)
- Goroutine lifecycle: no leaks, no deadlock on empty input
- Idiomatic Go concurrency patterns

Each group represents a different implementation approach.

- **1** = poor (works on the happy path but leaks goroutines, races, or has style issues)
- **2** = acceptable (correct, but not idiomatic Go)
- **3** = good (clean, idiomatic, no leaks)

---

## Group A — Indexed jobs over channels

A `jobs` channel of `(idx, value)` and a results slice indexed by position. Most idiomatic.

| File | Quality | Notes |
|------|---------|-------|
| `pool_a1.go` | Poor | Forgets to `close(jobs)` — receivers block forever (deadlock) |
| `pool_a2.go` | Acceptable | Correct, but uses `sync.Mutex` to write results (unnecessary — indexed slice writes are race-free) |
| `pool_a3.go` | Good | Idiomatic: indexed jobs, `WaitGroup`, no mutex on `out[idx]` |

## Group B — Two channels (jobs and results)

`jobs` channel for inputs, `results` channel for `(idx, result)` pairs. Receiver goroutine fills the slice in any order.

| File | Quality | Notes |
|------|---------|-------|
| `pool_b1.go` | Poor | Doesn't size `results` channel correctly — blocks workers when full |
| `pool_b2.go` | Acceptable | Correct, but spawns one extra "collector" goroutine that complicates flow |
| `pool_b3.go` | Good | Buffered results channel, clean fan-out / fan-in, ordered fill |

## Group C — `sync.WaitGroup` only, no channels

Spawns one goroutine per input, capped at `workers` via a semaphore channel.

| File | Quality | Notes |
|------|---------|-------|
| `pool_c1.go` | Acceptable | Correct, but spawns `len(inputs)` goroutines even when many are blocked on the semaphore |
| `pool_c2.go` | Good | Semaphore pattern with `chan struct{}` — clean and idiomatic |

## Group D — `errgroup` style (creative, no errors needed)

Uses `golang.org/x/sync/errgroup` even though the function doesn't return errors.

| File | Quality | Notes |
|------|---------|-------|
| `pool_d1.go` | Acceptable | Works, but pulls in an external dependency for nothing |

## Group E — Concurrency bugs (compiles, races / deadlocks / wrong order)

| File | Bug |
|------|-----|
| `pool_e1.go` | Captures loop variable by reference — every worker processes the LAST input |
| `pool_e2.go` | Writes to a shared `[]R` via `append` from many goroutines — data race |
| `pool_e3.go` | Closes `results` channel inside a worker — second worker panics on send to closed channel |
| `pool_e4.go` | Returns `out` immediately after launching workers (no `Wait`) — caller sees zero values |
| `pool_e5.go` | Drains results in input order using a single goroutine BEFORE workers finish — deadlock |

## Group F — Order-preservation bugs

| File | Bug |
|------|-----|
| `pool_f1.go` | Uses `append(out, ...)` from each worker — output order matches completion order, not input order |
| `pool_f2.go` | Records results into a `map[int]R` but iterates the map (non-deterministic order) into the slice |

## Group G — Edge-case bugs

| File | Bug |
|------|-----|
| `pool_g1.go` | Crashes on empty `inputs` — `len(inputs) == 0` triggers division-by-zero / negative slice index |
| `pool_g2.go` | Treats `workers <= 0` as "spawn zero workers" — function hangs forever |
| `pool_g3.go` | When `workers > len(inputs)`, spawns `workers` goroutines that immediately block on an empty channel and never exit (leak) |

## Group H — Compile errors

| File | Bug |
|------|-----|
| `pool_h1.go` | Generic type parameter `[T, R any]` used as `[T,R]` (missing `any`) on receiver func |
| `pool_h2.go` | Missing `import "sync"` |

## Group I — Creative correct alternatives

| File | Quality | Notes |
|------|---------|-------|
| `pool_i1.go` | Good | Static partitioning — splits the input into `workers` contiguous chunks; one goroutine per chunk |
| `pool_i2.go` | Good | Pipeline style — `generator` → `worker pool` → `ordered collector` using three stages |
