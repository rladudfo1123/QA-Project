import pytest
from playwright.sync_api import Page, expect

@pytest.mark.parametrize("keyword", ["테스트 자동화"])
def test_wikipedia_search_contains_keyword(page: Page, keyword: str):
    # 준비: 위키백과 한국어 페이지 접속
    page.goto("https://ko.wikipedia.org")

    # 실행: 검색창에 키워드 입력 후 검색 버튼 클릭
    # 검색창은 role="searchbox" 중 첫 번째 요소 선택
    searchbox = page.get_by_role("searchbox").first
    searchbox.fill(keyword)

    # 검색 버튼은 role="button" 중 첫 번째 요소 선택
    search_button = page.get_by_role("button").first
    search_button.click()

    # 검증: 결과 페이지의 제목(h1 heading) 텍스트에 키워드 포함 여부 확인
    heading = page.get_by_role("heading", level=1).first
    expect(heading).to_contain_text(keyword)

    # 추가 검증: URL에 검색어가 포함되어 있는지 확인 (선택적)
    expect(page).to_have_url(lambda url: keyword in url)