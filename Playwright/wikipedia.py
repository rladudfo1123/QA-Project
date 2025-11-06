from playwright.sync_api import sync_playwright, expect
import re
import time

HOME = "https://ko.wikipedia.org/"

font_sizes = [
    ("작음", 0),
    ("표준", 1),
    ("큼", 2),
]
wide_case = [
    ("넓게", 0, "vector-feature-limited-width-clientpref-0"),
    ("표준", 1, "vector-feature-limited-width-clientpref-1"),
]
WIDE_DESC = "콘텐츠는 브라우저 창에 맞도록 최대한 넓게 맞춥니다."

theme_case = [
    ("자동", "os"),
    ("라이트", "day"),
    ("다크", "night"),
]

# 이중 장치
def _expect_html_class_contains(page, fragment: str):
    pattern = re.compile(rf"\b{re.escape(fragment)}\b")
    expect(page.locator("html")).to_have_attribute("class", pattern)

# SC1: 홈 진입 시 사이드 패널/디폴트 확인
def SC1(page):
    panel = page.locator('xpath=//*[@id="vector-appearance-pinned-container"]')
    expect(panel).to_be_visible() # 사이드 패널 유무 확인
    print("사이드 패널 확인")

    panel_title_desc = page.locator('xpath=//*[@id="vector-appearance"]/div[1]/div')
    expect(panel_title_desc).to_have_text("보이기") # 사이드 패널 타이틀 확인
    print("사이드 패널 보이기 문구 확인")

    panel_hide_btn = page.locator('xpath=//*[@id="vector-appearance"]/div[1]/button[2]')
    expect(panel_hide_btn).to_have_text("숨기기") # 사이드 패널 숨기기 확인
    print("사이드 패널 숨기기 문구 확인")

    fontsize_default_check = page.locator('xpath=//*[@id="skin-client-pref-vector-feature-custom-font-size-value-1"]')
    expect(fontsize_default_check).to_be_checked() # 폰트사이즈 체크 확인
    print("폰트크기 디폴트 표준 선택 확인")

    fontwide_default_check = page.locator('xpath=//*[@id="skin-client-pref-vector-feature-limited-width-value-1"]')
    expect(fontwide_default_check).to_be_checked() # 폰트너비 체크 확인
    print("폰트너비 디폴트 표준 선택 확인")
    
    fontcolor_default_check = page.locator('xpath=//*[@id="skin-client-pref-skin-theme-value-day"]')
    expect(fontcolor_default_check).to_be_checked() # 색상 체크 확인
    print("폰트색상 디폴트 라이트 선택 확인")

# SC2: 글 크기 라디오/라벨 클릭 검증
def SC2(page):
    # 글 크기 라디오 버튼 선택
    for name, value in font_sizes:
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-custom-font-size-value-{value}"]')
        radio.check()
        expect(radio).to_be_checked()
        _expect_html_class_contains(page, f"vector-feature-custom-font-size-clientpref-{value}")

    # 문구 클릭
    for name, value in font_sizes:
        label = page.locator(
            f'xpath=//*[@id="skin-client-prefs-vector-feature-custom-font-size"]/div[2]/ul/li/div/form/div[{value+1}]/label/span'
        )
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-custom-font-size-value-{value}"]')
        label.click()
        expect(radio).to_be_checked()
        _expect_html_class_contains(page, f"vector-feature-custom-font-size-clientpref-{value}")

# SC3: 글 크기 선택 후 새 탭에서 유지 확인
def SC3(page, context):
    for name, value in font_sizes:
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-custom-font-size-value-{value}"]')
        radio.click()
        expect(radio).to_be_checked()

        new_page = context.new_page()
        new_page.goto(HOME)
        new_radio = new_page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-custom-font-size-value-{value}"]')
        expect(new_radio).to_be_checked()
        new_page.close()

