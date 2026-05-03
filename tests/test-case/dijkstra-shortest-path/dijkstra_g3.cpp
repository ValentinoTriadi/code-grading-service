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
