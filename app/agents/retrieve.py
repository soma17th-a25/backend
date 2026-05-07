"""Mock retrieve_node — 파트 B 가 FAISS 본구현으로 교체.

계약: retrieved_docs 원소는 RetrievedDoc 스키마 준수.
스코프: 교통 도메인 전용. case_type 기준 mock 문서 반환.
"""
from app.state import LegalState

_TRAFFIC_DOCS: dict[str, list[dict]] = {
    "DRUNK_DRIVING": [
        {
            "doc_id": "law_road_44",
            "type": "법령",
            "title": "도로교통법 제44조 (술에 취한 상태에서의 운전 금지)",
            "content": "혈중알코올농도 0.03% 이상 운전 금지. 위반 시 형사·행정처분.",
            "case_types": ["DRUNK_DRIVING"],
            "score": 0.95,
            "settlement_amount": None,
        },
        {
            "doc_id": "law_road_148_2",
            "type": "법령",
            "title": "도로교통법 제148조의2 (벌칙 — 음주운전)",
            "content": "혈중알코올농도 구간별 처벌 규정 (단순/재범/인사사고).",
            "case_types": ["DRUNK_DRIVING"],
            "score": 0.93,
            "settlement_amount": None,
        },
    ],
    "HIT_AND_RUN": [
        {
            "doc_id": "law_specific_aggravation_5_3",
            "type": "법령",
            "title": "특정범죄 가중처벌 등에 관한 법률 제5조의3 (도주차량)",
            "content": "도주차량 운전자의 가중처벌 규정.",
            "case_types": ["HIT_AND_RUN"],
            "score": 0.94,
            "settlement_amount": None,
        },
    ],
    "PEDESTRIAN_ACCIDENT": [
        {
            "doc_id": "law_traffic_special_3",
            "type": "법령",
            "title": "교통사고처리 특례법 제3조",
            "content": "업무상 과실·중과실 치사상 특례 규정. 12대 중과실 단서.",
            "case_types": ["PEDESTRIAN_ACCIDENT"],
            "score": 0.92,
            "settlement_amount": None,
        },
        {
            "doc_id": "case_pedestrian_001",
            "type": "사례",
            "title": "보행자 사고 합의 사례 — 횡단보도 경상",
            "content": "치료비 200만원, 위자료 100만원, 합의금 350만원.",
            "case_types": ["PEDESTRIAN_ACCIDENT"],
            "score": 0.83,
            "settlement_amount": 3500000,
        },
        {
            "doc_id": "case_pedestrian_002",
            "type": "사례",
            "title": "보행자 사고 합의 사례 — 전치 6주",
            "content": "치료비 800만원, 일실 400만원, 위자료 300만원, 합의금 1,500만원.",
            "case_types": ["PEDESTRIAN_ACCIDENT"],
            "score": 0.85,
            "settlement_amount": 15000000,
        },
    ],
    "WRONG_WAY_DRIVING": [
        {
            "doc_id": "law_road_13",
            "type": "법령",
            "title": "도로교통법 제13조 (차마의 통행)",
            "content": "차마는 도로의 우측 부분으로 통행하여야 한다.",
            "case_types": ["WRONG_WAY_DRIVING"],
            "score": 0.9,
            "settlement_amount": None,
        },
    ],
    "RECKLESS_DRIVING": [
        {
            "doc_id": "law_road_46_3",
            "type": "법령",
            "title": "도로교통법 제46조의3 (난폭운전 금지)",
            "content": "9개 위반행위 둘 이상 또는 하나를 지속·반복 시 난폭운전.",
            "case_types": ["RECKLESS_DRIVING"],
            "score": 0.91,
            "settlement_amount": None,
        },
    ],
}


async def retrieve_node(state: LegalState) -> dict:
    case_type = state.get("case_type")
    if not case_type or case_type == "OUT_OF_SCOPE":
        return {"retrieved_docs": []}
    docs = _TRAFFIC_DOCS.get(case_type, [])
    return {"retrieved_docs": docs}
