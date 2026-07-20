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
