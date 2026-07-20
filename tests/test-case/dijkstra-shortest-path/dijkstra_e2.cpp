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
