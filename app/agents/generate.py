"""Mock generate_node — 파트 A가 Gemini Pro 스트리밍으로 교체.

토큰 단위 스트리밍은 LangGraph astream_events 통해 SSE로 전달.
"""
import asyncio
from app.state import AgentState


async def generate_node(state: AgentState) -> dict:
    docs = state.get("retrieved_docs", [])
    citations = [
        {"marker": f"[{i+1}]", "doc_id": d["id"], "title": d["title"], "source": d["source"]}
        for i, d in enumerate(docs[:5])
    ]
    domain = state.get("domain", "unknown")
    case_type = state.get("case_type", "")

    parts = [
        f"[{domain}/{case_type}] 분야 답변(mock).",
        "결론: 법적 권리 행사 가능.",
        f"근거: {', '.join(c['marker'] + ' ' + c['title'] for c in citations) or '검색 결과 없음'}.",
        "주의: 본 답변은 일반 정보이며 법률 자문이 아닙니다.",
    ]
    text = "\n".join(parts)

    await asyncio.sleep(0)
    return {"answer_text": text, "citations": citations}
