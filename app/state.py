from typing import TypedDict, Optional, Literal

Domain = Literal["traffic", "unknown"]


class RetrievedDoc(TypedDict):
    id: str
    type: Literal["statute", "precedent", "case"]
    title: str
    content: str
    source: str
    score: float
    metadata: dict


class GuideStep(TypedDict):
    step: int
    title: str
    items: list[str]
    note: Optional[str]


class Settlement(TypedDict):
    min: int
    median: int
    max: int
    n_samples: int
    currency: str
    reliable: bool


class Citation(TypedDict):
    marker: str
    doc_id: str
    title: str
    source: str


class AgentState(TypedDict, total=False):
    user_query: str
    history: list[dict]
    session_id: str

    domain: Domain
    case_type: Optional[str]
    needs_settlement: bool
    needs_clarify: bool
    classification_confidence: float
    clarify_question: Optional[str]

    retrieved_docs: list[RetrievedDoc]

    guide_steps: list[GuideStep]
    settlement: Optional[Settlement]

    answer_text: str
    citations: list[Citation]

    confidence_score: float
    recommend_lawyer: bool
    fallback_reason: Optional[str]
