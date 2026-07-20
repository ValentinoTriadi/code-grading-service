# Grade Review — Human vs. Independent LLM Re-grade

_Generated 2026-05-17 · 144 submissions across 6 problems._

Every submission was re-graded independently against the same per-problem rubric, then compared to the human grader's scores. The rubric was softened mid-review to grade **demonstrated algorithmic intent over executability** — a localized syntax / parse / compile error in otherwise readable code is now a bounded Code Quality deduction (capped at −5/100), not a Correctness zero. A row is **flagged 🚩** when the totals differ by ≥ 10 points, the human's per-criterion breakdown is internally inconsistent, or a documented semantic defect (wrong algorithm, crash, data race, deadlock, mis-eviction, logic bug) is not reflected in the score.

In every per-problem table, a criterion cell reads `you→me` (your sub-score, then mine); a single number means we agreed. `Δ` = your total − my total (a **positive Δ means you scored higher than I would**).

## Executive summary

| Problem | N | Flagged | Your mean | My mean | Mean Δ (you−me) | Mean \|Δ\| |
|---|---|---|---|---|---|---|
| P1 Sum Array | 28 | 7 | 83.7 | 78.5 | +5.2 | 9.7 |
| P2 Palindrome Check | 20 | 6 | 91.2 | 84.2 | +7.0 | 8.3 |
| P3 LRU Cache | 25 | 7 | 88.0 | 86.5 | +1.4 | 7.4 |
| P4 Dijkstra Shortest Path | 25 | 9 | 88.0 | 83.3 | +4.7 | 6.6 |
| P5 Binary Search Tree | 23 | 6 | 90.9 | 89.6 | +1.3 | 5.5 |
| P6 Concurrent Worker Pool | 23 | 10 | 79.1 | 72.7 | +6.5 | 12.7 |
| **All** | **144** | **45** | **86.6** | **82.4** | **+4.3** | **8.4** |

**45 of 144 submissions are flagged.** Under the softened rubric, the dominant pattern is over-scoring of code with **real semantic defects** — wrong algorithm, crashes, deadlocks, data races, mis-eviction, off-by-one logic bugs — where the human kept near-full Correctness. A secondary pattern is **under-scoring clean correct alternatives** (hash+DLL caches in P3, the augmented BST in P5, a modern-Go solution in P6, the cleanest `reduce` solutions in P1). Localized syntax / compile failures are no longer themselves a flag source — they are bounded at −5 via Code Quality and the affected rows now sit within tolerance of the human score.

### Where to look first

- **P6** has the highest mean \|Δ\| (12.7) — concurrency bugs (deadlocks, races, panics, goroutine leaks) were repeatedly given 60-tier scores.
- **P4** flags concentrate on **wrong-algorithm** submissions (BFS / Bellman-Ford / DFS scored as Dijkstra) and Dijkstra-shaped implementations with real correctness bugs (`dist[source] = LLONG_MAX`, missing re-push, mark-before-pop).
- **P3** flags split both directions: documented eviction / infinite-loop defects over-scored, and clean hash+DLL caches under-scored.
- **P5** is the most consistent (mean \|Δ\| 5.5); only 6 rows need a look.

## Top 20 discrepancies

| Problem | Submission | Total (you) | Total (me) | Δ | Issue |
|---|---|---|---|---|---|
| P1 | `sum_array_d1` | 60 | 10 | +50 | The function is named `sum` and calls `sum(arr)`, so it recurses into itself infinitely → RecursionError. |
| P1 | `sum_array_h2` | 88 | 43 | +45 | `arr[i + 1]` with `i` ranging over `len(arr)` indexes one past the end on the last iteration → IndexError; ... |
| P1 | `sum_array_h3` | 88 | 43 | +45 | `range(1, len(arr) + 1)` indexes past the end on the final iteration → IndexError, and also skips index 0. |
| P6 | `pool_g3` | 70 | 34 | +36 | `jobs` is never closed, so the workers' `for{ <-jobs, ok }` loop never sees `ok == false` and `wg.Wait()` d... |
| P1 | `sum_array_h1` | 88 | 56 | +32 | `range(len(arr) - 1)` silently drops the last element — every non-empty array returns the wrong sum. |
| P3 | `lru_g1` | 90 | 59 | +31 | The eviction loop body calls `this.store.has(oldest)` and never deletes, so any `put` that overflows capaci... |
| P6 | `pool_e5` | 60 | 30 | +30 | Main blocks on `<-results[0]` before sending any job over the unbuffered `jobs` channel — immediate deadlock. |
| P6 | `pool_e2` | 60 | 32 | +28 | `append` into a shared `[]R` from many goroutines is a real data race and also produces completion-order ou... |
| P6 | `pool_e3` | 60 | 32 | +28 | `defer close(results)` in each worker causes a panic (send on closed channel / double close). |
| P6 | `pool_e4` | 60 | 32 | +28 | With no `WaitGroup`, `out` is returned before workers populate it — zero-value output plus a write/return r... |
| P2 | `PalindromeF1` | 70 | 43 | +27 | `cleaned.charAt(i) != cleaned.charAt(i)` compares each index to itself — the condition is never true, so th... |
| P3 | `lru_a3` | 70 | 97 | -27 | Human gave Correctness 20 and Efficiency 15 to a clean, idiomatic, O(1) generic Map LRU that is fully corre... |
| P6 | `pool_e1` | 60 | 87 | -27 | On a Go 1.22+ toolchain the per-iteration loop variable makes this race-free and order-preserving, so the h... |
| P2 | `PalindromeF3` | 95 | 69 | +26 | `while (i < j - 1)` is an off-by-one that exits before comparing the last remaining pair on even-length str... |
| P6 | `pool_a1` | 60 | 34 | +26 | Human missed that `close(jobs)` is absent — every worker ranges forever and `wg.Wait()` deadlocks. |
| P4 | `dijkstra_f4` | 85 | 60 | +25 | `dist[source]` is initialized to `LLONG_MAX`, so the popped entry is immediately stale and no relaxation ev... |
| P2 | `PalindromeB1` | 75 | 51 | +24 | `reversed` is built by char concatenation and is never reference-equal to `cleaned`, so it returns `false` ... |
| P2 | `PalindromeC1` | 90 | 67 | +23 | Human gave Correctness 50/60, but the code never strips non-alphanumerics and reverses the full lowercased ... |
| P3 | `lru_f3` | 85 | 62 | +23 | Human's Correctness 35 ignores the documented mis-eviction — `pop()` evicts the most-recently-used entry in... |
| P6 | `pool_b1` | 60 | 37 | +23 | The `results` channel is buffered to `workers`, not `len(inputs)`, and `wg.Wait()` runs before any drain — ... |

