import pytest
from playwright.sync_api import Page, expect

@pytest.mark.parametrize("keyword", ["테스트 자동화"])
def test_wikipedia_korean_search(page: Page, keyword: str):
    # 준비: 위키백과 한국어 페이지 접속
    page.goto("https://ko.wikipedia.org")

    # 실행: 검색창에 키워드 입력 후 검색 버튼 클릭
    searchbox = page.get_by_role("searchbox", name="검색")
    searchbox.fill(keyword)

    # "검색" 버튼 클릭 시도 (name="검색" 버튼 우선)
    search_button = page.get_by_role("button", name="검색")
    if search_button.count() > 0:
        search_button.click()
    else:
        # 버튼이 없으면 Enter 키로 검색 실행
        searchbox.press("Enter")

    # 검증: 결과 페이지 제목에 검색어 포함 여부 확인
    expect(page).to_have_title(lambda title: keyword in title)