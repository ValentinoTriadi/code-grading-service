## P5 — Binary Search Tree (23 submissions)

**Rubric:** Correctness 40 · Data Structures 30 · Efficiency 15 · Code Quality 15
**Summary:** flagged 6/23 · mean |Δ| 5.5 · your mean 90.9 · my mean 89.6

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