---

## P1 — Sum Array (28 submissions)

**Rubric:** Correctness 60 · Code Quality 25 · Efficiency 15
**Summary:** flagged 7/28 · mean \|Δ\| 9.7 · your mean 83.7 · my mean 78.5

| ID | Correctness | Code Quality | Efficiency | Total (you) | Total (me) | Δ | Flag | Suggestion |
|----|---|---|---|---|---|---|---|---|
| sum_array_a1 | 60 | 15→13 | 15 | 90 | 88 | +2 |  | — |
| sum_array_a2 | 60 | 20→18 | 15 | 95 | 93 | +2 |  | — |
| sum_array_a3 | 60 | 25 | 15 | 100 | 100 | 0 |  | — |
| sum_array_b1 | 60 | 13 | 15 | 88 | 88 | 0 |  | — |
| sum_array_b2 | 60 | 18 | 15 | 93 | 93 | 0 |  | — |
| sum_array_b3 | 60 | 23 | 15 | 98 | 98 | 0 |  | — |
| sum_array_c1 | 60 | 20→13 | 15 | 95 | 88 | +7 |  | — |
| sum_array_c2 | 60 | 23→18 | 15 | 98 | 93 | +5 |  | — |
| sum_array_c3 | 60 | 25 | 15 | 100 | 100 | 0 |  | — |
| sum_array_c4 | 60 | 24→18 | 15 | 99 | 93 | +6 |  | — |
| sum_array_d1 | 40→3 | 15→4 | 10→3 | 60 | 10 | +50 | 🚩 | Correctness must be near 0 — `sum` shadows built-in causing infinite recursion / RecursionError; nothing returns. |
| sum_array_d2 | 60 | 20→23 | 15 | 95 | 98 | −3 |  | — |
| sum_array_d3 | 60 | 25 | 15 | 100 | 100 | 0 |  | — |
| sum_array_e1 | 60→48 | 10 | 15 | 85 | 73 | +12 | 🚩 | Correctness should drop — `reduce` without initializer raises TypeError on empty array. |
| sum_array_e2 | 60→48 | 12→21 | 15 | 87 | 84 | +3 |  | — |
| sum_array_e3 | 60 | 12→25 | 15 | 87 | 100 | −13 | 🚩 | Code Quality is the cleanest in the group (operator.add, explicit init 0) yet scored lowest — raise it. |
| sum_array_f1 | 60 | 10→13 | 10 | 80 | 83 | −3 |  | — |
| sum_array_f2 | 60 | 15→23 | 10 | 85 | 93 | −8 |  | — |
| sum_array_f3 | 60 | 15→25 | 10 | 85 | 95 | −10 | 🚩 | Code Quality undervalued — clean `not arr` idiom + type hints; this is the group's best. |
| sum_array_g1 | 10 | 10→12 | 10→15 | 30 | 37 | −7 |  | — |
| sum_array_g2 | 10 | 10→12 | 10→15 | 30 | 37 | −7 |  | — |
| sum_array_g3 | 10 | 10→12 | 10 | 30 | 32 | −2 |  | — |
| sum_array_h1 | 55→18 | 23 | 15 | 88 | 56 | +32 | 🚩 | Correctness wildly overscored — off-by-one drops the last element, wrong answer on every non-empty array. |
| sum_array_h2 | 55→5 | 23 | 15 | 88 | 43 | +45 | 🚩 | Correctness must be near 0 — `arr[i+1]` raises IndexError on the final iteration; the function crashes. |
| sum_array_h3 | 55→5 | 23 | 15 | 88 | 43 | +45 | 🚩 | Correctness must be near 0 — `range(1, len(arr)+1)` raises IndexError; skips index 0 and crashes. |
| sum_array_i1 | 60 | 25→20 | 15 | 90 | 95 | -5 |  | Localized SyntaxError (missing `:` after def) — algorithm intent (for-loop accumulator) is fully readable; under the new rubric the syntax defect is capped at −5 via Code Quality, not a Correctness zero. |
| sum_array_i2 | 60 | 20→15 | 15 | 90 | 90 | 0 |  | Localized SyntaxError (unindented body) — algorithm intent is fully readable; capped at −5 via Code Quality under the new rubric. |
| sum_array_i3 | 60 | 25→20 | 15 | 90 | 95 | -5 |  | Localized SyntaxError (missing `:` after `for`) — algorithm intent is fully readable; capped at −5 via Code Quality under the new rubric. |

