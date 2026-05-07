"""Gemini API 키·모델·SDK 통신 스모크 테스트.

용도:
  - .env 의 GEMINI_API_KEY 가 유효한지
  - GEMINI_FLASH_MODEL / GEMINI_PRO_MODEL 이 호출 가능한지
  - 동기·스트리밍 둘 다 동작하는지

실행:
  python -m scripts.smoke_gemini
"""
import sys
import asyncio
from app.config import settings


def _check_key() -> bool:
    if not settings.gemini_api_key:
        print("[FAIL] GEMINI_API_KEY 가 비어있음. .env 확인 필요.")
        return False
    masked = settings.gemini_api_key[:6] + "..." + settings.gemini_api_key[-4:]
    print(f"[OK]   GEMINI_API_KEY 로딩됨 ({masked})")
    return True


def test_flash_sync():
    """Flash 모델 동기 호출."""
    from google import genai
    client = genai.Client(api_key=settings.gemini_api_key)
    print(f"\n--- Flash 동기 호출: {settings.gemini_flash_model} ---")
    res = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents="한 문장으로 자기소개해줘.",
    )
    print("응답:", res.text)


def test_pro_streaming():
    """Pro 모델 스트리밍 호출."""
    from google import genai
    client = genai.Client(api_key=settings.gemini_api_key)
    print(f"\n--- Pro 스트리밍 호출: {settings.gemini_pro_model} ---")
    print("토큰: ", end="", flush=True)
    n_chunks = 0
    for chunk in client.models.generate_content_stream(
        model=settings.gemini_pro_model,
        contents="교통사고 합의 절차를 3단계로 짧게.",
    ):
        if chunk.text:
            print(chunk.text, end="", flush=True)
            n_chunks += 1
    print(f"\n[OK]   스트리밍 청크 수: {n_chunks}")


def test_structured_output():
    """Flash 구조화 출력 — A 가 classify_node 에서 쓸 패턴."""
    from google import genai
    from pydantic import BaseModel

    class Classification(BaseModel):
        domain: str
        case_type: str
        confidence: float

    client = genai.Client(api_key=settings.gemini_api_key)
    print(f"\n--- 구조화 출력 (JSON 강제): {settings.gemini_flash_model} ---")
    res = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents="질문: '음주운전으로 단속됐어요'. 분류해줘. domain은 'traffic'|'unknown', case_type은 'dui'|'accident_settlement'|'hit_and_run'|'unlicensed'|'traffic_violation'|null 중 하나.",
        config={"response_mime_type": "application/json", "response_schema": Classification},
    )
    print("JSON:", res.text)
    print("파싱:", res.parsed)


def main() -> int:
    if not _check_key():
        return 1

    failed = []
    for name, fn in [
        ("flash_sync", test_flash_sync),
        ("pro_streaming", test_pro_streaming),
        ("structured_output", test_structured_output),
    ]:
        try:
            fn()
            print(f"[OK]   {name}")
        except Exception as e:
            print(f"[FAIL] {name}: {type(e).__name__}: {e}")
            failed.append(name)

    print("\n" + "=" * 50)
    if failed:
        print(f"실패: {failed}")
        return 1
    print("모두 통과. Gemini 연결 정상.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
