# Fix two_layer_path: fallback if no transfer combination
import networkx as nx
import time
import random
import math
from collections import defaultdict

# TODO 필요시 graphml 파일을 불러와서 하는 게 아니라 과제에서 주어진 정보에서 시작할 수 있도록 수정
G = nx.read_graphml(r'C:\Users\USER\PycharmProjects\dsa_team_proj\data\graph\all_subway_network.graphml')
TG = nx.read_graphml(r'C:\Users\USER\PycharmProjects\dsa_team_proj\data\graph\transfer_subway_network.graphml')
transfer_nodes = set(TG.nodes())

# Reconstruct necessary precomputations quickly (abbreviated)

# TODO jupyter 수정본으로 수정할 것
lines = defaultdict(list)
for u, v, data in G.edges(data=True):
    line = data.get('line')
    if line: lines[line].append((u,v))

#TODO 이거 없어도 되는 거 아님??
def order_line_stations(edges):
    adj = defaultdict(list)
    for u,v in edges:
        adj[u].append(v); adj[v].append(u)
    ends = [n for n, nbrs in adj.items() if len(nbrs)==1]
    start = ends[0] if ends else edges[0][0]
    seq=[start]; prev=None
    while True:
        nxt=[w for w in adj[seq[-1]] if w!=prev]
        if not nxt: break
        prev=seq[-1]; seq.append(nxt[0])
    return seq
line_sequences = {ln: order_line_stations(ed) for ln,ed in lines.items()}

# TG2 = nx.Graph()
# for seq in line_sequences.values():
#     last_t,dist=None,0
#     for st in seq:
#         if st in transfer_nodes:
#             if last_t: TG2.add_edge(last_t,st,weight=dist)
#             else: TG2.add_node(st)
#             last_t,dist=st,0
#         dist+=1

dist_transfers = dict(nx.all_pairs_dijkstra_path_length(TG, weight='weight'))
path_transfers = dict(nx.all_pairs_dijkstra_path(TG, weight='weight'))

station_to_transfers = {n:[] for n in G.nodes()}
station_lines = defaultdict(list)
for ln,seq in line_sequences.items():
    for st in seq:
        station_lines[st].append(ln)
    t_idx=[i for i,s in enumerate(seq) if s in transfer_nodes]
    for i,s in enumerate(seq):
        if s in transfer_nodes: station_to_transfers[s].append((s,0))
        for ti in t_idx:
            station_to_transfers[s].append((seq[ti], abs(ti-i)))
for s,lst in station_to_transfers.items():
    best={}
    for t,d in lst:
        if t not in best or d<best[t]: best[t]=d
    station_to_transfers[s]=list(best.items())

# path functions
def bfs_path(pair):
    return nx.shortest_path(G, pair[0], pair[1])

def two_layer_path(s, t):
    if s == t: return [s] # 동일역
    # 동일 호선이면 해당 호선으로 직행이 가장 빠르다고 가정하는데, 아닐 거 같음. 보류.
    # common = set(station_lines[s]) & set(station_lines[t])
    # if common:
    #     ln = next(iter(common)); seq=line_sequences[ln]
    #     i_s, i_t = seq.index(s), seq.index(t)
    #     step = 1 if i_t>i_s else -1
    #     return seq[i_s:i_t+step:step]
    best, bp = math.inf, None
    for x, dx in station_to_transfers.get(s,[]):
        for y, dy in station_to_transfers.get(t,[]):
            dxy = dist_transfers.get(x,{}).get(y, math.inf)
            total = dx + dxy + dy
            if total < best:
                best, bp = total, (x, y)
    if bp is None:
        return nx.shortest_path(G, s, t)  # fallback
    x, y = bp
    # s->x
    ln_s = next(ln for ln in station_lines[s] if ln in station_lines[x])
    seq_s = line_sequences[ln_s]
    i_s, i_x = seq_s.index(s), seq_s.index(x)
    step_s = 1 if i_x>i_s else -1
    path_sx = seq_s[i_s:i_x+step_s:step_s]
    # x->y
    trans_path = path_transfers[x][y]
    # y->t
    ln_t = next(ln for ln in station_lines[t] if ln in station_lines[y])
    seq_t = line_sequences[ln_t]
    i_y, i_t = seq_t.index(y), seq_t.index(t)
    step_t = 1 if i_t>i_y else -1
    path_yt = seq_t[i_y:i_t+step_t:step_t]
    # combine
    return path_sx + trans_path[1:] + path_yt[1:]

# 5 test pairs
nodes=list(G.nodes())
pairs=[]
while len(pairs)<5:
    a,b=random.choice(nodes),random.choice(nodes)
    if a!=b: pairs.append((a,b))

import pandas as pd
results=[]
for s,t in pairs:
    results.append({
        'Source': s,
        'Target': t,
        'BFS Path': bfs_path((s,t)),
        'Two-layer Path': two_layer_path(s,t)
    })
df=pd.DataFrame(results)
df.to_csv('test_pairs.csv', index=False)
# from ace_tools import display_dataframe_to_user
# display_dataframe_to_user("Paths for 5 Test Pairs", df)