### Flagged in P1
- **sum_array_d1** (you 65 / me 10, Δ +55): The function is named `sum` and calls `sum(arr)`, so it recurses into itself infinitely → RecursionError. The README explicitly marks it "Broken". Human gave Correctness 40/60; it should be ~3 (a tiny partial for plausible-looking intent). Recommended corrected total ≈ 10.
- **sum_array_e1** (you 85 / me 73, Δ +12): `reduce(lambda a,b: a+b, arr)` has no initializer, so an empty array raises `TypeError: reduce() of empty iterable with no initial value`. This is an edge-case correctness bug the human did not deduct for. Correctness should be ~48. Recommended corrected total ≈ 73.
- **sum_array_e3** (you 87 / me 100, Δ −13): This is the cleanest reduce implementation — `operator.add` instead of a lambda, explicit initial value `0` (so it also handles empty arrays correctly). The README rates it "Good", yet the human gave Code Quality 12/25, the lowest in the group. Code Quality should be ~25. Recommended corrected total = 100.
- **sum_array_f3** (you 85 / me 95, Δ −10): Clean recursion using the `not arr` idiom plus full type hints — README rates it "Good". Human gave Code Quality 15/25; it should be 25 (the O(n²) slicing cost is captured under Efficiency, which is already 10/15). Recommended corrected total ≈ 95.
- **sum_array_h1** (you 93 / me 56, Δ +37): `range(len(arr) - 1)` silently drops the last element — every non-empty array returns the wrong sum. Human kept Correctness at 55/60, treating a wrong-answer bug as a minor deduction. Correctness should be ~18. Recommended corrected total ≈ 56.
- **sum_array_h2** (you 93 / me 43, Δ +50): `arr[i + 1]` with `i` ranging over `len(arr)` indexes one past the end on the last iteration → IndexError; the function crashes and never returns. Human kept Correctness at 55/60. Correctness should be near 0 (~5). Recommended corrected total ≈ 43.
- **sum_array_h3** (you 93 / me 43, Δ +50): `range(1, len(arr) + 1)` indexes past the end on the final iteration → IndexError, and also skips index 0. The code crashes. Human's Correctness 55/60 ignores the documented crash. Correctness should be near 0 (~5). Recommended corrected total ≈ 43.
- *(Note: c1/c2/c4 are within tolerance and not flagged, but the human applied the `sum`-shadowing penalty inconsistently across groups — Group A/B docked it harder than Group C for the same defect.)*
- *(Re-graded under softened rubric: `sum_array_i1`, `i2`, `i3` were flagged in the first pass for SyntaxError. The new rubric grades demonstrated algorithmic intent, capping a localized syntax / parse defect at −5 via Code Quality rather than zeroing Correctness. All three submissions have a fully-readable accumulator loop, so the walk-back lands within 5 of the human score and the flags drop.)*

---

## P2 — Palindrome Check (20 submissions)

**Rubric:** Correctness 60 · Code Quality 25 · Efficiency 15
**Summary:** flagged 6/20 · mean \|Δ\| 8.3 · your mean 91.2 · my mean 84.2

