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
- 절대 실제 DOM 구조를 임의로 추측하지 말 것.
- get_by_placeholder, get_by_role(name=...) 값은 반드시 '사용자가 제공한 사이트와 문맥에 맞는 가장 가능성 높은 실제 UI 텍스트'로 구성해야 한다.
- placeholder, name 값이 불명확하면:
    1) get_by_role("searchbox") 를 사용하고, 여러 개가 나올 수 있으면 .first 속성으로 첫 요소를 선택할 것. (예: searchbox = page.get_by_role("searchbox").first)
    2) role="textbox" + label 기반 선택
    3) aria-label 또는 id 기반 selector 사용
    4) text 기반 selector 사용
  이 순서를 우선적으로 적용할 것.
- placeholder 또는 name 이 여러 요소에 매칭될 가능성이 있으면 반드시 .first 속성이나 .nth(0) 메서드로 하나만 선택할 것.
- button 은 text 기반 또는 role="button" 기반으로 찾되, 여러 개일 수 있으므로 .first 속성 또는 .nth(0)로 첫 번째 버튼만 선택할 것.
- heading 은 get_by_role("heading", level=1).first 로 선택.

테스트 안정화 규칙:
- Playwright expect() 의 auto-waiting 기능을 적극 활용하되, page.wait_for_* 는 사용하지 말 것.
- 클릭 이후 페이지 전환을 예상할 때는 expect(page).to_have_url() 또는 expect(heading) 기반 검증을 작성할 것.

기타 규칙:
- URL이 프롬프트에 명시되면 반드시 그 URL을 사용하고, 명시되지 않았다면 https://ko.wikipedia.org 을 기본값으로 사용.
- 하나의 .py 파일 전체 출력 (pytest 테스트 파일 완성형)
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
