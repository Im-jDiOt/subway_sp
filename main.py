import networkx as nx
from collections import defaultdict
from bisect import bisect_left
import matplotlib.pyplot as plt

# 0. 노선 정의 (기존과 동일)
lines = {
    1: "소요산 - 동두천 - 보산 - 동두천중앙 - 지행 - 덕정 - 덕계 - 양주 - 녹양 - 가능 - 의정부 - 회룡 - 망월사 - 도봉산 - 도봉 - 방학 - 창동 - 녹천 - 월계 - 성북 - 석계 - 신이문 - 외대앞 - 회기 - 청량리 - 제기동 - 신설동 - 동묘앞 - 동대문 - 종로5가 - 종로3가 - 종각 - 시청 - 서울역 - 남영 - 용산 - 노량진 - 대방 - 신길 - 영등포 - 신도림 - 구로 - 구일 - 개봉 - 오류동 - 온수 - 역곡 - 소사 - 부천 - 중동 - 송내 - 부개 - 부평 - 백운 - 동암 - 간석 - 주안 - 도화 - 제물포 - 도원 - 동인천 - 인천 - 광명 - 가산디지털단지 - 독산 - 금천구청 - 석수 - 관악 - 안양 - 명학 - 금정 - 군포 - 당정 - 의왕 - 성균관대 - 화서 - 수원 - 세류 - 병점 - 세마 - 오산대 - 오산 - 진위 - 송탄 - 서정리 - 지제 - 평택 - 성환 - 직산 - 두정 - 천안 - 봉명 - 쌍용 - 아산 - 배방 - 온양온천 - 신창 - 서동탄",
    2: "시청 - 을지로입구 - 을지로3가 - 을지로4가 - 동대문역사문화공원 - 신당 - 상왕십리 - 왕십리 - 한양대 - 뚝섬 - 성수 - 건대입구 - 구의 - 강변 - 잠실나루 - 잠실 - 신천 - 종합운동장 - 삼성 - 선릉 - 역삼 - 강남 - 교대 - 서초 - 방배 - 사당 - 낙성대 - 서울대입구 - 봉천 - 신림 - 신대방 - 구로디지털단지 - 대림 - 신도림 - 문래 - 영등포구청 - 당산 - 합정 - 홍대입구 - 신촌 - 이대 - 아현 - 충정로 - 시청",
    3: "대화 - 주엽 - 정발산 - 마두 - 백석 - 대곡 - 화정 - 원당 - 삼송 - 지축 - 구파발 - 연신내 - 불광 - 녹번 - 홍제 - 무악재 - 독립문 - 경복궁 - 안국 - 종로3가 - 을지로3가 - 충무로 - 동대입구 - 약수 - 금호 - 옥수 - 압구정 - 신사 - 잠원 - 고속터미널 - 교대 - 남부터미널 - 양재 - 매봉 - 도곡 - 대치 - 학여울 - 대청 - 일원 - 수서 - 가락시장 - 경찰병원 - 오금",
    4: "진접 - 오남 - 별내별가람 - 당고개 - 상계 - 노원 - 창동 - 쌍문 - 수유 - 미아 - 미아삼거리 - 길음 - 성신여대입구 - 한성대입구 - 혜화 - 동대문 - 동대문역사문화공원 - 충무로 - 명동 - 회현 - 서울역 - 숙대입구 - 삼각지 - 신용산 - 이촌 - 동작 - 이수 - 사당 - 남태령 - 선바위 - 경마공원 - 대공원 - 과천 - 정부과천청사 - 인덕원 - 평촌 - 범계 - 금정 - 산본 - 수리산 - 대야미 - 반월 - 상록수 - 한대앞 - 중앙 - 고잔 - 공단 - 안산 - 신길온천 - 정왕 - 오이도",
    5: "방화 - 개화산 - 김포공항 - 송정 - 마곡 - 발산 - 우장산 - 화곡 - 까치산 - 신정 - 목동 - 오목교 - 양평 - 영등포구청 - 영등포시장 - 신길 - 여의도 - 여의나루 - 마포 - 공덕 - 애오개 - 충정로 - 서대문 - 광화문 - 종로3가 - 을지로4가 - 동대문역사문화공원 - 청구 - 신금호 - 행당 - 왕십리 - 마장 - 답십리 - 장한평 - 군자 - 아차산 - 광나루 - 천호 - 강동 - 길동 - 굽은다리 - 명일 - 고덕 - 상일동 - 둔촌동 - 올림픽공원 - 방이 - 오금 - 개롱 - 거여 - 마천"
}

# 1. 전역 변수 초기화
G = nx.Graph()      # 전체 역 그래프
TG = nx.Graph()     # 환승/종점 압축 그래프
station_lines = defaultdict(list)      # {역 이름 : 호선 리스트}
line_sequences = {}                    # 호선 번호 → [(node, idx, pos), ...]
transfer_positions = {}                # 호선 번호 → [pos1,pos2,...] (환승+끝점 포지션)
global_idx = 0

# 2. 노드 추가 및 속성 부여 (idx, pos)
for line, station_str in lines.items():
    names = [s.strip() for s in station_str.split('-')]
    seq = []
    for pos, name in enumerate(names):
        node = (line, name)
        # 전역 인덱스, 라인 내 위치 속성
        G.add_node(node, idx=global_idx, pos=pos, line=line)
        TG.add_node(node, idx=global_idx, pos=pos, line=line)
        station_lines[name].append(line)
        seq.append(node)
        global_idx += 1
    line_sequences[line] = seq

# 3. 전체 그래프 G: 인접 역 간 간선
for line, seq in line_sequences.items():
    for u, v in zip(seq, seq[1:]):
        G.add_edge(u, v, weight=2)

# 4. 환승 + 종점 위치 수집
for line, seq in line_sequences.items():
    N = len(seq)
    pos_list = []
    for pos, node in enumerate(seq):
        name = node[1]
        # 환승역 혹은 라인 종점(양 끝)
        if len(station_lines[name]) > 1 or pos == 0 or pos == N-1:
            pos_list.append(pos)
    pos_list.sort()
    transfer_positions[line] = pos_list

# 5. TG: 환승역/종점 압축 간선 구축
for line, seq in line_sequences.items():
    pos_list = transfer_positions[line]
    M = len(pos_list)
    circular = (line == 2)  # 2호선이 순환선
    for i in range(M):
        p1 = pos_list[i]
        p2 = pos_list[(i+1) % M] if circular else (pos_list[i+1] if i+1<M else None)
        if p2 is None:
            continue
        u, v = seq[p1], seq[p2]
        # 거리: 정거장 수 × 2
        # 순환선일 땐 wrap-around 거리를 계산
        if circular and i == M-1:
            # wrap: p2 + N - p1
            dist = (p2 + len(seq) - p1) * 2
        else:
            dist = (p2 - p1) * 2
        TG.add_edge(u, v, weight=dist)

# 6. TG: 호선 간 환승 간선 추가
for name, lines_list in station_lines.items():
    if len(lines_list) > 1:
        nodes = [ (ln, name) for ln in lines_list ]
        for u in nodes:
            for v in nodes:
                if u < v:
                    TG.add_edge(u, v, weight=2)

# 7. 그래프 시각화 (선택)
pos = nx.kamada_kawai_layout(G)
nx.draw(G, pos, with_labels=True, font_family='Malgun Gothic')

# 이제 G, TG 모두 준비 완료!