| ID | Correctness | Code Quality | Efficiency | Total (you) | Total (me) | Δ | Flag | Suggestion |
|----|---|---|---|---|---|---|---|---|
| PalindromeA1 | 60→35 | 20→22 | 10→15 | 90 | 72 | +18 | 🚩 | Code never lower-cases before comparing chars; fails the canonical mixed-case test. Drop Correctness to ~35. |
| PalindromeA2 | 60 | 25→23 | 10→13 | 95 | 96 | -1 | | — |
| PalindromeA3 | 60 | 25 | 15 | 100 | 100 | 0 | | — |
| PalindromeB1 | 40→30 | 20→14 | 15→7 | 75 | 51 | +24 | 🚩 | `==` on non-interned strings returns false almost always; O(n²) concat. Correctness ~30, Quality/Efficiency lower. |
| PalindromeB2 | 60 | 25→22 | 15→9 | 100 | 91 | +9 | | — |
| PalindromeB3 | 60 | 25 | 15 | 100 | 100 | 0 | | — |
| PalindromeC1 | 50→30 | 25→22 | 15 | 90 | 67 | +23 | 🚩 | Never strips non-alphanumerics; fails punctuation inputs. Correctness must reflect a real wrong-answer defect. |
| PalindromeC2 | 60 | 25 | 15 | 100 | 100 | 0 | | — |
| PalindromeC3 | 58→60 | 25→24 | 15 | 98 | 99 | -1 | | — |
| PalindromeD1 | 60 | 20→22 | 10→7 | 90 | 89 | +1 | | — |
| PalindromeD2 | 60 | 15→22 | 10 | 85 | 92 | -7 | | — |
| PalindromeD3 | 60 | 20→24 | 10→11 | 90 | 95 | -5 | | — |
| PalindromeE1 | 60 | 25 | 15 | 100 | 100 | 0 | | — |
| PalindromeE2 | 60 | 25 | 15 | 100 | 100 | 0 | | — |
| PalindromeF1 | 40→10 | 25→18 | 15 | 70 | 43 | +27 | 🚩 | `charAt(i) != charAt(i)` compares an index to itself — always-true logic, never fails. Correctness near 0. |
| PalindromeF2 | 40→20 | 20 | 15 | 75 | 55 | +20 | 🚩 | No normalization at all; fails case, punctuation, `"Aa"`. Correctness ~20. |
| PalindromeF3 | 55→30 | 25→24 | 15 | 95 | 69 | +26 | 🚩 | `while (i < j-1)` off-by-one skips the final pair on even-length strings. Real wrong-answer bug. |
| PalindromeG1 | 55 | 25→20 | 15 | 90 | 90 | 0 |  | Localized compile error (missing semicolon) — algorithm intent is fully readable; under the new rubric the defect is capped at −5 via Code Quality, not a Correctness zero. |
| PalindromeG2 | 50 | 25→20 | 15 | 90 | 85 | +5 |  | Localized compile error (`void` return type returning `boolean`) — algorithm intent is fully readable; capped at −5 via Code Quality under the new rubric. |
| PalindromeG3 | 60 | 20→15 | 15 | 90 | 90 | 0 |  | Localized compile error (extra `}` at end of file) — algorithm intent is fully readable; capped at −5 via Code Quality under the new rubric. |

### Flagged in P2
- **PalindromeA1** (you 90 / me 72, Δ +18): Human gave full Correctness 60/60, but the loop compares raw chars (`a != b`) without lower-casing, so it fails the canonical `"A man, a plan, a canal: Panama"`. Case-insensitivity is a core requirement — Correctness should be ~35, corrected total ~72.
- **PalindromeB1** (you 75 / me 51, Δ +24): README-documented `==` bug. `reversed` is built by char concatenation and is never reference-equal to `cleaned`, so it returns `false` for essentially every real palindrome. Correctness ~30, plus quality penalty for the `==` bug and efficiency penalty for O(n²) concat; corrected total ~51.
- **PalindromeC1** (you 90 / me 67, Δ +23): Human gave Correctness 50/60, but the code never strips non-alphanumerics and reverses the full lowercased string, so any input with punctuation/spaces fails. That is a wrong-answer defect, not a 10-point deduction; corrected total ~67.
- **PalindromeF1** (you 80 / me 43, Δ +37): `cleaned.charAt(i) != cleaned.charAt(i)` compares each index to itself — the condition is never true, so the method always returns `true`. Silent always-true logic; Correctness near 0 (~10), corrected total ~43.
- **PalindromeF2** (you 75 / me 55, Δ +20): No normalization performed at all — fails case, punctuation, and `"Aa"`. Correctness ~20, corrected total ~55.
- **PalindromeF3** (you 95 / me 69, Δ +26): `while (i < j - 1)` is an off-by-one that exits before comparing the last remaining pair on even-length strings, producing false positives. README-documented bug not reflected in Correctness 55/60; corrected total ~69.
- *(Re-graded under softened rubric: `PalindromeG1`, `G2`, `G3` were flagged in the first pass for compile errors. The new rubric grades demonstrated algorithmic intent, capping a localized compile defect at −5 via Code Quality rather than zeroing Correctness. All three submissions have a fully-readable palindrome implementation around the localized defect, so the walk-back lands within 5 of the human score and the flags drop.)*

---

## P3 — LRU Cache (25 submissions)

**Rubric:** Correctness 40 · Data Structures 25 · Efficiency 20 · Code Quality 15
**Summary:** flagged 7/25 · mean \|Δ\| 7.4 · your mean 88.0 · my mean 86.5

