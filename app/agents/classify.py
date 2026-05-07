"""Mock classify_node — 파트 A가 실제 구현으로 교체.

스코프: 교통 관련 사건만. 비교통 질문은 unknown → fallback.
case_type 매핑은 키워드 우선순위 기반(앞 규칙이 우선). 본구현 시 Gemini Flash JSON 출력으로 대체.
"""
from app.state import AgentState


KEYWORD_RULES: list[tuple[str, list[str], bool]] = [
    # (case_type, keywords, needs_settlement)
    ("dui", ["음주운전", "음주", "혈중알코올", "면허취소", "면허정지"], False),
    ("hit_and_run", ["뺑소니", "도주", "사고 후 도주", "특가법"], True),
    ("unlicensed", ["무면허"], False),
    ("accident_injury", ["사망", "중상", "전치", "인사사고", "사람 다침", "인명"], True),
    ("accident_settlement", ["교통사고", "접촉사고", "추돌", "물피", "차사고", "보험", "합의금", "과실비율", "과실"], True),
    ("traffic_violation", ["과속", "신호위반", "범칙금", "벌점", "딱지"], False),
]


async def classify_node(state: AgentState) -> dict:
    q = state.get("user_query", "")

    for case_type, keywords, needs_settlement in KEYWORD_RULES:
        if any(k in q for k in keywords):
            return {
                "domain": "traffic",
                "case_type": case_type,
                "needs_settlement": needs_settlement,
                "needs_clarify": False,
                "classification_confidence": 0.85,
            }

    return {
        "domain": "unknown",
        "case_type": None,
        "needs_settlement": False,
        "needs_clarify": True,
        "classification_confidence": 0.3,
    }
