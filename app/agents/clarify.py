"""Mock clarify_node — 파트 A가 실제 구현으로 교체."""
from app.state import AgentState

TEMPLATES = {
    "traffic": "사고 일자, 피해 정도(대물/인적), 가입 보험, 과실 인정 여부를 알려주세요.",
    "unknown": "교통사고·음주운전·뺑소니 등 교통 관련 사건만 상담 가능합니다. 사건 유형을 구체적으로 알려주세요.",
}


async def clarify_node(state: AgentState) -> dict:
    domain = state.get("domain", "unknown")
    return {"clarify_question": TEMPLATES.get(domain, TEMPLATES["unknown"])}
