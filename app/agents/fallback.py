"""폴백 노드 — 분류 실패·검색 0건·법률 무관."""
from app.state import AgentState


async def fallback_node(state: AgentState) -> dict:
    reason = state.get("fallback_reason") or "unknown"
    msgs = {
        "no_domain": "질문이 법률 영역과 관련이 없거나 분류가 어렵습니다. 좀 더 구체적으로 작성해 주세요.",
        "no_docs": "관련 법령·판례를 충분히 찾지 못했습니다. 일반 안내만 제공합니다.",
        "llm_error": "응답 생성 중 일시적 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        "unknown": "처리할 수 없는 요청입니다.",
    }
    return {
        "answer_text": msgs.get(reason, msgs["unknown"]),
        "citations": [],
        "confidence_score": 0.0,
        "recommend_lawyer": True,
    }
