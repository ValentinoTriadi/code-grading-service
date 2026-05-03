#include <vector>
#include <climits>

static void dfs(int u,
                long long acc,
                const std::vector<std::vector<std::pair<int,int>>>& graph,
                std::vector<long long>& dist,
                std::vector<bool>& on_path) {
    if (acc >= dist[u]) return;
    dist[u] = acc;
    on_path[u] = true;
    for (auto& [v, w] : graph[u]) {
        if (!on_path[v]) {
            dfs(v, acc + w, graph, dist, on_path);
        }
    }
    on_path[u] = false;
}

std::vector<long long> dijkstra(int n,
                                const std::vector<std::vector<std::pair<int,int>>>& graph,
                                int source) {
    std::vector<long long> dist(n, LLONG_MAX);
    std::vector<bool> on_path(n, false);
    dfs(source, 0, graph, dist, on_path);
    return dist;
}
