import networkx as nx
import time
import random
import math
from collections import defaultdict

# ——————————————————————————————————————————————
# 1. 그래프 로드
# ——————————————————————————————————————————————
G = nx.read_graphml(r'C:\Users\USER\PycharmProjects\dsa_team_proj\data\graph\all_subway_network.graphml')
TG = nx.read_graphml(r'C:\Users\USER\PycharmProjects\dsa_team_proj\data\graph\transfer_subway_network.graphml')
transfer_nodes = set(TG.nodes())

# ——————————————————————————————————————————————
# 2. 각 노선별 역 순서 추출
# ——————————————————————————————————————————————
lines = defaultdict(list)
for u, v, data in G.edges(data=True):
    line = data.get('line')
    if line:
        lines[line].append((u, v))

def order_line_stations(edges):
    # (1) 인접 리스트 구성
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    # (2) 출발점: degree=1인 역(종점) 혹은 임의 노드
    ends = [n for n, nbrs in adj.items() if len(nbrs)==1]
    start = ends[0] if ends else edges[0][0]
    # (3) 단방향 순회
    seq = [start]
    prev = None
    while True:
        nxt = [w for w in adj[seq[-1]] if w!=prev]
        if not nxt: break
        prev = seq[-1]
        seq.append(nxt[0])
    return seq

line_seqs = {ln: order_line_stations(ed) for ln, ed in lines.items()}

# ——————————————————————————————————————————————
# 3. 환승역 그래프 구축 (Transfer Graph)
# ——————————————————————————————————————————————
TG2 = nx.Graph()
for seq in line_seqs.values():
    last_t, dist = None, 0
    for st in seq:
        if st in transfer_nodes:
            if last_t is None:
                TG2.add_node(st)
            else:
                TG2.add_node(st)
                TG2.add_edge(last_t, st, weight=dist)
            last_t = st
            dist = 0
        dist += 1

# ——————————————————————————————————————————————
# 4. 환승역 APSP 전처리
# ——————————————————————————————————————————————
# dist_transfers[X][Y] = X→Y 최단 정거장 수
dist_transfers = dict(nx.all_pairs_dijkstra_path_length(TG2, weight='weight'))

# ——————————————————————————————————————————————
# 5. 각 역 → 인접 환승역 거리 맵핑
# ——————————————————————————————————————————————
station_to_transfers = {n: [] for n in G.nodes()}
for seq in line_seqs.values():
    t_idx = [i for i, st in enumerate(seq) if st in transfer_nodes]
    for i, st in enumerate(seq):
        # 자신이 환승역이면 (거리0)
        if st in transfer_nodes:
            station_to_transfers[st].append((st, 0))
        # 가까운 환승역들(스캔)
        for ti in t_idx:
            d = abs(ti - i)
            station_to_transfers[st].append((seq[ti], d))
# 중복 제거: 같은 환승역에 대해 최소 거리만 남김
for st, lst in station_to_transfers.items():
    best = {}
    for t, d in lst:
        if t not in best or d < best[t]:
            best[t] = d
    station_to_transfers[st] = list(best.items())

# ——————————————————————————————————————————————
# 6. 테스트용 1000개 랜덤 쿼리 생성
# ——————————————————————————————————————————————
nodes = list(G.nodes())
pairs = []
while len(pairs) < 1000:
    a, b = random.choice(nodes), random.choice(nodes)
    if a != b:
        pairs.append((a, b))

# ——————————————————————————————————————————————
# 7. Baseline: BFS per query
# ——————————————————————————————————————————————
def bfs_dist(pair):
    return nx.shortest_path_length(G, pair[0], pair[1])

t0 = time.perf_counter()
for p in pairs:
    bfs_dist(p)
t1 = time.perf_counter()
bfs_total = t1 - t0

# ——————————————————————————————————————————————
# 8. Two-layer Transfer 방식 (거리만 계산)
# ——————————————————————————————————————————————
def two_layer_dist(s, t):
    if s == t:
        return 0
    best = math.inf
    for (x, dx) in station_to_transfers[s]:
        for (y, dy) in station_to_transfers[t]:
            # 환승역 간 최단 거리
            dxy = dist_transfers.get(x, {}).get(y, math.inf)
            cand = dx + dxy + dy
            if cand < best:
                best = cand
    return best

# 측정
t0 = time.perf_counter()
for p in pairs:
    two_layer_dist(*p)
t1 = time.perf_counter()
two_total = t1 - t0

# ——————————————————————————————————————————————
# 9. 결과 정리
# ——————————————————————————————————————————————
import pandas as pd
df = pd.DataFrame([
    ['BFS per query', 0.0, bfs_total, bfs_total],
    ['Two-layer Transfer', 0.0, two_total, two_total]
], columns=['Method','Precompute Time (s)','Total Query Time (s)','Total Time (s)'])

df.to_csv('subway_shortest_path_comparison2.csv', index=False)

# Method	            Precompute Time (s)	    Total Query Time (s)	        Total Time (s)
# built-in sp algo	    0	                            0.034331200004089624	    0.034331200004089624
# Two-layer Transfer	0	                            0.0001218	                    0.0001218
