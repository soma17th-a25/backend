# Part 1 — LLM 노드 (분류 · 명확화 · 답변 생성)

> 25조 AI 기반 법률 AI 챗봇 / 교통법규 시연 MVP / 파트 1 담당

---

## 1. 개요

LangGraph 기반 법률 챗봇에서 LLM 호출을 담당하는 파트.  
Upstage Solar mini로 사건 분류, Solar Pro로 답변 생성, 신뢰도 미달 시 명확화 질문을 반환한다.

| 노드            | 역할                                 | 모델        |
| --------------- | ------------------------------------ | ----------- |
| `classify_node` | 질문 → case_type 분류                | solar-mini  |
| `clarify_node`  | 분류 신뢰도 낮을 때 명확화 질문 반환 | 없음 (정적) |
| `generate_node` | 검색·가이드·합의금을 묶어 답변 생성  | solar-pro   |

---

## 2. 디렉토리 구조

```
part1/
├── .env.example              # UPSTAGE_API_KEY=your_key_here
├── .gitignore
├── requirements.txt
├── pytest.ini
├── README.md
│
├── constants.py              # 모델명, 임계치, 면책 고지 상수
├── taxonomy.py               # CaseType Literal, 한국어 매핑
├── state.py                  # LegalState TypedDict (팀 공유 인터페이스)
│
├── prompts/
│   ├── classify_system.txt   # 분류 시스템 프롬프트
│   ├── classify_examples.json  # 12개 few-shot 예시
│   ├── generate_system.txt   # 답변 생성 시스템 프롬프트
│   └── generate_user_template.txt  # 컨텍스트 슬롯 템플릿
│
├── llm/
│   └── solar_client.py       # Upstage Solar API 래퍼 (JSON / 스트리밍)
│
├── agents/
│   ├── classify.py           # classify_node
│   ├── clarify.py            # clarify_node
│   └── generate.py           # generate_node / generate_node_stream
│
├── utils/
│   ├── citation_extractor.py # [N] 마커 추출 → citations 배열
│   ├── keyword_fallback.py   # API 장애 시 키워드 분류 폴백
│   └── prompt_loader.py      # 프롬프트 파일 로딩 + 슬롯 치환
│
├── tests/
│   ├── scenarios.json        # 평가용 시나리오 12개
│   ├── test_classify.py
│   ├── test_generate.py
│   └── test_citation.py
│
└── scripts/
    ├── hello_upstage.py      # API 연결 확인
    ├── run_classify.py       # classify 단독 실행
    ├── run_generate.py       # generate 단독 실행 (mock 입력, outputs/ 저장)
    └── eval_classify.py      # 평가셋 10개 실행 → eval_results.csv
```

---

## 3. 환경 셋업

Python 3.11 이상 권장.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4. .env 설정

