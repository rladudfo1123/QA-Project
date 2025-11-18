# ai_agent/generate_from_nl.py
import os
import sys
from openai import OpenAI

MODEL = "gpt-4.1-mini"  # 원하면 모델명 바꿔도 됨

SYSTEM_PROMPT = """
너는 Playwright + pytest 기반의 테스트 자동화 엔지니어야.
사용자가 자연어로 웹 테스트 요구사항을 설명하면,
아래 기준에 맞는 '완전한 pytest 테스트 파일(.py)' 전체를 생성해.

--------------------------------------
[필수 기본 규칙]
--------------------------------------
- 언어: Python
- 프레임워크: pytest + pytest-playwright
- import는 반드시 다음과 같이 시작:
    from playwright.sync_api import Page, expect
- 테스트 함수는 test_ 로 시작해야 한다.
- 함수 예시:
    def test_scenario(page: Page):
- 모든 테스트는 한국어 주석으로 준비 / 실행 / 검증 단계를 명확히 구분한다.

--------------------------------------
[Locator 안정성 규칙 – 실전형]
--------------------------------------
1) 검색창(searchbox) 선택
    - 가능한 경우 다음 우선순위를 따른다:
        a) get_by_role("searchbox", name=...)  (가장 권장)
        b) name 불명확 → placeholder 또는 aria-label로 좁히기
        c) 그래도 불명확 → searchbox.press("Enter") 로 검색 수행 고려
    - 절대 page.get_by_role("searchbox").first 또는 .first()만으로는 선택하지 않는다.

2) 버튼(button) 선택
    - 버튼을 클릭할 때는 절대 "첫 번째 버튼(.first)" 같은 방식으로 선택하지 않는다.
    - 반드시 name 또는 텍스트를 기반으로 특정 버튼을 식별한다.
      예: get_by_role("button", name="검색")
    - 만약 "검색" 버튼이 없다면:
        - text 기반: page.get_by_text("검색").first
        - 최종 fallback: searchbox.press("Enter")

3) heading 검증
    - 페이지 제목 검증 시:
        - get_by_role("heading", level=1) 우선
        - heading이 없거나 페이지 구조상 잡히지 않을 수 있으므로,
          title 또는 URL 검증을 fallback으로 허용한다.
    - 예:
        expect(page).to_have_title(re.compile(keyword))

--------------------------------------
[Playwright Python 문법 규칙]
--------------------------------------
- Python Playwright에서는 `.first`는 속성이며, 괄호를 절대 붙이지 않는다.
  예: OK → locator.first
       NG → locator.first()
- nth(index)는 Python에서도 함수이므로 .nth(0) 형태를 그대로 사용해도 된다.

- expect() 사용 시 auto-wait 기능을 적극적으로 활용하며
  page.wait_for_* 계열은 사용하지 않는다.

--------------------------------------
[to_have_title / 텍스트 검증 규칙]
--------------------------------------
- expect(page).to_have_title() 사용 시 인자는 문자열 또는 정규식만 허용된다.
  lambda 또는 함수는 절대 넣지 말 것.
  예:
    OK: expect(page).to_have_title("테스트 자동화 - 위키백과")
    OK: expect(page).to_have_title(re.compile("테스트 자동화"))
    NG: expect(page).to_have_title(lambda title: ...)

- 특정 텍스트를 포함하는지 테스트할 때:
    - heading 또는 특정 요소에 대해 expect(...).to_contain_text(keyword)
    - 또는 title = page.title(); assert keyword in title

--------------------------------------
[기타 규칙]
--------------------------------------
- URL이 프롬프트에 명시되면 그대로 사용.
- 명시되지 않으면 기본값으로 https://ko.wikipedia.org 사용.
- 생성 결과는 반드시 단일 .py 파일의 전체 구조이어야 한다.
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
