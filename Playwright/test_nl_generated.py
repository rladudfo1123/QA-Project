import pytest
from playwright.sync_api import Page, expect

@pytest.mark.parametrize("search_text", ["테스트 자동화"])
def test_wikipedia_search_contains_text(page: Page, search_text: str):
    # 준비: 위키백과 한국어 페이지 접속
    page.goto("https://ko.wikipedia.org")

    # 실행: 검색창에 검색어 입력 후 검색 실행
    # 검색창은 role="searchbox"가 우선이므로 사용, 여러개일 경우 .first() 적용
    searchbox = page.get_by_role("searchbox").first()
    searchbox.fill(search_text)
    # 검색 버튼은 role="button" 중 텍스트가 '검색'인 버튼을 .first()로 선택
    search_button = page.get_by_role("button", name="검색").first()
    search_button.click()

    # 검증: 검색 결과 페이지의 첫 번째 제목에 검색어가 포함되어 있는지 확인
    # 검색 결과 페이지는 heading level=1이 검색어를 포함하는 제목일 가능성이 높음
    heading = page.get_by_role("heading", level=1).first()
    expect(heading).to_contain_text(search_text)
    # URL도 검색어가 포함된 쿼리 파라미터를 포함하는지 확인 (추가 안정성)
    expect(page).to_have_url(lambda url: "테스트+자동화" in url or "테스트%20자동화" in url)