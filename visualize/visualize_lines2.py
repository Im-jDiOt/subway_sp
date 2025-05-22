import matplotlib.pyplot as plt
import networkx as nx

plt.rcParams['font.family'] = 'Malgun Gothic'

lines = {
    1: "소요산 - 동두천 - 보산 - 동두천중앙 - 지행 - 덕정 - 덕계 - 양주 - 녹양 - 가능 - 의정부 - 회룡 - 망월사 - 도봉산 - 도봉 - 방학 - 창동 - 녹천 - 월계 - 성북 - 석계 - 신이문 - 외대앞 - 회기 - 청량리 - 제기동 - 신설동 - 동묘앞 - 동대문 - 종로5가 - 종로3가 - 종각 - 시청 - 서울역 - 남영 - 용산 - 노량진 - 대방 - 신길 - 영등포 - 신도림 - 구로 - 구일 - 개봉 - 오류동 - 온수 - 역곡 - 소사 - 부천 - 중동 - 송내 - 부개 - 부평 - 백운 - 동암 - 간석 - 주안 - 도화 - 제물포 - 도원 - 동인천 - 인천 - 광명 - 가산디지털단지 - 독산 - 금천구청 - 석수 - 관악 - 안양 - 명학 - 금정 - 군포 - 당정 - 의왕 - 성균관대 - 화서 - 수원 - 세류 - 병점 - 세마 - 오산대 - 오산 - 진위 - 송탄 - 서정리 - 지제 - 평택 - 성환 - 직산 - 두정 - 천안 - 봉명 - 쌍용 - 아산 - 배방 - 온양온천 - 신창 - 서동탄",
    2: "시청 - 을지로입구 - 을지로3가 - 을지로4가 - 동대문역사문화공원 - 신당 - 상왕십리 - 왕십리 - 한양대 - 뚝섬 - 성수 - 건대입구 - 구의 - 강변 - 잠실나루 - 잠실 - 신천 - 종합운동장 - 삼성 - 선릉 - 역삼 - 강남 - 교대 - 서초 - 방배 - 사당 - 낙성대 - 서울대입구 - 봉천 - 신림 - 신대방 - 구로디지털단지 - 대림 - 신도림 - 문래 - 영등포구청 - 당산 - 합정 - 홍대입구 - 신촌 - 이대 - 아현 - 충정로 - 시청",
    3: "대화 - 주엽 - 정발산 - 마두 - 백석 - 대곡 - 화정 - 원당 - 삼송 - 지축 - 구파발 - 연신내 - 불광 - 녹번 - 홍제 - 무악재 - 독립문 - 경복궁 - 안국 - 종로3가 - 을지로3가 - 충무로 - 동대입구 - 약수 - 금호 - 옥수 - 압구정 - 신사 - 잠원 - 고속터미널 - 교대 - 남부터미널 - 양재 - 매봉 - 도곡 - 대치 - 학여울 - 대청 - 일원 - 수서 - 가락시장 - 경찰병원 - 오금",
    4: "진접 - 오남 - 별내별가람 - 당고개 - 상계 - 노원 - 창동 - 쌍문 - 수유 - 미아 - 미아삼거리 - 길음 - 성신여대입구 - 한성대입구 - 혜화 - 동대문 - 동대문역사문화공원 - 충무로 - 명동 - 회현 - 서울역 - 숙대입구 - 삼각지 - 신용산 - 이촌 - 동작 - 이수 - 사당 - 남태령 - 선바위 - 경마공원 - 대공원 - 과천 - 정부과천청사 - 인덕원 - 평촌 - 범계 - 금정 - 산본 - 수리산 - 대야미 - 반월 - 상록수 - 한대앞 - 중앙 - 고잔 - 공단 - 안산 - 신길온천 - 정왕 - 오이도",
    5: "방화 - 개화산 - 김포공항 - 송정 - 마곡 - 발산 - 우장산 - 화곡 - 까치산 - 신정 - 목동 - 오목교 - 양평 - 영등포구청 - 영등포시장 - 신길 - 여의도 - 여의나루 - 마포 - 공덕 - 애오개 - 충정로 - 서대문 - 광화문 - 종로3가 - 을지로4가 - 동대문역사문화공원 - 청구 - 신금호 - 행당 - 왕십리 - 마장 - 답십리 - 장한평 - 군자 - 아차산 - 광나루 - 천호 - 강동 - 길동 - 굽은다리 - 명일 - 고덕 - 상일동 - 둔촌동 - 올림픽공원 - 방이 - 오금 - 개롱 - 거여 - 마천"
}

line_colors = {
    1: 'blue',
    2: 'green',
    3: 'orange',
    4: 'red',
    5: 'purple'
}

G = nx.Graph()
edges_by_line = {line: [] for line in lines}

# station_nodes: 기본 역명과 관련된 (역명_호선) 리스트 저장
station_nodes = {}

# 각 호선 별로 (역명_호선) 형태의 노드를 생성하고 연속역 간 간선 추가
for line, station_str in lines.items():
    station_list = [s.strip() for s in station_str.split('-')]
    # 각 역을 개별 노드로 생성
    nodes = [f"{station}_{line}" for station in station_list]
    for station, node in zip(station_list, nodes):
        station_nodes.setdefault(station, []).append(node)
    for i in range(len(nodes)-1):
        G.add_edge(nodes[i], nodes[i+1], weight=2, line=line)
        edges_by_line[line].append((nodes[i], nodes[i+1]))

# 동일 역명의 서로 다른 호선들 사이에 환승 간선 추가 (가중치 2)
transfer_edges = []
for station, node_list in station_nodes.items():
    if len(node_list) > 1:
        for i in range(len(node_list)):
            for j in range(i+1, len(node_list)):
                G.add_edge(node_list[i], node_list[j], weight=2, transfer=True)
                transfer_edges.append((node_list[i], node_list[j]))

pos = nx.kamada_kawai_layout(G)

plt.figure(figsize=(20,20))

# 각 호선의 간선 그리기
for line, edges in edges_by_line.items():
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=line_colors[line], width=2)

# 환승 간선은 검은색 점선으로 그리기
nx.draw_networkx_edges(G, pos, edgelist=transfer_edges, edge_color='black', style='dashed', width=1)

# 노드 색상: 환승 노드는 gold, 일반 노드는 lightgray
transfer_nodes = {node for nodes in station_nodes.values() if len(nodes) > 1 for node in nodes}
node_colors = ['gold' if node in transfer_nodes else 'lightgray' for node in G.nodes()]
node_sizes = [80 if node in transfer_nodes else 20 for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)

# 노드 라벨은 원래 역명과 호선 번호를 표시
labels = {node: node for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_family='Malgun Gothic')

# 범례 추가
for line in range(1, 6):
    plt.plot([], [], color=line_colors[line], label=f"{line}\\호선", linewidth=4)
plt.plot([], [], color='black', linestyle='dashed', label="환승", linewidth=1)
plt.legend(title="노선", loc="lower left", fontsize=10)

plt.title("서울 지하철 1~5호선 위상도 (호선별 분리 및 환승 간선 추가)", fontsize=18)
plt.axis("off")
plt.tight_layout()
plt.show()