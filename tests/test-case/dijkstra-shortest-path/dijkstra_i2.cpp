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
