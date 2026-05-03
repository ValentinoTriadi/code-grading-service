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
