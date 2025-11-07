import pytest
from playwright.sync_api import Page, expect
from wikipedia import HOME

@pytest.fixture(autouse=True)
def goto_home(page: Page):
    # 위키피디아 홈으로 이동하고 완전히 로드될 때까지 대기
    page.goto(HOME, wait_until="domcontentloaded")

    # 메인 검색창이 뜰 때까지 기다려서 완전 로딩 보장
    search_box = page.locator("input#searchInput")
    expect(search_box).to_be_visible(timeout=10000)
