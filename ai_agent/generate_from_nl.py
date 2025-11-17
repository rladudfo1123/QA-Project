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
- 한국어 주석을 포함해 '준비 / 실행 / 검증' 단계 구조를 제공할 것.

Locator 안정성 규칙(중요!):
- get_by_placeholder() 를 사용할 때, 두 개 이상 매칭될 가능성이 있으면 절대 그대로 쓰지 말 것.
  예: placeholder 중복되는 경우 반드시 .first() 또는 .nth(0) 를 사용.
- 가능한 경우 get_by_role() + name 필터를 우선적으로 사용할 것.
  예: 검색창은 get_by_role("searchbox", name="위키백과 검색") 같은 형태 사용.
- role, label, aria-label, name 등을 활용해 'strict mode violation' 이 발생하지 않도록 작성할 것.
- selector가 불명확하면 #id 나 명확한 CSS selector를 안전하게 사용해도 됨.
- 테스트의 안정성을 위해 wait_for_selector 같은 대기 없이 expect 기반의 auto-waiting 사용.

기타 규칙:
- URL이 명시되지 않았다면 https://ko.wikipedia.org/ 를 기본 테스트 페이지로 사용할 것.
- 하나의 파일 전체 코드만 출력할 것(함수 여러개 가능).
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