| ID | Correctness | Data Structures | Efficiency | Code Quality | Total (you) | Total (me) | Δ | Flag | Suggestion |
|----|---|---|---|---|---|---|---|---|---|
| lru_a1 | 30→33 | 25 | 20 | 5→6 | 80 | 84 | -4 |  | — |
| lru_a2 | 40 | 25 | 20 | 10→13 | 95 | 98 | -3 |  | — |
| lru_a3 | 20→38 | 25 | 15→20 | 10→14 | 70 | 97 | -27 | 🚩 | Restore Correctness/Efficiency: this is a clean, correct O(1) Map LRU; throwing on capacity≤0 is defensive, not a defect. Corrected total ~97. |
| lru_b1 | 40→34 | 15→18 | 15→20 | 10→7 | 80 | 79 | +1 | 🚩 | DLL is genuinely O(1) — Efficiency should be 20, not 15. Also dock Correctness for plain-object index coercing numeric keys. |
| lru_b2 | 40 | 15→25 | 15→20 | 10→13 | 80 | 98 | -18 | 🚩 | Correct generic hash+DLL with sentinels — DS and Efficiency should be full (25/20), not 15/15. Corrected total ~98. |
| lru_b3 | 20→36 | 15→25 | 15→20 | 10→15 | 100 | 96 | +4 |  | Clean correct hash+DLL; DS/Eff/CQ all severely under-graded. Only real flaw is a capacity=0 edge (evicts sentinel). Corrected total ~96. |
| lru_c1 | 40→34 | 20→14 | 10→8 | 10→8 | 80 | 64 | +16 | 🚩 | Object-as-dict coerces keys via String() (numeric-key collisions) — dock Correctness; object-as-ordered-map abuse — dock DS. Corrected total ~64. |
| lru_c2 | 35→40 | 15→20 | 10 | 15 | 75 | 85 | -10 | 🚩 | Semantics are fully correct — Correctness should be 40; DS 15 is harsh for two clean parallel Maps. Corrected total ~85. |
| lru_d1 | 40 | 10→12 | 10→8 | 10→8 | 70 | 68 | +2 |  | — |
| lru_d2 | 40 | 20→18 | 10 | 15→14 | 85 | 82 | +3 |  | — |
| lru_e1 | 30→32 | 25 | 20 | 15→14 | 90 | 91 | -1 |  | — |
| lru_e2 | 40→39 | 25 | 20 | 10→14 | 95 | 98 | -3 |  | — |
| lru_f1 | 30 | 25 | 20 | 15 | 90 | 90 | 0 |  | — |
| lru_f2 | 30 | 20→16 | 15→12 | 15→14 | 80 | 72 | +8 |  | — |
| lru_f3 | 35→18 | 20→18 | 15→12 | 15→14 | 85 | 62 | +23 | 🚩 | Documented mis-eviction: pop() evicts the MOST-recently-used. Correctness must be heavily docked (~18). Corrected total ~62. |
| lru_f4 | 35→28 | 25 | 20 | 15 | 95 | 88 | +7 |  | — |
| lru_f5 | 35→33 | 25 | 20 | 15 | 95 | 93 | +2 |  | — |
| lru_g1 | 30→12 | 25 | 20→8 | 15→14 | 90 | 59 | +31 | 🚩 | Eviction body never deletes — any overflowing put infinite-loops, not just capacity=0. Correctness/Efficiency badly over-graded. Corrected total ~59. |
| lru_g2 | 38→35 | 25 | 20 | 15 | 98 | 95 | +3 |  | — |
| lru_h1 | 40 | 25 | 20 | 13→8 | 88 | 93 | -5 |  | Localized compile error (missing closing brace) — algorithm intent is fully readable; under the new rubric the defect is capped at −5 via Code Quality, not a Correctness zero. |
| lru_h2 | 35 | 25 | 20 | 15→10 | 95 | 90 | +5 |  | Localized compile error (`store` referenced without `this.`) — algorithm intent is fully readable; capped at −5 via Code Quality under the new rubric. |
| lru_h3 | 38 | 25 | 20 | 15→10 | 98 | 93 | +5 |  | Localized compile error (`Map<K, V, V>` — extra type arg) — algorithm intent is fully readable; capped at −5 via Code Quality under the new rubric. |
| lru_i1 | 40 | 25 | 10 | 15 | 90 | 90 | 0 |  | — |
| lru_i2 | 40 | 25 | 20 | 15 | 100 | 99 | +1 |  | — |
| lru_i3 | 40 | 20→25 | 20 | 15 | 95 | 99 | -4 |  | — |

