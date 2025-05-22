import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
from itertools import combinations

# 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'

# 호선별 역 데이터는 그대로 유지
lines = {
    1: "소요산 - 동두천 - 보산 - 동두천중앙 - 지행 - 덕정 - 덕계 - 양주 - 녹양 - 가능 - 의정부 - 회룡 - 망월사 - 도봉산 - 도봉 - 방학 - 창동 - 녹천 - 월계 - 성북 - 석계 - 신이문 - 외대앞 - 회기 - 청량리 - 제기동 - 신설동 - 동묘앞 - 동대문 - 종로5가 - 종로3가 - 종각 - 시청 - 서울역 - 남영 - 용산 - 노량진 - 대방 - 신길 - 영등포 - 신도림 - 구로 - 구일 - 개봉 - 오류동 - 온수 - 역곡 - 소사 - 부천 - 중동 - 송내 - 부개 - 부평 - 백운 - 동암 - 간석 - 주안 - 도화 - 제물포 - 도원 - 동인천 - 인천 - 광명 - 가산디지털단지 - 독산 - 금천구청 - 석수 - 관악 - 안양 - 명학 - 금정 - 군포 - 당정 - 의왕 - 성균관대 - 화서 - 수원 - 세류 - 병점 - 세마 - 오산대 - 오산 - 진위 - 송탄 - 서정리 - 지제 - 평택 - 성환 - 직산 - 두정 - 천안 - 봉명 - 쌍용 - 아산 - 배방 - 온양온천 - 신창 - 서동탄",
    2: "시청 - 을지로입구 - 을지로3가 - 을지로4가 - 동대문역사문화공원 - 신당 - 상왕십리 - 왕십리 - 한양대 - 뚝섬 - 성수 - 건대입구 - 구의 - 강변 - 잠실나루 - 잠실 - 신천 - 종합운동장 - 삼성 - 선릉 - 역삼 - 강남 - 교대 - 서초 - 방배 - 사당 - 낙성대 - 서울대입구 - 봉천 - 신림 - 신대방 - 구로디지털단지 - 대림 - 신도림 - 문래 - 영등포구청 - 당산 - 합정 - 홍대입구 - 신촌 - 이대 - 아현 - 충정로 - 시청",
    3: "대화 - 주엽 - 정발산 - 마두 - 백석 - 대곡 - 화정 - 원당 - 삼송 - 지축 - 구파발 - 연신내 - 불광 - 녹번 - 홍제 - 무악재 - 독립문 - 경복궁 - 안국 - 종로3가 - 을지로3가 - 충무로 - 동대입구 - 약수 - 금호 - 옥수 - 압구정 - 신사 - 잠원 - 고속터미널 - 교대 - 남부터미널 - 양재 - 매봉 - 도곡 - 대치 - 학여울 - 대청 - 일원 - 수서 - 가락시장 - 경찰병원 - 오금",
    4: "진접 - 오남 - 별내별가람 - 당고개 - 상계 - 노원 - 창동 - 쌍문 - 수유 - 미아 - 미아삼거리 - 길음 - 성신여대입구 - 한성대입구 - 혜화 - 동대문 - 동대문역사문화공원 - 충무로 - 명동 - 회현 - 서울역 - 숙대입구 - 삼각지 - 신용산 - 이촌 - 동작 - 이수 - 사당 - 남태령 - 선바위 - 경마공원 - 대공원 - 과천 - 정부과천청사 - 인덕원 - 평촌 - 범계 - 금정 - 산본 - 수리산 - 대야미 - 반월 - 상록수 - 한대앞 - 중앙 - 고잔 - 공단 - 안산 - 신길온천 - 정왕 - 오이도",
    5: "방화 - 개화산 - 김포공항 - 송정 - 마곡 - 발산 - 우장산 - 화곡 - 까치산 - 신정 - 목동 - 오목교 - 양평 - 영등포구청 - 영등포시장 - 신길 - 여의도 - 여의나루 - 마포 - 공덕 - 애오개 - 충정로 - 서대문 - 광화문 - 종로3가 - 을지로4가 - 동대문역사문화공원 - 청구 - 신금호 - 행당 - 왕십리 - 마장 - 답십리 - 장한평 - 군자 - 아차산 - 광나루 - 천호 - 강동 - 길동 - 굽은다리 - 명일 - 고덕 - 상일동 - 둔촌동 - 올림픽공원 - 방이 - 오금 - 개롱 - 거여 - 마천"
}

# 역별 호선 정보 구축 함수
def build_station_lines():
    station_lines = defaultdict(list)
    for line, station_str in lines.items():
        for station in [s.strip() for s in station_str.split('-')]:
            station_lines[station].append(line)
    return station_lines


# 네트워크 그래프 생성 함수
def build_transit_graph(station_lines):
    G_t = nx.Graph()

    # 각 호선별 환승역 및 시종점 인덱스 수집
    line_transfer_idx = {}
    for line, station_str in lines.items():
        stations = [s.strip() for s in station_str.split('-')]

        # 환승역과 시종점 찾기
        indices = []
        for idx, station in enumerate(stations):
            if len(station_lines[station]) > 1 or idx == 0 or idx == len(stations) - 1:
                indices.append((idx, station))

        # 중복 제거하면서 원래 순서 유지
        line_transfer_idx[line] = list(dict.fromkeys(indices))

    # 1. 동일 호선 내 환승역 간 간선 추가
    for line, items in line_transfer_idx.items():
        items.sort(key=lambda x: x[0])
        for i in range(len(items) - 1):
            idx1, station1 = items[i]
            idx2, station2 = items[i + 1]

            weight = 2 * (idx2 - idx1)
            u = f"({line},{station1})"
            v = f"({line},{station2})"

            # add_nodes_from으로 한 번에 노드 추가
            G_t.add_nodes_from([u, v])
            G_t.add_edge(u, v, weight=weight)

    # 2. 환승역 간 간선 추가 (호선 간 연결)
    for station, lines_list in station_lines.items():
        if len(lines_list) > 1:
            # 실제 그래프에 존재하는 노드만 필터링
            transfer_nodes = [f"({line},{station})" for line in lines_list
                              if f"({line},{station})" in G_t.nodes]

            # 모든 환승노드 쌍에 간선 추가
            if len(transfer_nodes) > 1:
                G_t.add_edges_from([(u, v, {'weight': 2})
                                    for u, v in combinations(transfer_nodes, 2)])

    return G_t


# 네트워크 시각화 함수
def visualize_network(G):
    pos = nx.kamada_kawai_layout(G)
    for node, (x, y) in pos.items():
        G_t.nodes[node]['x'] = x
        G_t.nodes[node]['y'] = y
    plt.figure(figsize=(10, 10))

    # 노드, 간선, 레이블 그리기
    nx.draw_networkx_nodes(G, pos, node_color='gold', node_size=80)
    nx.draw_networkx_edges(G, pos, edge_color='black', width=0.8)

    # 노드 레이블
    nx.draw_networkx_labels(G, pos, font_family='Malgun Gothic', font_size=8)

    # 간선 가중치 표시
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7)

    plt.axis('off')
    plt.tight_layout()
    plt.show()


# 메인 실행 로직
station_lines = build_station_lines()
G_t = build_transit_graph(station_lines)
visualize_network(G_t)
nx.write_graphml(G_t, "data/graph/transfer_subway_network.graphml")