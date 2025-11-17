from playwright.sync_api import Page, expect

def test_wikipedia_search_contains_test_automation(page: Page):
    # 준비: 위키백과 한국어 페이지 접속
    page.goto("https://ko.wikipedia.org/")

    # 실행: 검색창에 '테스트 자동화' 입력 후 검색 버튼 클릭
    # 검색창은 role="searchbox" + name="검색" 으로 접근
    searchbox = page.get_by_role("searchbox", name="검색")
    searchbox.fill("테스트 자동화")

    # 검색 버튼은 role="button" + name="검색" 으로 접근
    search_button = page.get_by_role("button", name="검색")
    search_button.click()

    # 검증: 결과 페이지 제목에 '테스트 자동화' 텍스트 포함 여부 확인
    # 제목은 role="heading" + level=1 으로 접근
    heading = page.get_by_role("heading", level=1)
    expect(heading).to_contain_text("테스트 자동화")