## P6 — Concurrent Worker Pool (23 submissions)

**Rubric:** Correctness 35 · Concurrency Safety 35 · Efficiency 15 · Code Quality 15
**Summary:** flagged 11/23 · mean |Δ| 17.2 · your mean 78.7 · my mean 67.8

| ID | Correctness | Concurrency Safety | Efficiency | Code Quality | Total (you) | Total (me) | Δ | Flag | Suggestion |
|----|---|---|---|---|---|---|---|---|---|
| pool_a1 | 20→8 | 15→8 | 15→10 | 10→8 | 60 | 34 | +26 | 🚩 | Missing `close(jobs)`: workers range forever, `wg.Wait()` never returns — hard deadlock. Score Correctness and Concurrency Safety in the single digits. |
| pool_a2 | 35 | 35 | 5→11 | 10→11 | 85 | 92 | -7 | | — |
| pool_a3 | 35 | 35 | 15 | 15 | 100 | 100 | 0 | | — |
| pool_b1 | 20→10 | 20→10 | 10→8 | 10→9 | 60 | 37 | +23 | 🚩 | `results` buffered only to `workers`; workers block on a full channel while `wg.Wait()` runs before any drain — deadlock once `len(inputs) > workers`. |
| pool_b2 | 35 | 35 | 5→15 | 10→12 | 85 | 97 | -12 | 🚩 | Code is fully correct and parallel; the collector goroutine drains concurrently so there is no serialization. Efficiency 5 is unjustified — raise to ~15. |
| pool_b3 | 35 | 35 | 15 | 15 | 100 | 100 | 0 | | — |
| pool_c1 | 30→35 | 35 | 10→12 | 15 | 90 | 97 | -7 | | — |
| pool_c2 | 35 | 35 | 15 | 15 | 100 | 100 | 0 | | — |
| pool_d1 | 35 | 35 | 15 | 5→9 | 90 | 94 | -4 | | — |
| pool_e1 | 15→35 | 15→35 | 15→5 | 15→12 | 60 | 87 | -27 | 🚩 | Under Go 1.22+ the per-iteration loop var makes this race-free and order-correct; it is not a capture bug on a modern toolchain. Real flaw is ignoring `workers` (spawns one goroutine per input) — penalize Efficiency, not Correctness/Safety. |
| pool_e2 | 15→8 | 15→6 | 15→10 | 15→8 | 60 | 32 | +28 | 🚩 | `append` to a shared slice from many goroutines is a genuine data race and also breaks input order — both Correctness and Concurrency Safety should be near-zero. |
| pool_e3 | 15→8 | 15→6 | 15→10 | 15→8 | 60 | 32 | +28 | 🚩 | `defer close(results)` in every worker → panic on send-to-closed / double-close. This is a runtime panic, not a 60-tier submission. |
| pool_e4 | 15→8 | 15→6 | 15→10 | 15→8 | 60 | 32 | +28 | 🚩 | No `WaitGroup`/`Wait`: `out` is returned before workers write it — caller sees zero values and there is a write/return race plus a goroutine leak. |
| pool_e5 | 15→6 | 15→6 | 15→10 | 15→8 | 60 | 30 | +30 | 🚩 | Main drains `results[i]` in order before any job is sent over the unbuffered `jobs` channel — immediate deadlock. Score it as a deadlocking submission. |
| pool_f1 | 20 | 25→33 | 15→13 | 10 | 70 | 76 | -6 | | — |
| pool_f2 | 20 | 25→33 | 15→13 | 10 | 70 | 76 | -6 | | — |
| pool_g1 | 25→22 | 35 | 15 | 10→12 | 85 | 84 | +1 | | — |
| pool_g2 | 25→22 | 35→25 | 15 | 10→12 | 85 | 74 | +11 | 🚩 | No `workers <= 0` guard; with `workers <= 0` zero workers spawn and the unbuffered `jobs` send deadlocks. Concurrency Safety 35 ignores a documented deadlock path. |
| pool_g3 | 30→8 | 25→8 | 15→10 | 10→8 | 70 | 34 | +36 | 🚩 | `jobs` is never closed, so workers' `for{ ok }` loop blocks forever and `wg.Wait()` deadlocks on every input — not an 80-tier submission. |
| pool_h1 | 30 | 35 | 15 | 5 | 85 | 80 | +5 |  | Localized compile error (`[T, R]` without `any` constraint) — algorithm intent is fully readable; under the new rubric the defect is capped at −5 via Code Quality, not a Correctness zero. (Human CQ 5 already absorbs the cap.) |
| pool_h2 | 30 | 35 | 15 | 10→5 | 90 | 85 | +5 |  | Localized compile error (missing `import "sync"`) — algorithm intent is fully readable; capped at −5 via Code Quality under the new rubric. |
| pool_i1 | 35 | 35 | 15 | 15 | 100 | 100 | 0 | | — |
| pool_i2 | 35 | 35 | 15 | 10→13 | 95 | 98 | -3 | | — |

