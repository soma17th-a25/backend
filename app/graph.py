"""LangGraph StateGraph 골격.

흐름:
  classify → (clarify | retrieve)
  retrieve → guide → settlement → generate → post_check → END
  검색 0건 / 분류 실패 시 fallback.
"""
from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.agents.classify import classify_node
from app.agents.clarify import clarify_node
from app.agents.retrieve import retrieve_node
from app.agents.guide import guide_node
from app.agents.settlement import settlement_node
from app.agents.generate import generate_node
from app.agents.post_check import post_check_node
from app.agents.fallback import fallback_node


def _route_after_classify(state: AgentState) -> str:
    if state.get("domain") == "unknown":
        return "fallback_no_domain"
    if state.get("needs_clarify"):
        return "clarify"
    return "retrieve"


def _route_after_retrieve(state: AgentState) -> str:
    if not state.get("retrieved_docs"):
        return "fallback_no_docs"
    return "guide"


async def _set_fallback_no_domain(state: AgentState) -> dict:
    return {"fallback_reason": "no_domain"}


async def _set_fallback_no_docs(state: AgentState) -> dict:
    return {"fallback_reason": "no_docs"}


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("classify", classify_node)
    g.add_node("clarify", clarify_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("guide", guide_node)
    g.add_node("settlement", settlement_node)
    g.add_node("generate", generate_node)
    g.add_node("post_check", post_check_node)
    g.add_node("fallback_no_domain", _set_fallback_no_domain)
    g.add_node("fallback_no_docs", _set_fallback_no_docs)
    g.add_node("fallback", fallback_node)

    g.set_entry_point("classify")

    g.add_conditional_edges(
        "classify",
        _route_after_classify,
        {
            "clarify": "clarify",
            "fallback_no_domain": "fallback_no_domain",
            "retrieve": "retrieve",
        },
    )
    g.add_edge("clarify", END)

    g.add_conditional_edges(
        "retrieve",
        _route_after_retrieve,
        {
            "fallback_no_docs": "fallback_no_docs",
            "guide": "guide",
        },
    )

    g.add_edge("guide", "settlement")
    g.add_edge("settlement", "generate")
    g.add_edge("generate", "post_check")
    g.add_edge("post_check", END)

    g.add_edge("fallback_no_domain", "fallback")
    g.add_edge("fallback_no_docs", "fallback")
    g.add_edge("fallback", END)

    return g.compile()


graph = build_graph()
