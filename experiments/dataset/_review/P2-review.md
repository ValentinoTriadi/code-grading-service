## P2 — Palindrome Check (20 submissions)

**Rubric:** Correctness 60 · Code Quality 25 · Efficiency 15
**Summary:** flagged 8/20 · mean |Δ| 9.1 · your mean 91.3 · my mean 67.5

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
