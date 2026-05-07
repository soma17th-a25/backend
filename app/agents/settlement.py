"""settlement_node — retrieved_docs 중 사례에서 합의금 통계."""
from statistics import median
from app.state import AgentState

MIN_RELIABLE_SAMPLES = 5


async def settlement_node(state: AgentState) -> dict:
    if not state.get("needs_settlement"):
        return {"settlement": None}

    amounts: list[int] = []
    for doc in state.get("retrieved_docs", []):
        if doc.get("type") != "case":
            continue
        amt = doc.get("metadata", {}).get("settlement_amount")
        if isinstance(amt, (int, float)) and amt > 0:
            amounts.append(int(amt))

    if not amounts:
        return {"settlement": None}

    return {
        "settlement": {
            "min": min(amounts),
            "median": int(median(amounts)),
            "max": max(amounts),
            "n_samples": len(amounts),
            "currency": "KRW",
            "reliable": len(amounts) >= MIN_RELIABLE_SAMPLES,
        }
    }
