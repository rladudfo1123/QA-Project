# ai_agent/generate_from_nl.py
import os
import sys
from openai import OpenAI

MODEL = "gpt-4.1-mini"  # 원하면 모델명 바꿔도 됨

SYSTEM_PROMPT = """
너는 Playwright + pytest 기반의 테스트 자동화 엔지니어야.
사용자가 자연어로 웹 테스트 요구사항을 설명하면,
아래 기준에 맞는 '완전한 테스트 파일 전체'를 생성해.

필수 규칙:
- 언어: Python
- 프레임워크: pytest + pytest-playwright
- import:
  from playwright.sync_api import Page, expect
- 테스트 함수는 반드시 test_ 로 시작
- 시그니처 예: def test_scenario(page: Page):
- 한국어 주석으로 '준비 / 실행 / 검증' 단계를 명확히 작성할 것.

Locator 안정성 규칙(매우 중요):
1) 검색창(searchbox) 선택 규칙:
   - get_by_role("searchbox", name 포함)를 우선 사용
     예: get_by_role("searchbox", name="검색")
   - name이 여러 개이면 placeholder나 aria-label로 좁히기
   - searchbox가 불명확할 경우 press("Enter") 활용을 우선 고려

2) 버튼 선택 규칙:
   - "검색" 버튼은 반드시 name="검색" 조건을 우선 사용
     예: get_by_role("button", name="검색")
   - name="검색"이 없으면 text 기반으로 "검색" 포함 버튼 선택
   - 버튼 식별 불가 시 click() 대신 searchbox.press("Enter")로 검색 실행

3) heading 검증 규칙:
   - get_by_role("heading", level=1)로 찾기 어려울 경우,
     결과 검증은 page.title() 또는 URL 기반 검증을 대체 수단으로 허용
"""


def build_user_prompt(nl_description: str) -> str:
    return f"""
아래는 사용자가 원하는 웹 테스트에 대한 자연어 설명이야:

[요구사항 설명]
{nl_description}

위 요구사항을 만족하는 pytest + Playwright(sync) 테스트 코드를
'하나의 파이썬 파일 전체' 형태로 작성해줘.

조건:
- test_ 로 시작하는 하나 이상의 테스트 함수 작성
- selector는 text, role, placeholder 등 안정적인 것을 우선 사용
- 한국어 주석을 적절히 포함해줘
"""

def extract_code(block: str) -> str:
    # ```python ... ``` 형식 제거
    if "```" not in block:
        return block

    parts = block.split("```")
    # ```python\n...\n``` 구조일 가능성
    for part in parts:
        part = part.strip()
        if part.startswith("python"):
            lines = part.splitlines()
            # 첫 줄 'python' 제거
            return "\n".join(lines[1:])
    # 그냥 첫 코드 블럭 사용
    if len(parts) >= 2:
        return parts[1]
    return block


def main():
    # 프롬프트를 CLI 인자나 환경변수로 받기
    nl_description = None
    if len(sys.argv) > 1:
        nl_description = sys.argv[1]
    elif os.environ.get("NL_PROMPT"):
        nl_description = os.environ["NL_PROMPT"]

    if not nl_description:
        print("자연어 설명이 필요합니다. 예:")
        print('  python ai_agent/generate_from_nl.py "위키백과 검색 테스트 만들어줘"')
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(nl_description)},
        ],
        temperature=0.2,
    )

    raw_content = completion.choices[0].message.content or ""
    code = extract_code(raw_content)

    # Playwright 폴더 아래에 테스트 파일 생성
    os.makedirs("Playwright", exist_ok=True)
    target_path = os.path.join("Playwright", "test_nl_generated.py")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"[INFO] 자연어 설명으로부터 테스트 파일 생성 완료: {target_path}")

if __name__ == "__main__":
    main()
