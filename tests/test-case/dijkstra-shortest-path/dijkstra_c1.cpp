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
