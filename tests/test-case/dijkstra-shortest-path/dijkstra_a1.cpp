#include <vector>
#include <climits>
using namespace std;

vector<long long> dijkstra(int n, const vector<vector<pair<int,int>>>& graph, int source) {
    vector<long long> dist(n, INT_MAX);
    vector<bool> visited(n, false);
    dist[source] = 0;

    for (int i = 0; i < n; i++) {
        int u = -1;
        long long best = INT_MAX;
        for (int j = 0; j < n; j++) {
            if (!visited[j] && dist[j] < best) {
                best = dist[j];
                u = j;
            }
        }
        if (u == -1) break;
        visited[u] = true;
        for (int k = 0; k < (int)graph[u].size(); k++) {
            int v = graph[u][k].first;
            int w = graph[u][k].second;
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
    }
    return dist;
}