### Flagged in P3
- **lru_a3** (you 70 / me 97, Δ -27): Human gave Correctness 20 and Efficiency 15 to a clean, idiomatic, O(1) generic Map LRU that is fully correct; throwing `RangeError` on `capacity<=0` is defensive design, not a bug. Recommended corrected total ~97.
- **lru_b1** (you 80 / me 79, Δ +1): Totals match, but the human scored Efficiency 15 on a genuinely O(1) hash+DLL — the documented hash+DLL under-grade pattern. Efficiency should be 20; Correctness should instead drop slightly for the plain-object index coercing numeric keys.
- **lru_b2** (you 80 / me 98, Δ -18): Correct generic hash+DLL with sentinel head/tail was scored DS 15 / Efficiency 15 — both should be full (25/20). The human penalized a correct hash+DLL relative to equivalent Map solutions. Recommended corrected total ~98.
- **lru_b3** (you 60 / me 96, Δ -36): Largest gap in the set. A clean, encapsulated, correct hash+DLL was given Correctness 20 / DS 15 / Eff 15 / CQ 10 — all unjustified. Only genuine flaw is a capacity=0 edge that evicts the sentinel tail. Recommended corrected total ~96.
- **lru_c1** (you 80 / me 64, Δ +16): Human awarded full Correctness 40 and DS 20, missing that `String(key)` coercion collides numeric and string keys and that an object literal is being abused as an ordered map. Recommended corrected total ~64.
- **lru_c2** (you 75 / me 85, Δ -10): LRU semantics are fully correct, so Correctness should be 40 (not 35); DS 15 is harsh for two clean parallel Maps with no corruption. The only real cost is the O(n) eviction scan. Recommended corrected total ~85.
- **lru_f3** (you 85 / me 62, Δ +23): Human's Correctness 35 ignores the documented mis-eviction — `pop()` evicts the most-recently-used entry instead of the least. This is a core eviction defect; Correctness should be ~18. Recommended corrected total ~62.
- **lru_g1** (you 90 / me 59, Δ +31): The eviction loop body calls `this.store.has(oldest)` and never deletes, so any `put` that overflows capacity infinite-loops (not only capacity=0). Correctness 30 and Efficiency 20 are far too high. Recommended corrected total ~59.
- *(Re-graded under softened rubric: `lru_h1`, `h2`, `h3` were flagged in the first pass for compile errors. The new rubric grades demonstrated algorithmic intent, capping a localized compile defect at −5 via Code Quality rather than zeroing Correctness. All three submissions have a fully-readable LRU implementation around the localized defect, so the walk-back lands within 5 of the human score and the flags drop.)*

---

## P4 — Dijkstra Shortest Path (25 submissions)

**Rubric:** Correctness 45 · Efficiency 25 · Data Structures 15 · Code Quality 15
**Summary:** flagged 9/25 · mean \|Δ\| 6.6 · your mean 88.0 · my mean 83.3

| ID | Correctness | Efficiency | Data Structures | Code Quality | Total (you) | Total (me) | Δ | Flag | Suggestion |
|----|---|---|---|---|---|---|---|---|---|
| dijkstra_a1 | 40→38 | 20→17 | 10→7 | 15→13 | 85 | 75 | +10 | 🚩 | Deduct on Correctness: returns `INT_MAX` (not `LLONG_MAX`) for unreachable nodes — wrong sentinel. Linear scan should cost more Data Structures points. Corrected total ~75. |
| dijkstra_a2 | 40→45 | 20→17 | 10→7 | 5→11 | 75 | 80 | -5 |  | — |
| dijkstra_a3 | 45 | 20→17 | 10→7 | 15 | 90 | 84 | +6 |  | — |
| dijkstra_b1 | 45 | 20→18 | 15 | 15 | 95 | 93 | +2 |  | — |
| dijkstra_b2 | 45 | 25 | 15 | 15 | 100 | 100 | 0 |  | — |
| dijkstra_b3 | 45 | 25 | 15 | 15 | 100 | 100 | 0 |  | — |
| dijkstra_c1 | 45 | 20→22 | 15 | 15 | 95 | 97 | -2 |  | — |
| dijkstra_c2 | 45 | 25 | 15 | 15 | 100 | 100 | 0 |  | — |
| dijkstra_d1 | 45 | 15→25 | 15 | 15 | 90 | 100 | -10 | 🚩 | Efficiency wrongly docked: this skips stale entries (`d > dist[u]`) and runs O((V+E)logV). An unused `parent` array is not an efficiency defect. Corrected total 100. |
| dijkstra_d2 | 45 | 20→25 | 15 | 15 | 95 | 100 | -5 |  | — |
| dijkstra_e1 | 30→15 | 15→12 | 10→12 | 10→13 | 65 | 52 | +13 | 🚩 | Plain BFS, ignores weights — not Dijkstra. Correctness must score far lower (~15). Corrected total ~52. |
| dijkstra_e2 | 30→20 | 20→10 | 10→12 | 10→13 | 70 | 55 | +15 | 🚩 | Bellman-Ford, not Dijkstra; O(VE). Wrong algorithm hits Correctness hard and Efficiency too. Corrected total ~55. |
| dijkstra_e3 | 30→14 | 15→8 | 10→11 | 10→12 | 65 | 45 | +20 | 🚩 | DFS-based, not Dijkstra and produces wrong distances (no shortest tracking); exponential. Correctness must drop to ~14. Corrected total ~45. |
| dijkstra_f1 | 35→25 | 25 | 15 | 15 | 90 | 80 | +10 | 🚩 | Marks node visited before popping — misses shorter paths discovered later, so distances can be wrong. Correctness should drop further (~25). Corrected total ~80. |
| dijkstra_f2 | 35→20 | 25→22 | 15 | 15 | 90 | 72 | +18 | 🚩 | Never pushes relaxed nodes back — only direct neighbors of source ever get a finite distance. This is a severe correctness bug, ~20/45. Corrected total ~72. |
| dijkstra_f3 | 40→42 | 25 | 15 | 15 | 95 | 97 | -2 |  | — |
| dijkstra_f4 | 40→8 | 25→22 | 15 | 15 | 85 | 60 | +25 | 🚩 | `dist[source]=LLONG_MAX` — source never relaxes anything; the heap pop is immediately stale and nothing propagates. Output is all-`LLONG_MAX`. Correctness ~8/45. Corrected total ~60. |
| dijkstra_g1 | 43 | 25 | 15 | 15 | 98 | 98 | 0 |  | — |
| dijkstra_g2 | 43 | 25 | 15 | 15 | 98 | 98 | 0 |  | — |
| dijkstra_g3 | 40→30 | 25 | 15 | 15 | 95 | 85 | +10 | 🚩 | Returns `0` for unreachable nodes instead of `LLONG_MAX`, and `dist` init to `0` makes `dist[v]==0` ambiguous — relaxation logic is unsafe. Correctness ~30/45. Corrected total ~85. |
| dijkstra_h1 | 40 | 25 | 15 | 10→5 | 90 | 85 | +5 |  | Localized compile error (missing `#include <queue>`) — algorithm intent is fully readable; under the new rubric the defect is capped at −5 via Code Quality, not a Correctness zero. |
| dijkstra_h2 | 25 | 25 | 15 | 10→5 | 75 | 70 | +5 |  | Localized compile error (wrong `priority_queue` template params) — algorithm intent is readable; capped at −5 via Code Quality under the new rubric. |
| dijkstra_h3 | 45 | 25 | 15 | 10→5 | 90 | 90 | 0 |  | Localized compile error (missing closing brace) — algorithm intent is fully readable; capped at −5 via Code Quality under the new rubric. |
| dijkstra_i1 | 30→25 | 20→18 | 10→11 | 10→13 | 70 | 67 | +3 |  | — |
| dijkstra_i2 | 45 | 25 | 15 | 15 | 100 | 100 | 0 |  | — |