# SC4: 너비 라디오/라벨 클릭 검증
def SC4(page):
    for name, value, key in wide_case:
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-limited-width-value-{value}"]')
        radio.click()
        expect(radio).to_be_checked()
        _expect_html_class_contains(page, key)

        if value == 0:  # 넓게일 때만 설명 문구 노출
            desc = page.locator('xpath=//*[@id="skin-client-prefs-vector-feature-limited-width"]/div[2]/span')
            expect(desc).to_have_text(WIDE_DESC)
        else:
            pass

    # 문구(라벨) 클릭
    for name, value, key in wide_case:
        div_index = 2 if value == 0 else 1  # value 1 표준, value 2 넓게
        label = page.locator(
            f'xpath=//*[@id="skin-client-prefs-vector-feature-limited-width"]/div[2]/ul/li/div/form/div[{div_index}]/label/span'
        )
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-limited-width-value-{value}"]')
        label.click()
        expect(radio).to_be_checked()
        _expect_html_class_contains(page, key)

# SC5: 너비 선택 후 새 탭에서 유지 확인
def SC5(page, context):
    for name, value, _ in wide_case:
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-limited-width-value-{value}"]')
        radio.click()
        expect(radio).to_be_checked()

        new_page = context.new_page()
        new_page.goto(HOME)
        new_radio = new_page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-limited-width-value-{value}"]')
        expect(new_radio).to_be_checked()
        new_page.close()

# SC6: 글 크기 해제 불가 & 복수 선택 불가
def SC6(page):
    for name, value in font_sizes:
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-custom-font-size-value-{value}"]')
        radio.click()
        expect(radio).to_be_checked()

        # 재선택해도 체크 유지
        radio.click()
        expect(radio).to_be_checked()

        _expect_html_class_contains(page, f"vector-feature-custom-font-size-clientpref-{value}")

        # 같은 그룹의 다른 항목은 미체크
        for other_name, other_value in font_sizes:
            if other_value == value:
                continue
            other_radio = page.locator(
                f'xpath=//*[@id="skin-client-pref-vector-feature-custom-font-size-value-{other_value}"]'
            )
            expect(other_radio).not_to_be_checked()

# SC7: 너비 해제 불가 & 복수 선택 불가
def SC7(page):
    for name, value, key in wide_case:
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-vector-feature-limited-width-value-{value}"]')
        radio.click()
        expect(radio).to_be_checked()

        radio.click()  # 재선택
        expect(radio).to_be_checked()

        _expect_html_class_contains(page, key)

        for other_name, other_value, _ in wide_case:
            if other_value == value:
                continue
            other_radio = page.locator(
                f'xpath=//*[@id="skin-client-pref-vector-feature-limited-width-value-{other_value}"]'
            )
            expect(other_radio).not_to_be_checked()

# SC8: 테마(색상) 해제 불가 & 복수 선택 불가
def SC8(page):
    for name, value in theme_case:
        radio = page.locator(f'xpath=//*[@id="skin-client-pref-skin-theme-value-{value}"]')
        radio.click()
        expect(radio).to_be_checked()

        radio.click()  # 재선택
        expect(radio).to_be_checked()

        for other_name, other_value in theme_case:
            if other_value == value:
                continue
            other_radio = page.locator(f'xpath=//*[@id="skin-client-pref-skin-theme-value-{other_value}"]')
            if other_radio.count():
                expect(other_radio).not_to_be_checked()

# (옵션) 사이드 패널 숨기기 버튼 흐름
def open_appearance_button(page):
    btn = page.locator('xpath=/html/body/div[2]/div/div[3]/main/div[2]/div/nav[2]/div/div/div[1]/button[2]')
    btn.wait_for(state="visible")
    btn.click()

    pop = page.locator('xpath=/html/body/div[1]/header/div[2]/nav/div[1]/nav/div[2]/div[1]/div')
    print("popdesc:", pop.get_attribute("popdesc"))

    widthwide_radio = page.locator('xpath=//*[@id="skin-client-pref-vector-feature-limited-width-value-0"]')
    widthwide_radio.click()
    expect(widthwide_radio).to_be_checked()

    widthwide_desc = page.locator('xpath=//*[@id="skin-client-prefs-vector-feature-limited-width"]/div[2]/span')
    expect(widthwide_desc).to_have_text(WIDE_DESC)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(HOME)

        SC1(page)
        SC2(page)
        SC3(page, context)
        SC4(page)
        SC5(page, context)
        SC6(page)
        SC7(page)
        SC8(page)

        browser.close()
