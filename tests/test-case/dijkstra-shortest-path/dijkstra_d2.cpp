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
