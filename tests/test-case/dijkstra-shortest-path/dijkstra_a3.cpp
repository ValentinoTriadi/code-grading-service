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
