from typing import List, Any, Tuple

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from itertools import combinations, chain

lines = {
    1: "소요산 - 동두천 - 보산 - 동두천중앙 - 지행 - 덕정 - 덕계 - 양주 - 녹양 - 가능 - 의정부 - 회룡 - 망월사 - 도봉산 - 도봉 - 방학 - 창동 - 녹천 - 월계 - 성북 - 석계 - 신이문 - 외대앞 - 회기 - 청량리 - 제기동 - 신설동 - 동묘앞 - 동대문 - 종로5가 - 종로3가 - 종각 - 시청 - 서울역 - 남영 - 용산 - 노량진 - 대방 - 신길 - 영등포 - 신도림 - 구로 - 구일 - 개봉 - 오류동 - 온수 - 역곡 - 소사 - 부천 - 중동 - 송내 - 부개 - 부평 - 백운 - 동암 - 간석 - 주안 - 도화 - 제물포 - 도원 - 동인천 - 인천 - 광명 - 가산디지털단지 - 독산 - 금천구청 - 석수 - 관악 - 안양 - 명학 - 금정 - 군포 - 당정 - 의왕 - 성균관대 - 화서 - 수원 - 세류 - 병점 - 세마 - 오산대 - 오산 - 진위 - 송탄 - 서정리 - 지제 - 평택 - 성환 - 직산 - 두정 - 천안 - 봉명 - 쌍용 - 아산 - 배방 - 온양온천 - 신창 - 서동탄",
    2: "시청 - 을지로입구 - 을지로3가 - 을지로4가 - 동대문역사문화공원 - 신당 - 상왕십리 - 왕십리 - 한양대 - 뚝섬 - 성수 - 건대입구 - 구의 - 강변 - 잠실나루 - 잠실 - 신천 - 종합운동장 - 삼성 - 선릉 - 역삼 - 강남 - 교대 - 서초 - 방배 - 사당 - 낙성대 - 서울대입구 - 봉천 - 신림 - 신대방 - 구로디지털단지 - 대림 - 신도림 - 문래 - 영등포구청 - 당산 - 합정 - 홍대입구 - 신촌 - 이대 - 아현 - 충정로 - 시청",
    3: "대화 - 주엽 - 정발산 - 마두 - 백석 - 대곡 - 화정 - 원당 - 삼송 - 지축 - 구파발 - 연신내 - 불광 - 녹번 - 홍제 - 무악재 - 독립문 - 경복궁 - 안국 - 종로3가 - 을지로3가 - 충무로 - 동대입구 - 약수 - 금호 - 옥수 - 압구정 - 신사 - 잠원 - 고속터미널 - 교대 - 남부터미널 - 양재 - 매봉 - 도곡 - 대치 - 학여울 - 대청 - 일원 - 수서 - 가락시장 - 경찰병원 - 오금",
    4: "진접 - 오남 - 별내별가람 - 당고개 - 상계 - 노원 - 창동 - 쌍문 - 수유 - 미아 - 미아삼거리 - 길음 - 성신여대입구 - 한성대입구 - 혜화 - 동대문 - 동대문역사문화공원 - 충무로 - 명동 - 회현 - 서울역 - 숙대입구 - 삼각지 - 신용산 - 이촌 - 동작 - 이수 - 사당 - 남태령 - 선바위 - 경마공원 - 대공원 - 과천 - 정부과천청사 - 인덕원 - 평촌 - 범계 - 금정 - 산본 - 수리산 - 대야미 - 반월 - 상록수 - 한대앞 - 중앙 - 고잔 - 공단 - 안산 - 신길온천 - 정왕 - 오이도",
    5: "방화 - 개화산 - 김포공항 - 송정 - 마곡 - 발산 - 우장산 - 화곡 - 까치산 - 신정 - 목동 - 오목교 - 양평 - 영등포구청 - 영등포시장 - 신길 - 여의도 - 여의나루 - 마포 - 공덕 - 애오개 - 충정로 - 서대문 - 광화문 - 종로3가 - 을지로4가 - 동대문역사문화공원 - 청구 - 신금호 - 행당 - 왕십리 - 마장 - 답십리 - 장한평 - 군자 - 아차산 - 광나루 - 천호 - 강동 - 길동 - 굽은다리 - 명일 - 고덕 - 상일동 - 둔촌동 - 올림픽공원 - 방이 - 오금 - 개롱 - 거여 - 마천"
}

