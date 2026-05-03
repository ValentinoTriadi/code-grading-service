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
