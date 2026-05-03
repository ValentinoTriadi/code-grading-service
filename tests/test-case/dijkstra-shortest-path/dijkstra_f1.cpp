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