### Flagged in P4
- **dijkstra_a1** (you 85 / me 75, Δ +10): The human missed that the distance vector is initialized to `INT_MAX`, so unreachable nodes are reported as `INT_MAX` rather than the required `LLONG_MAX` sentinel — a real Correctness defect. The naive linear scan also deserves a larger Data Structures deduction. Recommended corrected total ~75.
- **dijkstra_d1** (you 90 / me 100, Δ -10): The human docked Efficiency to 15/25, but this implementation correctly skips stale heap entries with `if (d > dist[u]) continue;` and runs in O((V+E)logV). An unused `parent` array is dead-but-harmless code, not an efficiency problem. Recommended corrected total 100.
- **dijkstra_e1** (you 65 / me 52, Δ +13): Human Correctness of 30/45 is far too generous for a plain BFS that ignores edge weights entirely — it is the wrong algorithm and produces wrong distances on any weighted graph. Correctness should be ~15. Recommended corrected total ~52.
- **dijkstra_e2** (you 70 / me 55, Δ +15): This is Bellman-Ford (V-1 full passes), not Dijkstra, and runs O(VE). Wrong-algorithm should sink Correctness to ~20 and Efficiency to ~10; the human gave 30 and 20. Recommended corrected total ~55.
- **dijkstra_e3** (you 65 / me 45, Δ +20): A DFS that explores in depth order and does not settle shortest distances — wrong algorithm and wrong results, with exponential blow-up. Correctness ~14/45, not 30. Recommended corrected total ~45.
- **dijkstra_f1** (you 90 / me 80, Δ +10): The node is marked visited before it is popped, so a later, cheaper path to it is skipped — distances can be wrong. Correctness should drop to ~25/45; the human's 35 plus a perfect 100-style finish understates the bug. Recommended corrected total ~80.
- **dijkstra_f2** (you 90 / me 72, Δ +18): The relaxation updates `dist[v]` but never pushes `v` onto the heap, so only the source's direct neighbors ever get a finite distance — a severe correctness failure. Correctness ~20/45, not 35. Recommended corrected total ~72.
- **dijkstra_f4** (you 95 / me 60, Δ +35): `dist[source]` is initialized to `LLONG_MAX`, so the popped entry is immediately stale and no relaxation ever fires — the function returns all-`LLONG_MAX`. This is almost completely non-functional; Correctness ~8/45, not 40. Recommended corrected total ~60.
- **dijkstra_g3** (you 95 / me 85, Δ +10): Distances are initialized to `0` and unreachable nodes are returned as `0` instead of `LLONG_MAX`; the `dist[v]==0` test also makes relaxation ambiguous. Correctness ~30/45. Recommended corrected total ~85.
- *(Re-graded under softened rubric: `dijkstra_h1`, `h2`, `h3` were flagged in the first pass for compile errors. The new rubric grades demonstrated algorithmic intent, capping a localized compile defect at −5 via Code Quality rather than zeroing Correctness. All three submissions have a readable Dijkstra implementation around the localized defect, so the walk-back lands within 5 of the human score and the flags drop.)*

---

## P5 — Binary Search Tree (23 submissions)

**Rubric:** Correctness 40 · Data Structures 30 · Efficiency 15 · Code Quality 15
**Summary:** flagged 6/23 · mean \|Δ\| 5.5 · your mean 90.9 · my mean 89.6

