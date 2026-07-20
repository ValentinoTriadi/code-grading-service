#include <vector>
#include <queue>
#include <climits>
using namespace std;

vector<long long> dijkstra(int n, const vector<vector<pair<int,int>>>& graph, int source) {
    vector<long long> dist(n, LLONG_MAX);
    priority_queue<pair<long long,int>, vector<pair<long long,int>>, greater<pair<long long,int>>> pq;
    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto top = pq.top();
        pq.pop();
        long long d = top.first;
        int u = top.second;
        for (auto& e : graph[u]) {
            int v = e.first, w = e.second;
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