# 2호선이 순환노선이라 시점과 종점역을 구분하기 위함.
line_seq = dict()
for line, station_str in lines.items():
    names = [s.strip() for s in station_str.split('-')]
    line_seq[line] = names
line_seq[2][-1] += '(종점)'

# G에 호선별로 노드 및 간선 추가
G=nx.Graph()
g_idx = 0
station_idx = dict() # (line, name):global_idx / g_idx -> 인접 환승역 빠른 계산
for line, seq in line_seq.items():
    prev = None
    for l_idx, name in enumerate(seq):
        curr = (line, name)
        G.add_node(curr, global_idx = g_idx, local_idx=l_idx, line=line)
        station_idx[curr] = g_idx

        if prev:
            G.add_edge(prev, curr, weight=2)
        g_idx += 1
        prev = curr

# 환승역 감지용
station_lines = defaultdict(list)
for line, seq in line_seq.items():
    for name in seq:
        station_lines[name].append(line)

# G에 환승 기능 구현
transfer_nodes = []
for station, lines in station_lines.items():
    if len(lines)>1:
        transfer_nodes.append([(line, station) for line in lines])
        for u,v in combinations(transfer_nodes[-1], 2):
            G.add_edge(u,v,weight=2)

G.add_edge((2, '시청'), (2, '시청(종점)'), weight=0.0000001) # 가중치 0 불가.. 이후 시간 계산할 때 소수점 자르기..

# #G 시각화 -> 환승, 2호선 순환 등이 잘 구현 되어있음을 확인함.
# pos = nx.kamada_kawai_layout(G)
# line_colors = {
#     1: 'blue',
#     2: 'green',
#     3: 'orange',
#     4: 'red',
#     5: 'purple'
# }
#
# for node, (x, y) in pos.items():
#     G.nodes[node]['x'] = x
#     G.nodes[node]['y'] = y
# plt.figure(figsize=(10, 10))
#
# # 노드, 간선, 레이블 그리기
# node_colors = [line_colors[G.nodes[n]['line']] for n in G.nodes()]
# nx.draw_networkx_nodes(G, pos, node_color='gray', node_size=10)
#
# edge_colors = []
# for u, v in G.edges():
#     if G.nodes[u]['line'] == G.nodes[v]['line']:
#         color = line_colors[G.nodes[u]['line']]
#     else:
#         color = 'gray'
#     edge_colors.append(color)
#
# nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)
#
# # 노드 레이블
# nx.draw_networkx_labels(G, pos, font_family='Malgun Gothic', font_size=8)
#
# # 간선 가중치 표시
# # edge_labels = nx.get_edge_attributes(G, 'weight')
# # nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7)
#
# plt.axis('off')
# plt.tight_layout()
# plt.show()

# TODO
# TG에 들어갈 노드들. 환승역과 시종점.
line_transfer_idx = defaultdict(list)
transfer_gidx = []
for line, name in list(chain.from_iterable(transfer_nodes)):
    line_transfer_idx[line].append((name, station_idx[(line, name)])) # line: [(name, global_idx), ...]
    transfer_gidx.append(station_idx[(line, name)])


end_gidx = [] # global idxes for end stations
for line, seq in line_seq.items():
    for l_idx, name in enumerate(seq):
        if l_idx==0 or l_idx==len(seq)-1:
            line_transfer_idx[line].append((name, station_idx[(line, name)]))
            end_gidx.append(station_idx[(line, name)])

# 호선별로 노드 및 간선 추가
TG = nx.Graph()
for line, transfer_idx in line_transfer_idx.items():
    transfer_idx.sort(key=lambda x: x[1])
    for i in range(len(transfer_idx) - 1):
        name1, idx1 = transfer_idx[i]
        name2, idx2 = transfer_idx[i + 1]

        weight = 2 * (idx2 - idx1)
        u = (line, name1)
        v = (line, name2)

        TG.add_node(u, global_idx=idx1, line=line)
        TG.add_node(v, global_idx=idx2, line=line)
        TG.add_edge(u, v, weight=weight)

for i in range(len(transfer_nodes)):
    for u,v in combinations(transfer_nodes[i], 2):
        TG.add_edge(u,v,weight=2)

