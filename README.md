# Legal AI Agent — Backend

교통 법률 상담 AI 에이전트 백엔드 (FastAPI + LangGraph + FAISS).

**스코프: 교통 도메인 전용** — 교통사고 합의, 인적 피해, 음주운전, 뺑소니, 무면허, 일반 위반.

## 파트 분담

| 파트 | 담당 | 영역 |
|---|---|---|
| A | LLM | `app/agents/classify.py`, `generate.py`, `clarify.py`, `app/llm/` (예정), `prompts/` (예정) |
| B | 검색 | `app/agents/retrieve.py`, `app/retrieval/` (예정), `data/raw/`, `data/indices/`, `scripts/build_index.py` (예정) |
| C | 로직·통합 | `app/agents/guide.py`, `settlement.py`, `post_check.py`, `fallback.py`, `app/graph.py`, `app/state.py`, `app/api/`, `data/guides.yaml`, 통합 테스트 |

현재 커밋은 파트 C가 깐 골격. A·B 영역은 mock으로 채워둠 — 실제 구현으로 교체.

## 실행

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env

uvicorn app.api.main:app --reload --port 8000
```

## 엔드포인트

- `GET  /healthz` — 헬스 체크
- `POST /chat` — SSE 스트리밍 (이벤트: `meta`, `token`, `state`, `done`, `error`)
- `POST /chat/sync` — 비스트리밍 디버그용

요청 본문:

```json
{
  "user_query": "전세 보증금을 못 받고 있습니다",
  "session_id": "optional-uuid",
  "history": []
}
```

## 그래프 흐름

```
classify ─┬─ needs_clarify          → clarify → END
          ├─ domain=unknown         → fallback_no_domain → fallback → END
          └─ retrieve ─┬─ docs=[]   → fallback_no_docs → fallback → END
                       └─ guide → settlement → generate → post_check → END
```

## State 계약

`app/state.py` 의 `AgentState` 가 3 파트 인터페이스. 변경 시 합의 필요.

`retrieved_docs` 원소 키 (B → A·C 계약):
`id, type, title, content, source, score, metadata`

`metadata.settlement_amount` 가 사례에 있으면 `settlement_node` 가 통계 산출.

## 테스트

```bash
pytest -q
```

6개 시나리오: 합의 골든 패스, 비교통 폴백, 음주운전(합의 스킵), 합의금 통계, 뺑소니 가이드, 무면허(가이드 미작성 통과).

## 배포 메모

- Vercel serverless 는 SSE 타임아웃 짧음 → BE 는 Railway / Fly / Render 등 별도 호스팅.
- FAISS 인덱스 + BGE-M3 임베딩 메모리 약 2GB. 무료 티어 빠듯.
- 인덱스 파일은 git 미포함. 별도 다운로드 스크립트 필요 (B 담당).
