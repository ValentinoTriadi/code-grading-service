# P4 — Dijkstra Shortest Path
_medium · cpp · 25 submissions_

## Description

Implement Dijkstra's single-source shortest-path algorithm with signature `std::vector<long long> dijkstra(int n, const std::vector<std::vector<std::pair<int, int>>>& graph, int source)`. `n` is the number of nodes (0..n-1); `graph[u]` is a list of `{v, w}` outgoing edges with non-negative weights. Return shortest distances from `source` to every node, with `LLONG_MAX` for unreachable nodes. Edge weights fit in `int`; distances accumulate in `long long`.

## Rubric

- **Correctness (45)** — The algorithm is actually Dijkstra (not BFS, DFS, or Bellman-Ford). Returns shortest distances from `source` to every node, with `LLONG_MAX` (or equivalent sentinel) for unreachable nodes. Initializes `dist[source] = 0`. Does not crash on `source` out of range. Handles negative weights either by failing fast or by documenting the precondition. Compiles without errors.
- **Efficiency (25)** — Skips stale heap entries to keep the run time at O((V+E) log V). Uses `long long` for accumulated distances (avoids overflow). Does not re-process settled nodes. Does not iterate the full graph for every relaxation.
- **Data Structures (15)** — Uses `std::priority_queue` (min-heap) or `std::set` for the frontier — not a linear scan or unsorted list. Adjacency list is consumed correctly (no transpose mistakes).
- **Code Quality (15)** — Idiomatic modern C++. Prefers `std::numeric_limits<long long>::max()` over `LLONG_MAX` arithmetic. Avoids `using namespace std` at file scope. Uses structured bindings or named pairs for `{v, w}` rather than `.first` / `.second` everywhere.

## Score sheet

| Submission | Correctness (45) | Efficiency (25) | Data Structures (15) | Code Quality (15) | **Total** | Notes |
|---|---|---|---|---|---|---|
| dijkstra_a1 |      |      |      |      |        |       |
| dijkstra_a2 |      |      |      |      |        |       |
| dijkstra_a3 |      |      |      |      |        |       |
| dijkstra_b1 |      |      |      |      |        |       |
| dijkstra_b2 |      |      |      |      |        |       |
| dijkstra_b3 |      |      |      |      |        |       |
| dijkstra_c1 |      |      |      |      |        |       |
| dijkstra_c2 |      |      |      |      |        |       |
| dijkstra_d1 |      |      |      |      |        |       |
| dijkstra_d2 |      |      |      |      |        |       |
| dijkstra_e1 |      |      |      |      |        |       |
| dijkstra_e2 |      |      |      |      |        |       |
| dijkstra_e3 |      |      |      |      |        |       |
| dijkstra_f1 |      |      |      |      |        |       |
| dijkstra_f2 |      |      |      |      |        |       |
| dijkstra_f3 |      |      |      |      |        |       |
| dijkstra_f4 |      |      |      |      |        |       |
| dijkstra_g1 |      |      |      |      |        |       |
| dijkstra_g2 |      |      |      |      |        |       |
| dijkstra_g3 |      |      |      |      |        |       |
| dijkstra_h1 |      |      |      |      |        |       |
| dijkstra_h2 |      |      |      |      |        |       |
| dijkstra_h3 |      |      |      |      |        |       |
| dijkstra_i1 |      |      |      |      |        |       |
| dijkstra_i2 |      |      |      |      |        |       |

## Submissions

### 1. `dijkstra_a1`

