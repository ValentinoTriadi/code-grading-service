## P4 — Dijkstra Shortest Path (25 submissions)

**Rubric:** Correctness 45 · Efficiency 25 · Data Structures 15 · Code Quality 15
**Summary:** flagged 7/25 · mean |Δ| 5.4 · your mean 89.6 · my mean 86.2

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
