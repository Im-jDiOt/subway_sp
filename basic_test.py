import networkx as nx
import time
import random
import pandas as pd
# from ace_tools import display_dataframe_to_user
from collections import deque
import math

# 1. 그래프 불러오기 및 가중치 설정
G = nx.read_graphml(r'C:\Users\USER\PycharmProjects\dsa_team_proj\data\graph\all_subway_network.graphml')
# 설정된 가중치가 없을 경우 기본 weight=1
for u, v, data in G.edges(data=True):
    data.setdefault('weight', 1.0)

nodes = list(G.nodes())
n_pairs = 1000

# 2. 좌표 정보 추출 (node attribute keys 중 숫자로 변환 가능한 두 키 찾기)
sample_attrs = next(iter(G.nodes(data=True)))[1]
# 가능한 coordinate keys
coord_keys = [k for k, v in sample_attrs.items() if isinstance(v, (int, float, str))]
# 시도: 'x','y' 또는 'latitude','longitude' 있는지 확인
if 'x' in sample_attrs and 'y' in sample_attrs:
    x_key, y_key = 'x', 'y'
elif 'longitude' in sample_attrs and 'latitude' in sample_attrs:
    x_key, y_key = 'longitude', 'latitude'
else:
    # fallback: 첫 두 numeric-like keys
    x_key, y_key = coord_keys[0], coord_keys[1]

coords = {n: (float(G.nodes[n][x_key]), float(G.nodes[n][y_key])) for n in nodes}

# 최대 edge 간 유클리디언 거리 계산 (heuristic scaling용)
max_edge_len = max(math.dist(coords[u], coords[v]) for u, v in G.edges())

# 랜덤 쿼리 페어 생성
pairs = []
while len(pairs) < n_pairs:
    s, e = random.choice(nodes), random.choice(nodes)
    if s != e:
        pairs.append((s, e))

# 각 방법에 대한 성능 측정
results = []

# 1) BFS per query (unweighted)
def bfs_path(pair):
    return nx.shortest_path(G, pair[0], pair[1])

start = time.perf_counter()
for pair in pairs:
    bfs_path(pair)
mid = time.perf_counter()
bfs_time = (mid - start)
results.append(("BFS per query", 0.0, bfs_time, 0.0 + bfs_time))

# 2) Dijkstra per query
def dijkstra_path(pair):
    return nx.shortest_path(G, pair[0], pair[1], weight='weight')

start = time.perf_counter()
for pair in pairs:
    dijkstra_path(pair)
mid = time.perf_counter()
dij_time = (mid - start)
results.append(("Dijkstra per query", 0.0, dij_time, dij_time))

# 3) Bidirectional Dijkstra per query
def bidi_path(pair):
    return nx.bidirectional_dijkstra(G, pair[0], pair[1], weight='weight')[1]

start = time.perf_counter()
for pair in pairs:
    bidi_path(pair)
mid = time.perf_counter()
bidi_time = (mid - start)
results.append(("Bidirectional Dijkstra", 0.0, bidi_time, bidi_time))

# 4) A* per query
def heuristic(u, v):
    return math.dist(coords[u], coords[v]) / max_edge_len

def astar_path(pair):
    return nx.astar_path(G, pair[0], pair[1], heuristic=heuristic, weight='weight')

start = time.perf_counter()
for pair in pairs:
    astar_path(pair)
mid = time.perf_counter()
astar_time = (mid - start)
results.append(("A* per query", 0.0, astar_time, astar_time))

# 5) APSP via repeated BFS (pred)
start_prep = time.perf_counter()
pred = {}
for u in nodes:
    dd = {u: None}
    dist = {u: 0}
    dq = deque([u])
    while dq:
        x = dq.popleft()
        for nbr in G[x]:
            if nbr not in dist:
                dist[nbr] = dist[x] + 1
                dd[nbr] = x
                dq.append(nbr)
    pred[u] = dd
prep_bfs = time.perf_counter() - start_prep

def pred_path(pair):
    s, e = pair
    path = []
    cur = e
    while cur != s:
        path.append(cur)
        cur = pred[s][cur]
    path.append(s)
    return list(reversed(path))

start = time.perf_counter()
for pair in pairs:
    pred_path(pair)
mid = time.perf_counter()
pred_time = (mid - start)
results.append(("APSP via repeated BFS", prep_bfs, pred_time, prep_bfs + pred_time))

# 6) APSP via all_pairs_dijkstra_path
start_prep = time.perf_counter()
paths = dict(nx.all_pairs_dijkstra_path(G, weight='weight'))
prep_apsp = time.perf_counter() - start_prep

def apsp_path(pair):
    s, e = pair
    return paths[s][e]

start = time.perf_counter()
for pair in pairs:
    apsp_path(pair)
mid = time.perf_counter()
apsp_time = (mid - start)
results.append(("APSP via all_pairs_dijkstra", prep_apsp, apsp_time, prep_apsp + apsp_time))

# 7) APSP via Floyd-Warshall
start_prep = time.perf_counter()
predecessor, distance = nx.floyd_warshall_predecessor_and_distance(G, weight='weight')
prep_fw = time.perf_counter() - start_prep

def fw_path(pair):
    s, e = pair
    # 경로 복원
    path = [e]
    while path[0] != s:
        path.insert(0, predecessor[s][path[0]])
    return path

start = time.perf_counter()
for pair in pairs:
    fw_path(pair)
mid = time.perf_counter()
fw_time = (mid - start)
results.append(("APSP via Floyd-Warshall", prep_fw, fw_time, prep_fw + fw_time))

# 4. 결과 정리 및 표시
df = pd.DataFrame(results, columns=["Method", "Precompute Time (s)", "Total Query Time (s)", "Total Time (s)"])
# display_dataframe_to_user("좌표 정보 포함 지하철 최단경로 비교", df)
df.to_csv('subway_shortest_path_comparison.csv', index=False)

# Method	Precompute Time (s)	Total Query Time (s)	Total Time (s)
# BFS per query	0	0.0648178	0.0648178
# Dijkstra per query	0	0.16484489999857033	0.16484489999857033
# Bidirectional Dijkstra	0	0.15272850000110338	0.15272850000110338
# A* per query	0	0.17020810000030906	0.17020810000030906
# APSP via repeated BFS	0.0841325	0.0041747	0.0883072
# APSP via all_pairs_dijkstra	0.19204549999994924	0.000762	0.1928075
# APSP via Floyd-Warshall	2.472860400001082	0.0047274	2.4775878000036755
