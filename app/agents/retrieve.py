"""Mock retrieve_node — 파트 B가 FAISS 실제 구현으로 교체.

계약: retrieved_docs 원소는 RetrievedDoc 스키마 준수.
스코프: 교통 도메인 전용 mock.
"""
from app.state import AgentState


_TRAFFIC_DOCS = {
    "accident_settlement": [
        {
            "id": "stat_road_traffic_3",
            "type": "statute",
            "title": "도로교통법 제3조 (신호기 등의 설치 및 관리)",
            "content": "신호기 등의 설치·관리 의무 규정...",
            "source": "law.go.kr",
            "score": 0.88,
            "metadata": {"article": "3조"},
        },
        {
            "id": "case_traffic_settle_001",
            "type": "case",
            "title": "교통사고 합의 사례 — 추돌 경상",
            "content": "치료비 200만원, 위자료 100만원, 합의금 350만원.",
            "source": "internal",
            "score": 0.83,
            "metadata": {"settlement_amount": 3500000, "injury_level": "minor"},
        },
        {
            "id": "case_traffic_settle_002",
            "type": "case",
            "title": "교통사고 합의 사례 — 후방추돌",
            "content": "전치 3주, 합의금 480만원.",
            "source": "internal",
            "score": 0.79,
            "metadata": {"settlement_amount": 4800000, "injury_level": "minor"},
        },
    ],
    "accident_injury": [
        {
            "id": "stat_traffic_special_3",
            "type": "statute",
            "title": "교통사고처리 특례법 제3조",
            "content": "업무상 과실·중과실 치사상 특례 규정...",
            "source": "law.go.kr",
            "score": 0.92,
            "metadata": {"article": "3조"},
        },
        {
            "id": "case_traffic_injury_001",
            "type": "case",
            "title": "인적 피해 합의 사례 — 전치 6주",
            "content": "치료비 800만원, 일실수익 400만원, 위자료 300만원, 합의금 1500만원.",
            "source": "internal",
            "score": 0.85,
            "metadata": {"settlement_amount": 15000000, "injury_level": "moderate"},
        },
    ],
    "dui": [
        {
            "id": "stat_road_traffic_44",
            "type": "statute",
            "title": "도로교통법 제44조 (술에 취한 상태에서의 운전 금지)",
            "content": "혈중알코올농도 0.03% 이상 운전 금지...",
            "source": "law.go.kr",
            "score": 0.95,
            "metadata": {"article": "44조"},
        },
        {
            "id": "stat_road_traffic_148_2",
            "type": "statute",
            "title": "도로교통법 제148조의2 (벌칙)",
            "content": "음주운전 처벌 규정 (단순·재범·인사사고)...",
            "source": "law.go.kr",
            "score": 0.93,
            "metadata": {"article": "148조의2"},
        },
    ],
    "hit_and_run": [
        {
            "id": "stat_specific_aggravation_5_3",
            "type": "statute",
            "title": "특정범죄 가중처벌 등에 관한 법률 제5조의3",
            "content": "도주차량 운전자의 가중처벌 규정...",
            "source": "law.go.kr",
            "score": 0.94,
            "metadata": {"article": "5조의3"},
        },
    ],
    "unlicensed": [
        {
            "id": "stat_road_traffic_43",
            "type": "statute",
            "title": "도로교통법 제43조 (무면허 운전 등의 금지)",
            "content": "운전면허 없이 자동차를 운전하지 못한다...",
            "source": "law.go.kr",
            "score": 0.9,
            "metadata": {"article": "43조"},
        },
    ],
    "traffic_violation": [
        {
            "id": "stat_road_traffic_17",
            "type": "statute",
            "title": "도로교통법 제17조 (자동차등의 속도)",
            "content": "도로별 제한속도 규정...",
            "source": "law.go.kr",
            "score": 0.86,
            "metadata": {"article": "17조"},
        },
    ],
}


async def retrieve_node(state: AgentState) -> dict:
    if state.get("domain") != "traffic":
        return {"retrieved_docs": []}
    case_type = state.get("case_type")
    docs = _TRAFFIC_DOCS.get(case_type, [])
    return {"retrieved_docs": docs}
