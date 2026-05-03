# Dijkstra Shortest Path — Test Cases

**Language:** C++
**Difficulty:** Medium

## Problem

Implement Dijkstra's single-source shortest-path algorithm.

```cpp
std::vector<long long> dijkstra(
    int n,
    const std::vector<std::vector<std::pair<int, int>>>& graph,
    int source
);
```

- `n` is the number of nodes (`0 .. n-1`).
- `graph[u]` is a list of `{v, w}` outgoing edges with **non-negative** weights.
- Return a vector of length `n` where `dist[v]` is the shortest distance from `source` to `v`, or `LLONG_MAX` (treated as "unreachable") if there is no path.

Edge weights fit in `int`. Distances are accumulated in `long long`.

Each group represents a different implementation approach. Within a group:

- **1** = poor (bad style, magic numbers, inefficient)
- **2** = acceptable (correct, some style issues)
- **3** = good (clean, idiomatic)

---

## Group A — Naive O(V²) (no priority queue)

For each iteration, linearly scan unvisited nodes for the minimum-distance one.

| File | Quality | Notes |
|------|---------|-------|
| `dijkstra_a1.cpp` | Poor | `using namespace std`, raw `INT_MAX` arithmetic risks overflow |
| `dijkstra_a2.cpp` | Acceptable | Correct, uses `LLONG_MAX`, but inner loop variable shadows outer |
| `dijkstra_a3.cpp` | Good | Clean separation, `std::numeric_limits<long long>::max()` |

## Group B — `std::priority_queue` (binary heap)

Standard textbook implementation with a min-heap of `{dist, node}`.

| File | Quality | Notes |
|------|---------|-------|
| `dijkstra_b1.cpp` | Poor | Doesn't skip stale heap entries — slower but correct |
| `dijkstra_b2.cpp` | Acceptable | Correct; `greater<>` comparator inline; no early exit |
| `dijkstra_b3.cpp` | Good | Skips stale entries, uses `std::pair` and `decltype` cleanly |

## Group C — `std::set<std::pair>` (ordered set)

Uses a `set<pair<long long,int>>` keyed on `{dist, node}` and erases-then-inserts on relaxation.

| File | Quality | Notes |
|------|---------|-------|
| `dijkstra_c1.cpp` | Acceptable | Correct, but rebuilds pair on every erase |
| `dijkstra_c2.cpp` | Good | Clean erase/insert, structured bindings |

## Group D — Path reconstruction (parents array)

Same algorithm but also tracks `parent[]` for path reconstruction.

| File | Quality | Notes |
|------|---------|-------|
| `dijkstra_d1.cpp` | Acceptable | Correct dist + parent, returns dist only (parent unused) |
| `dijkstra_d2.cpp` | Good | Returns dist; parent kept as static for follow-up reconstruction |

## Group E — Wrong / broken algorithms

Compiles, but is not Dijkstra.

| File | Bug |
|------|-----|
| `dijkstra_e1.cpp` | Plain BFS (ignores weights) — only correct on unweighted graphs |
| `dijkstra_e2.cpp` | Bellman-Ford with V-1 relaxations — correct answer but `O(VE)` and not Dijkstra |
| `dijkstra_e3.cpp` | DFS-based — explores in depth order, doesn't track shortest |

## Group F — Logic bugs (Dijkstra-shaped but wrong)

| File | Bug |
|------|-----|
| `dijkstra_f1.cpp` | Marks node visited *before* popping from heap — misses better paths |
| `dijkstra_f2.cpp` | Updates `dist[v]` inside the relaxation but forgets to push `v` back into the heap |
| `dijkstra_f3.cpp` | Uses `<` instead of `<=` when relaxing — drops equal-cost ties incorrectly mixed with parent tracking, leaves parent stale |
| `dijkstra_f4.cpp` | Initializes `dist[source] = INT_MAX` — never relaxes anything |

## Group G — Boundary / edge-case bugs

| File | Bug |
|------|-----|
| `dijkstra_g1.cpp` | Crashes when `source == n` (off-by-one): no bounds check |
| `dijkstra_g2.cpp` | Treats negative weights silently — Dijkstra produces wrong answers without warning |
| `dijkstra_g3.cpp` | Returns `0` instead of `LLONG_MAX` for unreachable nodes |

## Group H — Compile errors

| File | Bug |
|------|-----|
| `dijkstra_h1.cpp` | Missing `#include <queue>` |
| `dijkstra_h2.cpp` | `priority_queue` declared with wrong number of template params |
| `dijkstra_h3.cpp` | Missing closing brace on outer function |

## Group I — Creative correct alternatives

| File | Quality | Notes |
|------|---------|-------|
| `dijkstra_i1.cpp` | Acceptable | 0-1 BFS with `std::deque` — only correct if edge weights are 0 or 1 |
| `dijkstra_i2.cpp` | Good | Heap of node IDs, comparator captures `dist[]` — neat lazy-comparator trick |
