# Playwright/conftest.py
import pytest
from playwright.sync_api import Page
from wikipedia import HOME  # 같은 폴더의 wikipedia.py에서 HOME 가져옴

@pytest.fixture(autouse=True)
def goto_home(page: Page):
    page.goto(HOME)
