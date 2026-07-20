## P3 — LRU Cache (25 submissions)

**Rubric:** Correctness 40 · Data Structures 25 · Efficiency 20 · Code Quality 15
**Summary:** flagged 11/25 · mean |Δ| 11.8 · your mean 84.2 · my mean 85.1

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
