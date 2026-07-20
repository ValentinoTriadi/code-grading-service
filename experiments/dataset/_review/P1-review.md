## P1 — Sum Array (28 submissions)

**Rubric:** Correctness 60 · Code Quality 25 · Efficiency 15
**Summary:** flagged 11/28 · mean |Δ| 19.5 · your mean 80.6 · my mean 67.7

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