### Flagged in P6
- **pool_a1** (you 60 / me 34, Δ +26): Human missed that `close(jobs)` is absent — every worker ranges forever and `wg.Wait()` deadlocks. This is a non-terminating submission; corrected total ≈ 34, with Correctness and Concurrency Safety in single digits.
- **pool_b1** (you 60 / me 37, Δ +23): The `results` channel is buffered to `workers`, not `len(inputs)`, and `wg.Wait()` runs before any drain — workers deadlock on a full channel once `len(inputs) > workers`. Corrected total ≈ 37.
- **pool_b2** (you 85 / me 97, Δ -12): The implementation is fully correct, leak-free, and genuinely parallel; the concurrent collector goroutine means there is no serialization. The human's Efficiency 5 is the inconsistency — corrected total ≈ 97.
- **pool_e1** (you 60 / me 87, Δ -27): On a Go 1.22+ toolchain the per-iteration loop variable makes this race-free and order-preserving, so the harsh 15/15 on Correctness/Concurrency Safety is unwarranted. The real defect is ignoring `workers` entirely — penalize Efficiency. Corrected total ≈ 87 (note the 1.22 dependency).
- **pool_e2** (you 60 / me 32, Δ +28): `append` into a shared `[]R` from many goroutines is a real data race and also produces completion-order output. Both Correctness and Concurrency Safety should be near-zero; corrected total ≈ 32.
- **pool_e3** (you 60 / me 32, Δ +28): `defer close(results)` in each worker causes a panic (send on closed channel / double close). A panicking submission cannot sit at the 60 tier; corrected total ≈ 32.
- **pool_e4** (you 60 / me 32, Δ +28): With no `WaitGroup`, `out` is returned before workers populate it — zero-value output plus a write/return race and goroutine leak. Corrected total ≈ 32.
- **pool_e5** (you 60 / me 30, Δ +30): Main blocks on `<-results[0]` before sending any job over the unbuffered `jobs` channel — immediate deadlock. Corrected total ≈ 30.
- **pool_g2** (you 85 / me 74, Δ +11): No `workers <= 0` guard; that input path spawns zero workers and deadlocks on the unbuffered `jobs` send. Concurrency Safety 35 ignores a documented deadlock; corrected total ≈ 74.
- **pool_g3** (you 80 / me 34, Δ +46): `jobs` is never closed, so the workers' `for{ <-jobs, ok }` loop never sees `ok == false` and `wg.Wait()` deadlocks on every call — not just the `workers > len` case. Corrected total ≈ 34.
- *(Re-graded under softened rubric: `pool_h1`, `h2` were flagged in the first pass for compile errors. The new rubric grades demonstrated algorithmic intent, capping a localized compile defect at −5 via Code Quality rather than zeroing Correctness. Both submissions have a fully-readable concurrent worker pool around the localized defect, so the walk-back lands within 5 of the human score and the flags drop.)*
