import pytest
from playwright.sync_api import Page, expect

@pytest.mark.parametrize("keyword", ["테스트 자동화"])
def test_wikipedia_search_contains_keyword(page: Page, keyword: str):
    # 준비: 위키백과 한국어 페이지 접속
    page.goto("https://ko.wikipedia.org")

    # 실행: 검색창에 키워드 입력 후 검색 버튼 클릭
    searchbox = page.get_by_role("searchbox").first()
    searchbox.fill(keyword)
    search_button = page.get_by_role("button", name="검색").first()
    search_button.click()

    # 검증: 결과 페이지의 제목에 키워드가 포함되어 있는지 확인
    heading = page.get_by_role("heading", level=1).first()
    expect(heading).to_contain_text(keyword)