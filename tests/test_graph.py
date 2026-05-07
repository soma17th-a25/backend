"""end-to-end 시나리오 — 교통 도메인 전용. mock 노드 기준."""
import asyncio

from app.graph import graph


def _run(inputs: dict) -> dict:
    return asyncio.run(graph.ainvoke(inputs))


def test_accident_settlement_golden_path():
    out = _run({"user_query": "교통사고가 났는데 합의금을 얼마 받아야 할까요", "history": [], "session_id": "t1"})
    assert out["domain"] == "traffic"
    assert out["case_type"] == "accident_settlement"
    assert out["retrieved_docs"]
    assert out["guide_steps"], "guides.yaml 룩업 실패"
    assert out["answer_text"]
    assert out["confidence_score"] >= 0.0


def test_off_topic_routes_to_fallback():
    out = _run({"user_query": "오늘 점심 뭐 먹지", "history": [], "session_id": "t2"})
    assert out["domain"] == "unknown"
    assert out["fallback_reason"] == "no_domain"


def test_dui_skips_settlement():
    out = _run({"user_query": "음주운전으로 단속됐어요", "history": [], "session_id": "t3"})
    assert out["case_type"] == "dui"
    assert out["needs_settlement"] is False
    assert out.get("settlement") is None
    assert out["guide_steps"]


def test_settlement_computed_from_cases():
    out = _run({"user_query": "교통사고 합의금 어떻게 정하나요", "history": [], "session_id": "t4"})
    s = out.get("settlement")
    assert s is not None
    assert s["n_samples"] >= 2  # mock 사례 2건
    assert s["min"] <= s["median"] <= s["max"]


def test_hit_and_run_path_has_guide():
    out = _run({"user_query": "뺑소니 사고 어떻게 해야 하나요", "history": [], "session_id": "t5"})
    assert out["case_type"] == "hit_and_run"
    assert out["guide_steps"]
    assert any("자수" in step["title"] or "변론" in step["title"] for step in out["guide_steps"])


def test_unlicensed_no_guide_yet_falls_through():
    """unlicensed 는 가이드 미작성 → guide_steps 빈 배열이지만 흐름은 정상."""
    out = _run({"user_query": "무면허 운전으로 적발됐어요", "history": [], "session_id": "t6"})
    assert out["case_type"] == "unlicensed"
    assert out["retrieved_docs"]  # 검색은 됨
    assert out["guide_steps"] == []  # YAML 미작성
    assert out["answer_text"]  # 답변은 생성됨
