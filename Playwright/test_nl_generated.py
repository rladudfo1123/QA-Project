import re
from playwright.sync_api import Page, expect

def test_wikipedia_search_contains_keyword(page: Page):
    # 준비: 위키백과 한국어 페이지 접속
    page.goto("https://ko.wikipedia.org")

    # 실행: 검색창에 '테스트 자동화' 입력 후 검색 버튼 클릭
    searchbox = page.get_by_role("searchbox", name="검색")
    searchbox.fill("테스트 자동화")

    # '검색' 버튼을 역할과 이름으로 명확히 선택하여 클릭
    search_button = page.get_by_role("button", name="검색")
    search_button.click()

    # 검증: 결과 페이지 제목에 '테스트 자동화' 포함 여부 확인
    expect(page).to_have_title(re.compile("테스트 자동화"))