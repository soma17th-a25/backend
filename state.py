from typing import TypedDict, Optional, Literal

CaseType = Literal[
    "HIT_AND_RUN",
    "WRONG_WAY_DRIVING",
    "DRUNK_DRIVING",
    "PEDESTRIAN_ACCIDENT",
    "RECKLESS_DRIVING",
    "OUT_OF_SCOPE",
]


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class RetrievedDoc(TypedDict):
    doc_id: str
    type: Literal["법령", "판례", "사례"]
    title: str
    content: str
    case_types: list[str]
    score: float
    settlement_amount: Optional[int]


class Settlement(TypedDict):
    min: int
    median: int
    max: int
    sample_size: int
    basis: str


class Citation(TypedDict):
    marker_idx: int
    doc_id: str


class LegalState(TypedDict):
    # === 입력 (FastAPI에서 채움) ===
    session_id: str
    user_query: str
    history: list[ChatMessage]

    # === 파트 1: classify_node 산출 ===
    domain: str
    case_type: Optional[CaseType]
    needs_settlement: bool
    classification_confidence: float

    # === 파트 1: clarify_node 산출 (조기 종료 시) ===
    clarification_question: Optional[str]

    # === 파트 2: retrieve_node 산출 ===
    retrieved_docs: list[RetrievedDoc]

    # === 파트 2: guide_node 산출 ===
    guide_steps: Optional[list[str]]

    # === 파트 2: settlement_node 산출 (조건부) ===
    settlement: Optional[Settlement]

    # === 파트 1: generate_node 산출 ===
    answer_text: str
    citations: list[Citation]

    # === 파트 3: post_check_node 산출 ===
    confidence_score: float
    recommend_lawyer: bool
    situation_summary: Optional[str]