[Upstage Console](https://console.upstage.ai/api-keys)에서 API 키 발급 후:

```bash
cp .env.example .env
# .env 파일을 열어 UPSTAGE_API_KEY=발급받은_키 입력
```

---

## 5. 동작 확인

### API 연결 확인

```bash
python scripts/hello_upstage.py
# 정상: ✓ Upstage Solar API 연결 성공
```

### classify 단독 실행

```bash
python scripts/run_classify.py "술 마시고 운전하다 단속됐어요"
# 출력: case_type, confidence, needs_settlement
```

### generate 단독 실행

```bash
python scripts/run_generate.py
# 출력: 생성된 답변 (터미널 + outputs/generate_YYYYMMDD_HHMMSS.txt 저장)
```

---

## 6. 테스트

```bash
pytest tests/ -v
# 15개 테스트 전체 통과 확인
```

---

## 7. 평가

```bash
python scripts/eval_classify.py
# 시나리오 10개 실행, 호출 간격 7초
# 목표: 정확도 80% 이상
```

> eval_results.csv는 .gitignore에 포함되어 저장소에 올라가지 않는다.

---

## 8. 주요 상수 (constants.py)

| 상수                 | 값         | 설명                                     |
| -------------------- | ---------- | ---------------------------------------- |
| `CLARIFY_THRESHOLD`  | 0.4        | confidence < 0.4 이면 clarify 분기       |
| `MAX_CONTEXT_DOCS`   | 5          | generate에 넘길 retrieved_docs 최대 개수 |
| `MAX_HISTORY_TURNS`  | 6          | generate에 포함할 최근 대화 턴 수        |
| `GEMINI_FLASH_MODEL` | solar-mini | 분류용 (Solar mini)                      |
| `GEMINI_PRO_MODEL`   | solar-pro  | 생성용 (Solar Pro)                       |

---

## 9. 노드 동작 요약

### classify_node

1. `classify_system.txt` + `classify_examples.json` 12개 few-shot으로 프롬프트 조립
2. Solar mini에 JSON 모드 요청 (`response_format={"type": "json_object"}`)
3. API 실패 시 `keyword_fallback.classify_by_keyword()` 호출 (confidence=0.3 고정)
4. `OUT_OF_SCOPE` / `RECKLESS_DRIVING`은 `needs_settlement` 강제 false

### clarify_node

- confidence < 0.4 일 때 호출 (LangGraph 라우팅)
- 정적 명확화 질문 반환 (MVP)

### generate_node

1. retrieved_docs에 `[1]`, `[2]` 마커 부여 후 컨텍스트 조립
2. settlement / guide_steps 없으면 해당 섹션 제외 (None 출력 방지)
3. 답변 끝에 면책 고지 자동 부착 (중복 방지)
4. `citation_extractor`로 본문 스캔 → citations 배열 반환
5. Solar Pro 실패 시 검색 문서 목록 기반 폴백 답변 반환

---

## 10. 파트 2에서 받아야 하는 데이터

`classify_node` 실행 후 파트 2(FAISS 검색)가 `retrieve_node`를 통해 State에 채워야 하는 필드:

```python
state["retrieved_docs"]: list[RetrievedDoc]
```

각 `RetrievedDoc` dict의 키는 아래와 정확히 일치해야 한다.

| 키                  | 타입                             | 설명                                            |
| ------------------- | -------------------------------- | ----------------------------------------------- |
| `doc_id`            | `str`                            | 고유 식별자 (알파벳·숫자·\_만)                  |
| `type`              | `"법령"` \| `"판례"` \| `"사례"` | 문서 유형                                       |
| `title`             | `str`                            | 인용 시 표시할 제목                             |
| `content`           | `str`                            | 임베딩 및 답변 컨텍스트용 본문                  |
| `case_types`        | `list[str]`                      | 해당 case_type enum 값 리스트                   |
| `score`             | `float`                          | FAISS 유사도 점수 (높을수록 우선)               |
| `settlement_amount` | `Optional[int]`                  | `type="사례"`일 때만 원 단위 정수, 그 외 `None` |

- `generate_node`는 `score` 내림차순으로 상위 `MAX_CONTEXT_DOCS`(=5)개만 사용한다.
- `retrieved_docs`가 빈 리스트이면 폴백 답변이 생성된다.

---

## 11. 파트 3에서 받아야 하는 데이터

`retrieve_node` 이후 파트 3(guide_node, settlement_node)가 State에 채워야 하는 필드:

### guide_steps (guide_node 산출)

```python
state["guide_steps"]: Optional[list[str]]
```

- 사건 유형별 단계별 대응 문자열 리스트
- 예: `["면허정지 행정처분 확인", "형사처벌 절차 파악", ...]`
- `None`이면 `generate_node`가 가이드 섹션을 생략한다

### settlement (settlement_node 산출, 조건부)

```python
state["settlement"]: Optional[Settlement]
```

`needs_settlement=True`일 때만 채운다. `Settlement` dict의 키:

| 키            | 타입  | 설명                  |
| ------------- | ----- | --------------------- |
| `min`         | `int` | 최소 합의금 (원)      |
| `median`      | `int` | 중간값 합의금 (원)    |
| `max`         | `int` | 최대 합의금 (원)      |
| `sample_size` | `int` | 산출에 사용한 사례 수 |
| `basis`       | `str` | 산출 근거 설명        |

- `settlement=None`이면 `generate_node`가 합의금 섹션을 생략한다.

---

## 12. 파트 3 통합

파트 3(FastAPI + LangGraph)에서 노드 import:

```python
from part1.agents.classify import classify_node
from part1.agents.generate import generate_node, generate_node_stream
from part1.agents.clarify import clarify_node
from part1.state import LegalState
from part1.taxonomy import CaseType
from part1.constants import CLARIFY_THRESHOLD
```

LangGraph 라우팅 예시:

```python
def route_after_classify(state: LegalState) -> str:
    if state["classification_confidence"] < CLARIFY_THRESHOLD:
        return "clarify"
    return "retrieve"
```

통합 시 점검 사항:

- `generate_node_stream`이 `astream_events`로 토큰을 외부로 흘리는지 (LangGraph 콜백 설정 필요)
- 파트 2의 `retrieved_docs` dict 키가 위 §10 표와 정확히 일치하는지
- `guide_steps`, `settlement`이 `generate_node` 호출 전에 State에 채워지는지

---

## 13. 의존성 비고

- LLM SDK: `openai` (Upstage Solar API는 OpenAI 호환 포맷 사용)
- API Base URL: `https://api.upstage.ai/v1`
- 비동기: `asyncio` 기반, 테스트는 `pytest-asyncio` (asyncio_mode=auto)
