import networkx as nx
import time
import random
import math
import pandas as pd
from collections import defaultdict
# from ace_tools import display_dataframe_to_user

# Load full graph
G = nx.read_graphml(r'C:\Users\USER\PycharmProjects\dsa_team_proj\data\graph\all_subway_network.graphml')
TG = nx.read_graphml(r'C:\Users\USER\PycharmProjects\dsa_team_proj\data\graph\transfer_subway_network.graphml')
transfer_nodes = set(TG.nodes())

# Baseline BFS per query test pairs
nodes = list(G.nodes())
pairs = []
while len(pairs) < 1000:
    s, t = random.choice(nodes), random.choice(nodes)
    if s != t:
        pairs.append((s, t))

# Measure BFS per query
start_bfs = time.perf_counter()
for s, t in pairs:
    nx.shortest_path_length(G, s, t)
end_bfs = time.perf_counter()
bfs_query_time = end_bfs - start_bfs

# Two-layer precompute timing
start_pre = time.perf_counter()

# 1. Extract lines and order sequences
lines = defaultdict(list)
for u, v, data in G.edges(data=True):
    line = data.get('line')
    if line:
        lines[line].append((u, v))

def order_line_stations(edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    ends = [n for n, nbrs in adj.items() if len(nbrs) == 1]
    start = ends[0] if ends else edges[0][0]
    seq = [start]
    prev = None
    while True:
        nxt = [w for w in adj[seq[-1]] if w != prev]
        if not nxt:
            break
        prev = seq[-1]
        seq.append(nxt[0])
    return seq

line_sequences = {ln: order_line_stations(ed) for ln, ed in lines.items()}

# 2. Build transfer graph
TG2 = nx.Graph()
for seq in line_sequences.values():
    last_t, dist = None, 0
    for st in seq:
        if st in transfer_nodes:
            if last_t is None:
                TG2.add_node(st)
            else:
                TG2.add_edge(last_t, st, weight=dist)
            last_t, dist = st, 0
        dist += 1

# 3. APSP on transfer graph
dist_transfers = dict(nx.all_pairs_dijkstra_path_length(TG2, weight='weight'))
path_transfers = dict(nx.all_pairs_dijkstra_path(TG2, weight='weight'))

# 4. Station to transfer mapping
station_to_transfers = {n: [] for n in G.nodes()}
station_lines = defaultdict(list)
for ln, seq in line_sequences.items():
    for st in seq:
        station_lines[st].append(ln)
    t_idx = [i for i, s in enumerate(seq) if s in transfer_nodes]
    for i, s in enumerate(seq):
        if s in transfer_nodes:
            station_to_transfers[s].append((s, 0))
        for ti in t_idx:
            station_to_transfers[s].append((seq[ti], abs(ti - i)))
for s, lst in station_to_transfers.items():
    best = {}
    for t_node, d in lst:
        if t_node not in best or d < best[t_node]:
            best[t_node] = d
    station_to_transfers[s] = list(best.items())

end_pre = time.perf_counter()
precompute_time = end_pre - start_pre

# 5. Measure two-layer query time
def two_layer_dist(s, t):
    if s == t:
        return 0
    best = math.inf
    for x, dx in station_to_transfers[s]:
        for y, dy in station_to_transfers[t]:
            dxy = dist_transfers.get(x, {}).get(y, math.inf)
            total = dx + dxy + dy
            if total < best:
                best = total
    return best

start_tl = time.perf_counter()
for s, t in pairs:
    two_layer_dist(s, t)
end_tl = time.perf_counter()
two_layer_query_time = end_tl - start_tl

# 6. Summarize results
df = pd.DataFrame([
    ['BFS per query', 0.0, bfs_query_time, bfs_query_time],
    ['Two-layer Transfer', precompute_time, two_layer_query_time, precompute_time + two_layer_query_time]
], columns=['Method','Precompute Time (s)','Query Time (s)','Total Time (s)'])

df.to_csv('performance_comparison.csv', index=False)
# display_dataframe_to_user("Performance Comparison (1000 Queries)", df)

# Method                       Precompute Time (s)              Query Time (s)                     Total Time (s)
# built in sp algo               0.0                                    0.030184499999450054         0.030184499999450054
# Two-layer Transfer           0.00042799999937415123      0.00011219999578315765      0.0005401999951573089



