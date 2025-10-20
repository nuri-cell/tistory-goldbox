from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, sync_playwright
import re
import time

# 네이버 블로그용 HTML 기본 서식 변환 함수
def html_to_naver_format(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')

    allowed_tags = ['p', 'br', 'strong', 'b', 'em', 'i', 'u', 'a', 'ul', 'ol', 'li']

    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()

    for a_tag in soup.find_all('a'):
        a_tag.attrs = {k: v for k, v in a_tag.attrs.items() if k == 'href'}
        a_tag['target'] = '_blank'

    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr not in ['href', 'target']:
                del tag.attrs[attr]

    return str(soup)

# 네이버 블로그 로그인 및 글쓰기 자동화 함수
def publish_naver_blog(playwright: Playwright, blog_id: str, username: str, password: str, title: str, html_content: str):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 네이버 블로그 메인 페이지 이동
    page.goto(f"https://blog.naver.com/{blog_id}")

    # 로그인 프레임 진입 및 로그인 수행
    login_frame = page.frame(name='mainFrame')
    login_frame.get_by_role("link", name="로그인").click()

    # 로그인 창 내 iframe 전환 (로그인 페이지 구조에 따라 다를 수 있음)
    time.sleep(2)  # 대기 (필요하면 더 견고한 웨이트 사용)

    # 아이디/비밀번호 입력
    page.get_by_label("아이디 또는 전화번호").fill(username)
    page.get_by_label("비밀번호").fill(password)
    page.get_by_role("button", name="로그인", exact=True).click()

    time.sleep(5)  # 로그인 처리 대기 (네트워크 및 2차 인증 이슈 고려)

    # 글쓰기 화면 진입
    page.locator("iframe[name=\"mainFrame\"]").content_frame.get_by_role("link", name="글쓰기").click()
    time.sleep(3)

    # 글쓰기 iframe 진입
    page.locator("iframe[name=\"mainFrame\"]").content_frame.get_by_role("button", name="닫기").click()
    time.sleep(6)

    write_frame =  page.locator("iframe[name=\"mainFrame\"]")

    # 제목 입력
    # 제목 입력창 셀렉터는 네이버가 바꾸면 수정 필요

    main_frame = page.frame(name="mainFrame")
    main_frame.wait_for_selector('div.se-documentTitle[data-ally-title="제목"] p')
    title_component = main_frame.locator('div.se-documentTitle[data-ally-title="제목"] p')
    title_component.click()
    title_component.type("원하는 제목 텍스트")  # 또는 evaluate 활용 가능

    # 본문 입력: 네이버 편집기 iframe 또는 콘텐츠 editable 영역
    # 네이버 에디터는 iframe으로 구성되어 있거나 div[contenteditable] 의 형태임을 확인하세요
    # 여기서는 예시로 contenteditable div에 직접 입력하는 방식 사용
    page.locator("iframe[name=\"mainFrame\"]").content_frame.get_by_text("글감과 함께 나의 일상을 기록해보세요!").click()
    #page.locator("iframe[name=\"mainFrame\"]").content_frame.locator("p").filter(has_text="글감과 함께 나의 일상을 기록해보세요!").click()

    content_area = page.locator("iframe[name=\"mainFrame\"]").content_frame.get_by_text("글감과 함께 나의 일상을 기록해보세요!")
    content_area.click()
    # 본문 내용이 길면 set_content()나 evaluate()로 innerHTML 직접 조작 가능
    write_frame.evaluate(f'''el => el.innerHTML = `{html_content}`''', content_area.element_handle())

    time.sleep(2)  # 입력 안정화 대기

    # 임시저장 또는 발행 버튼 클릭 (임시저장 예)
    save_button = write_frame.get_by_role("button", name="저장")
    save_button.click()

    time.sleep(3)  # 저장 처리 대기

    print("네이버 블로그 글쓰기가 완료되었습니다.")

    context.close()
    browser.close()

# 메인 실행 예시
def main():
    raw_html = """
    <h2>예시 제목</h2>
    <p>이것은 <strong>테스트</strong>용 <a href="https://google.com">링크</a>입니다.</p>
    <ul><li>첫 번째 항목</li><li>두 번째 항목</li></ul>
    """

    # HTML 변환
    converted_html = html_to_naver_format(raw_html)

    with sync_playwright() as pw:
        # 네이버 블로그 아이디, 네이버 로그인 아이디, 비밀번호, 블로그 글 제목, 내용
        publish_naver_blog(
            playwright=pw,
            blog_id="modu_info",  # 예시 블로그 ID
            username="modu_info",
            password="Poiure01!",
            title="테스트 글 제목",
            html_content=converted_html
        )

if __name__ == "__main__":
    main()