TG.add_edge((2, '시청'), (2, '시청(종점)'), weight=0.0000001)
# #G 시각화 -> 환승, 2호선 순환 등이 잘 구현 되어있음을 확인함.
# pos = nx.kamada_kawai_layout(TG)
# line_colors = {
#     1: 'blue',
#     2: 'green',
#     3: 'orange',
#     4: 'red',
#     5: 'purple'
# }
#
# for node, (x, y) in pos.items():
#     TG.nodes[node]['x'] = x
#     TG.nodes[node]['y'] = y
# plt.figure(figsize=(10, 10))
#
# # 노드, 간선, 레이블 그리기
# node_colors = [line_colors[TG.nodes[n]['line']] for n in TG.nodes()]
# nx.draw_networkx_nodes(TG, pos, node_color='gray', node_size=10)
#
# edge_colors = []
# for u, v in TG.edges():
#     if G.nodes[u]['line'] == TG.nodes[v]['line']:
#         color = line_colors[TG.nodes[u]['line']]
#     else:
#         color = 'gray'
#     edge_colors.append(color)
#
# nx.draw_networkx_edges(TG, pos, edge_color=edge_colors, width=2)
#
# # 노드 레이블
# nx.draw_networkx_labels(TG, pos, font_family='Malgun Gothic', font_size=8)
#
# # 간선 가중치 표시
# edge_labels = nx.get_edge_attributes(TG, 'weight')
# nx.draw_networkx_edge_labels(TG, pos, edge_labels, font_size=7)
#
# plt.axis('off')
# plt.tight_layout()
# plt.show()

gidx_transfer = {
    g_idx: (line, name)
    for line, item in line_transfer_idx.items()
    for name, g_idx in item
}

node_near_transfer = dict()
keys = sorted(gidx_transfer.keys())

for k1, k2 in zip(keys[:-1], keys[1:]):
    g_idx1, transfer_node1 = k1, gidx_transfer[k1]
    g_idx2, transfer_node2 = k2, gidx_transfer[k2]

    for i in range(g_idx1, g_idx2):
        if g_idx1 in end_gidx:
            node_near_transfer[i]  = (transfer_node2)
        elif g_idx2 in end_gidx:
            node_near_transfer[i]  = (transfer_node1)
        else: node_near_transfer[i] = (transfer_node1, transfer_node2)

node_near_transfer[99] = ((2, '시청'), (2, '을지로3가'))

def near_transfer(s, t):
    idx1 = station_idx[s]
    idx2 = station_idx[t]

    if idx1 in transfer_gidx: near_s = (s)
    else: near_s = node_near_transfer[idx1]

    if idx2 in transfer_gidx: near_t = (t)
    else: near_t = node_near_transfer[idx2]

    return [near_s, near_t]

# transfer to transfer APSP
t2t_dist = dict(nx.all_pairs_dijkstra_path_length(TG, wieght='weight'))
t2t_path = dict(nx.all_pairs_dijkstra_path(TG, wieght='weight'))

nodes_list = list(station_idx.keys())
def two_layer_sp(x,y) -> Tuple[List[Any], int]:
    if x == y: return [x], 0

    near_x, near_y = near_transfer(x,y)
    xi, yi = station_idx[x], station_idx[y]
    idx1, idx2, not_reverse = (xi, yi, 1) if xi < yi else (xi, yi, -1)
    if near_x == near_y: # 같은 subline 내에 두 역이 존재
        # path = list(G.subgraph(s,t).nodes())
        path = nodes_list[idx1:idx2+1]
        return path[::not_reverse], 2*(idx2 - idx1)
    else: # 두 역이 다른 subline에 존재
        # near_x와 near_y 안에 있는 환승역들 가능한 조합 케이스 다 돌면서 x2t+t2t+t2y 계산
        # 이 때 xt와 yt가 같다면 x2t+t2y가 되고
        # 그게 아닐 때 x2t+t2t+t2y가 됨을 고려.
        # 그리고 항상  x2t+t2y< x2t+t2t+t2y일 거라 단정지을 수 없으므로 가능한 케이스 중
        # best 만을 반환하도록 할 것. (매번 best 비교하여 업데이트하는 방식으로)
        # 말은 쉬운데 뭔가 코드 작성이 더러워져서 기분이 나쁨. 그냥 지금까지 쓴 코드 다 너무너무 더러움..
        # 빨리 대충 완성하고 리팩토링하고 싶다......
        return 0