| ID | Correctness | Data Structures | Efficiency | Code Quality | Total (you) | Total (me) | Δ | Flag | Suggestion |
|----|---|---|---|---|---|---|---|---|---|
| BstA1 | 35→40 | 30→24 | 15 | 10 | 90 | 89 | +1 |  | — |
| BstA2 | 40 | 30 | 15 | 15 | 100 | 100 | 0 |  | — |
| BstA3 | 40 | 30 | 15 | 15 | 100 | 100 | 0 |  | — |
| BstB1 | 30→40 | 25→26 | 15 | 10→11 | 80 | 92 | -12 | 🚩 | delete/inorder are fully correct; raise Correctness to 40 and total to ~92 |
| BstB2 | 40 | 30 | 15 | 10→13 | 95 | 98 | -3 |  | — |
| BstB3 | 40 | 30 | 15 | 15 | 100 | 100 | 0 |  | — |
| BstC1 | 40 | 30 | 15 | 10 | 95 | 95 | 0 |  | — |
| BstC2 | 40 | 30 | 15 | 15 | 100 | 100 | 0 |  | — |
| BstD1 | 30→40 | 10→8 | 15 | 15 | 70 | 78 | -8 |  | — |
| BstD2 | 30→40 | 10→8 | 15 | 15 | 70 | 78 | -8 |  | — |
| BstE1 | 30→26 | 30 | 15 | 15 | 90 | 86 | +4 |  | — |
| BstE2 | 30→20 | 30 | 15 | 15 | 90 | 80 | +10 | 🚩 | contains always false ⇒ contains and delete both broken; cut Correctness to ~20, total ~80 |
| BstE3 | 30→28 | 30 | 15 | 15 | 90 | 88 | +2 |  | — |
| BstE4 | 35→26 | 30 | 15 | 15 | 95 | 86 | +9 | 🚩 | two-children delete leaves duplicate + wrong size; Correctness 35 is inconsistent, drop to ~26 |
| BstF1 | 30→28 | 30 | 15 | 15 | 90 | 88 | +2 |  | — |
| BstF2 | 35→30 | 30 | 15 | 15 | 95 | 90 | +5 |  | — |
| BstF3 | 40 | 30 | 15→7 | 10→15 | 95 | 92 | +3 |  | — |
| BstG1 | 40 | 30 | 15→11 | 15 | 100 | 96 | +4 |  | — |
| BstG2 | 40 | 30 | 5→6 | 10→11 | 85 | 87 | -2 |  | — |
| BstH1 | 35→18 | 25→22 | 15 | 10 | 85 | 65 | +20 | 🚩 | delete/inorder stubbed + static-root compile concern; cut Correctness to ~18, total ~65 |
| BstH2 | 35→16 | 30 | 15 | 10→11 | 90 | 72 | +18 | 🚩 | missing List import ⇒ does not compile, plus delete/inorder stubbed; Correctness to ~16 |
| BstI1 | 40 | 25→30 | 10→15 | 10→15 | 85 | 100 | -15 | 🚩 | augmented BST: size() is genuinely O(1) and code is clean; raise to ~100 |
| BstI2 | 40 | 30 | 15 | 15 | 100 | 100 | 0 |  | — |

### Flagged in P5
- **BstB1** (you 80 / me 92, Δ -12): The human docked Correctness to 30, but BstB1's iterative insert/contains and recursive delete (including the two-children case) are all correct and idempotent — there is no behavioural bug. The only real defects are public `Node` fields (minor Data Structures deduction) and package-private `root`/`n` (Code Quality). Recommended corrected total ~92.
- **BstE2** (you 90 / me 80, Δ +10): README-documented defect not reflected. `contains` recurses on the global `root` instead of the subtree, so it returns `false` for every non-root key; since `delete` gates on `contains`, deletion of non-root keys silently no-ops too. Two of five methods are broken — Correctness ~20, total ~80.
- **BstE4** (you 95 / me 86, Δ +9): Internally inconsistent breakdown. The two-children `delete` copies the successor key but omits the line that removes the successor, so a duplicate key remains and `size` is wrong — a real Correctness defect, yet the human left Correctness near full at 35. Recommended Correctness ~26, total ~86.
- **BstH1** (you 85 / me 65, Δ +20): README-documented defect not reflected. `delete` always returns `false` and `inorder` always returns an empty list — two methods are non-functional stubs — plus `root` is `static` with a non-static inner `Node` (the compile concern flagged in group H). Correctness ~18, Data Structures ~22, total ~65.
- **BstH2** (you 90 / me 72, Δ +18): README-documented defect not reflected. Missing `import java.util.List` means the file does not compile (the rubric makes "compiles" a Correctness bullet), and `delete`/`inorder` are stubs. Correctness ~16, total ~72.
- **BstI1** (you 85 / me 100, Δ -15): The human under-credited a clean, fully correct augmented BST. Each node caches `subtreeSize`, so `size()` is genuinely O(1) — that should earn full Efficiency, not 10. Data Structures and Code Quality are also idiomatic and well-encapsulated. Recommended corrected total ~100.

---

## P6 — Concurrent Worker Pool (23 submissions)

**Rubric:** Correctness 35 · Concurrency Safety 35 · Efficiency 15 · Code Quality 15
**Summary:** flagged 10/23 · mean \|Δ\| 12.7 · your mean 79.1 · my mean 72.7

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

---