```cpp
#include <vector>
#include <climits>
using namespace std;

vector<long long> dijkstra(int n, const vector<vector<pair<int,int>>>& graph, int source) {
    vector<long long> dist(n, INT_MAX);
    vector<bool> visited(n, false);
    dist[source] = 0;

    for (int i = 0; i < n; i++) {
        int u = -1;
        long long best = INT_MAX;
        for (int j = 0; j < n; j++) {
            if (!visited[j] && dist[j] < best) {
                best = dist[j];
                u = j;
            }
        }
        if (u == -1) break;
        visited[u] = true;
        for (int k = 0; k < (int)graph[u].size(); k++) {
            int v = graph[u][k].first;
            int w = graph[u][k].second;
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 2. `dijkstra_a2`

```cpp
#include <vector>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    std::vector<bool> visited(n, false);
    dist[source] = 0;

    for (int i = 0; i < n; i++) {
        int u = -1;
        long long best = LLONG_MAX;
        for (int i = 0; i < n; i++) {
            if (!visited[i] && dist[i] < best) {
                best = dist[i];
                u = i;
            }
        }
        if (u == -1) break;
        visited[u] = true;
        for (auto& edge : graph[u]) {
            int v = edge.first;
            int w = edge.second;
            if (dist[u] != LLONG_MAX && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 3. `dijkstra_a3`

```cpp
#include <vector>
#include <limits>
#include <utility>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    constexpr long long INF = std::numeric_limits<long long>::max();
    std::vector<long long> dist(n, INF);
    std::vector<bool> settled(n, false);
    dist[source] = 0;

    for (int step = 0; step < n; ++step) {
        int u = -1;
        long long best = INF;
        for (int i = 0; i < n; ++i) {
            if (!settled[i] && dist[i] < best) {
                best = dist[i];
                u = i;
            }
        }
        if (u == -1) break;
        settled[u] = true;

        for (const auto& [v, w] : graph[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 4. `dijkstra_b1`

```cpp
#include <vector>
#include <queue>
#include <climits>
using namespace std;

vector<long long> dijkstra(int n, const vector<vector<pair<int,int>>>& graph, int source) {
    vector<long long> dist(n, LLONG_MAX);
    priority_queue<pair<long long,int>, vector<pair<long long,int>>, greater<pair<long long,int>>> pq;
    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto top = pq.top();
        pq.pop();
        long long d = top.first;
        int u = top.second;
        for (auto& e : graph[u]) {
            int v = e.first, w = e.second;
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 5. `dijkstra_b2`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;
    std::vector<long long> dist(n, LLONG_MAX);

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d > dist[u]) continue;

        for (auto& [v, w] : graph[u]) {
            long long nd = d + w;
            if (nd < dist[v]) {
                dist[v] = nd;
                pq.push({nd, v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 6. `dijkstra_b3`

```cpp
#include <vector>
#include <queue>
#include <limits>
#include <functional>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    constexpr long long INF = std::numeric_limits<long long>::max();
    std::vector<long long> dist(n, INF);

    using Entry = std::pair<long long, int>;
    std::priority_queue<Entry, std::vector<Entry>, std::greater<>> pq;

    dist[source] = 0;
    pq.emplace(0, source);

    while (!pq.empty()) {
        const auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;

        for (const auto& [v, w] : graph[u]) {
            const long long nd = d + w;
            if (nd < dist[v]) {
                dist[v] = nd;
                pq.emplace(nd, v);
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 7. `dijkstra_c1`

```cpp
#include <vector>
#include <set>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    std::set<std::pair<long long,int>> active;

    dist[source] = 0;
    active.insert(std::make_pair((long long)0, source));

    while (!active.empty()) {
        auto top = *active.begin();
        active.erase(active.begin());
        int u = top.second;

        for (auto& edge : graph[u]) {
            int v = edge.first;
            int w = edge.second;
            if (dist[u] + w < dist[v]) {
                if (dist[v] != LLONG_MAX) {
                    active.erase(std::make_pair(dist[v], v));
                }
                dist[v] = dist[u] + w;
                active.insert(std::make_pair(dist[v], v));
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 8. `dijkstra_c2`

```cpp
#include <vector>
#include <set>
#include <limits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    constexpr long long INF = std::numeric_limits<long long>::max();
    std::vector<long long> dist(n, INF);
    std::set<std::pair<long long,int>> active;

    dist[source] = 0;
    active.emplace(0LL, source);

    while (!active.empty()) {
        const auto [d, u] = *active.begin();
        active.erase(active.begin());

        for (const auto& [v, w] : graph[u]) {
            const long long nd = d + w;
            if (nd < dist[v]) {
                if (dist[v] != INF) {
                    active.erase({dist[v], v});
                }
                dist[v] = nd;
                active.emplace(nd, v);
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 9. `dijkstra_d1`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    std::vector<int> parent(n, -1);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                parent[v] = u;
                pq.push({dist[v], v});
            }
        }
    }
    (void)parent;
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 10. `dijkstra_d2`

```cpp
#include <vector>
#include <queue>
#include <limits>

namespace {
std::vector<int> last_parent;
}

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    constexpr long long INF = std::numeric_limits<long long>::max();
    std::vector<long long> dist(n, INF);
    std::vector<int> parent(n, -1);

    using Entry = std::pair<long long, int>;
    std::priority_queue<Entry, std::vector<Entry>, std::greater<>> pq;

    dist[source] = 0;
    pq.emplace(0, source);

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (const auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                parent[v] = u;
                pq.emplace(dist[v], v);
            }
        }
    }

    last_parent = std::move(parent);
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 11. `dijkstra_e1`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    std::queue<int> q;

    dist[source] = 0;
    q.push(source);

    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (const auto& [v, w] : graph[u]) {
            (void)w;
            if (dist[u] + 1 < dist[v]) {
                dist[v] = dist[u] + 1;
                q.push(v);
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 12. `dijkstra_e2`

```cpp
#include <vector>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    dist[source] = 0;

    for (int iter = 0; iter < n - 1; ++iter) {
        for (int u = 0; u < n; ++u) {
            if (dist[u] == LLONG_MAX) continue;
            for (const auto& [v, w] : graph[u]) {
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                }
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 13. `dijkstra_e3`

```cpp
#include <vector>
#include <climits>

static void dfs(int u,
                long long acc,
                const std::vector<std::vector<std::pair<int,int>>>& graph,
                std::vector<long long>& dist,
                std::vector<bool>& on_path) {
    if (acc >= dist[u]) return;
    dist[u] = acc;
    on_path[u] = true;
    for (auto& [v, w] : graph[u]) {
        if (!on_path[v]) {
            dfs(v, acc + w, graph, dist, on_path);
        }
    }
    on_path[u] = false;
}

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    std::vector<bool> on_path(n, false);
    dfs(source, 0, graph, dist, on_path);
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 14. `dijkstra_f1`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    std::vector<bool> visited(n, false);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});
    visited[source] = true;

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        for (auto& [v, w] : graph[u]) {
            if (visited[v]) continue;
            if (d + w < dist[v]) {
                dist[v] = d + w;
                visited[v] = true;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 15. `dijkstra_f2`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                // forgot: pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 16. `dijkstra_f3`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    std::vector<int> parent(n, -1);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        for (auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
            if (d + w == dist[v] && parent[v] == -1) {
                parent[v] = u;
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 17. `dijkstra_f4`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = LLONG_MAX;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 18. `dijkstra_g1`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 19. `dijkstra_g2`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (auto& [v, w] : graph[u]) {
            // No check for w < 0 — Dijkstra silently produces wrong answers
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 20. `dijkstra_g3`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, 0);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > 0 && d > dist[u]) continue;
        for (auto& [v, w] : graph[u]) {
            if (dist[v] == 0 || d + w < dist[v]) {
                if (v != source) {
                    dist[v] = d + w;
                    pq.push({dist[v], v});
                }
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 21. `dijkstra_h1`

```cpp
#include <vector>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 22. `dijkstra_h2`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);

    std::priority_queue<std::pair<long long,int>, std::greater<std::pair<long long,int>>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        for (auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 23. `dijkstra_h3`

```cpp
#include <vector>
#include <queue>
#include <climits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);

    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (auto& [v, w] : graph[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }

    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 24. `dijkstra_i1`

```cpp
#include <vector>
#include <deque>
#include <limits>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    constexpr long long INF = std::numeric_limits<long long>::max();
    std::vector<long long> dist(n, INF);
    std::deque<int> dq;

    dist[source] = 0;
    dq.push_back(source);

    while (!dq.empty()) {
        const int u = dq.front();
        dq.pop_front();
        for (const auto& [v, w] : graph[u]) {
            const long long nd = dist[u] + w;
            if (nd < dist[v]) {
                dist[v] = nd;
                if (w == 0) dq.push_front(v);
                else        dq.push_back(v);
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 25. `dijkstra_i2`

```cpp
#include <vector>
#include <queue>
#include <limits>
#include <functional>

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    constexpr long long INF = std::numeric_limits<long long>::max();
    std::vector<long long> dist(n, INF);

    auto cmp = [&dist](int a, int b) { return dist[a] > dist[b]; };
    std::priority_queue<int, std::vector<int>, decltype(cmp)> pq(cmp);

    dist[source] = 0;
    pq.push(source);

    std::vector<bool> done(n, false);
    while (!pq.empty()) {
        int u = pq.top();
        pq.pop();
        if (done[u]) continue;
        done[u] = true;
        for (const auto& [v, w] : graph[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push(v);
            }
        }
    }
    return dist;
}
```

> Correctness: ____/45  Efficiency: ____/25  Data Structures: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:
