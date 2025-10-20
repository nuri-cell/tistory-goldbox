# tistory_publish_perplexity.py

import os
import requests
import re
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright
from Coupang_API.Coupang_Seaerch_API import CoupangMgr
import time

# .env 로드 (python-dotenv 필요)
try:
    load_dotenv()
except ImportError:
    pass

TISTORY_EMAIL = os.getenv("TISTORY_EMAIL")
TISTORY_PASSWORD = os.getenv("TISTORY_PASSWORD")
COUPANG_ACCESS_KEY = os.getenv("COUPANG_ACCESS_KEY")
COUPANG_SECRET_KEY = os.getenv("COUPANG_SECRET_KEY")
COUPANG_SUB_ID = os.getenv("COUPANG_SUB_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
TOP_BANNER = """
<p>[##_Image|kage@bWEEfl/dJMb9N9C9RK/AAAAAAAAAAAAAAAAAAAAAJuPRXUXAqKp1U10mh8M00ybds8JLuFGhhi1mCf7hGk-/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&amp;expires=1761922799&amp;allow_ip=&amp;allow_referer=&amp;signature=GvxMCYdeCyMMVSTdF4pRu95bwQg%3D|CDM|1.3|{"originWidth":890,"originHeight":43,"style":"alignCenter","filename":"티스토리쿠팡문구.png"}_##]</p>
"""
BOTTOM_BANNER = """
<p>[##_Image|kage@cInCZQ/dJMb9OtVL3F/AAAAAAAAAAAAAAAAAAAAANu6WzJVoVaMrOvsOMdaLE6vq3xtFB6u2hKA-BqlWTZC/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&amp;expires=1761922799&amp;allow_ip=&amp;allow_referer=&amp;signature=C07VUwZEyMa4iZHRIK3RPx1mS6U%3D|CDM|1.3|{"originWidth":848,"originHeight":45,"style":"alignCenter","filename":"티스토리쿠팡문구2.png"}_##]</p>
"""

BLOG_MANAGE_URL = (
    "https://www.tistory.com/auth/login"
    "?redirectUrl=https%3A%2F%2Fn-infor-moa2.tistory.com%2Fmanage%2Fposts"
)

FIXED_TOP_IMAGE = """
<p>[##_Image|kage@cyUIgT/dJMb9YJ0y8z/AAAAAAAAAAAAAAAAAAAAANxAtwHUPwXwSMUO3r9lwYprlTX6L_F8Tlmh2Tz6uXbg/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&amp;expires=1761922799&amp;allow_ip=&amp;allow_referer=&amp;signature=GRe0sMZbMnUWcCmFhEk9ye%2Bu4Zk%3D|CDM|1.3|{"originWidth":890,"originHeight":43,"style":"alignCenter","filename":"티스토리쿠팡문구.png"}_##]</p>
"""

def call_perplexity_api(query: str, retries: int = 3, timeout: int = 60) -> str:
    """Perplexity API 호출: 타임아웃 시 재시도"""
    endpoint = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": query}]
    }
    print(query)
    for attempt in range(1, retries + 1):
        try:
            print(f">>> API 호출 시도 {attempt}/{retries}")
            res = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
            print(f">>> 응답 상태 코드: {res.status_code}")
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"] or ""
            print(">>> API 응답 내용 수신")
            return content
        except requests.exceptions.ReadTimeout:
            print(f"!!! ReadTimeout: {timeout}s 경과 (시도 {attempt})")
        except requests.exceptions.RequestException as e:
            print(f"!!! 요청 오류: {e} (시도 {attempt})")
        # 재시도 전 대기
        time.sleep(2)
    print("!!! API 호출 실패: 모든 재시도 소진")
    return ""


def remove_codeblock_markup(text: str) -> str:
    return text.replace("``````", "").strip()

def clean_text(text: str) -> str:
    """불필요한 마크업과 숫자 인라인 제거"""
    text = re.sub(r'\`\`\`', '', text)
    text = re.sub(r'\`\`\`\`\`\`', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[주요 근거: \d+\]', '', text)
    text = text.replace('**', '')
    return text.strip()

def get_real_image_url(image_url: str) -> str:
    try:
        resp = requests.head(image_url, allow_redirects=True, timeout=5)
        resp.raise_for_status()
        return resp.url
    except Exception:
        return image_url

def get_product_specs(names: List[str]) -> str:
    p1, p2 = names
    prompt = (
        f"{p1}와 {p2}를 비교하는 블로그 글을 작성해줘. "
        f"구글 SEO에 맞춰 AI 탐지 방어 문체로, 가독성이 좋게 "
        f"블로그 서론, 1~6번 소제목 각각의 HTML <table> 비교와 표 아래 5줄 상세 설명, "
        f"마무리 및 추천까지 모두 포함해 자연스럽고 정성스럽게 작성해줘."
    )
    raw = call_perplexity_api(prompt)
    print(raw)
    return clean_text(remove_codeblock_markup(raw))

def extract_image_url(product: Dict) -> str:
    # CoupangMgr 반환값의 키(product_image)에 맞추어 확장
    for key in (
        "product_image",      # Coupang_Seaerch_API.py 에서 사용되는 키
        "productImage",       # 혹시 카멜케이스로 내려오는 경우
        "image_url",
        "thumbnail",
        "imageUrl",
        "product_image_url"
    ):
        url = product.get(key)
        if isinstance(url, str) and url.startswith("http"):
            return url
    return ""

def normalize_product(item: any) -> Dict:
    if isinstance(item, list) and item:
        item = item[0]
    if isinstance(item, dict):
        return item
    raise ValueError(f"Unsupported product info type: {type(item)}")


def create_blog_content(products_info: List[Dict]) -> str:
    p1, p2 = products_info
    name1, name2 = p1["product_name"], p2["product_name"]
    price1, price2 = p1["product_price"], p2["product_price"]
    link1, link2 = p1["coupang_deeplink"], p2["coupang_deeplink"]

    # 배너 및 비교 테이블 HTML 준비
    compare_table = f"""
<table style="border-collapse: collapse; width: 100%; height: 85px;" border="1" data-ke-align="alignLeft" data-ke-style="style12">
  <tbody>
    <tr>
      <td style="text-align: center;">항목</td>
      <td style="text-align: center;">{name1}</td>
      <td style="text-align: center;">{name2}</td>
    </tr>
    <tr>
      <td style="text-align: center;">가격대</td>
      <td style="text-align: center;">₩{price1:,}</td>
      <td style="text-align: center;">₩{price2:,}</td>
    </tr>
    <tr>
      <td style="text-align: center;">구매하러 가기</td>
      <td style="text-align: center;"><a href="{link1}" target="_blank">{name1} 제품 구매하러 가기</a></td>
      <td style="text-align: center;"><a href="{link2}" target="_blank">{name2} 제품 구매하러 가기</a></td>
    </tr>
  </tbody>
</table>
"""

    # 1. 최상단 배너
    content = TOP_BANNER

    # 2. 맨 위 비교 테이블
    content += compare_table

    # 3. Perplexity API 본문(raw) 처리
    raw = get_product_specs([name1, name2])
    raw = re.sub(r'--##\s*(.+)', r'<h3 style="margin-top:2em;">\1</h3>', raw)
    raw = re.sub(r'##\s*(.+)', r'<h3 style="margin-top:2em;">\1</h3>', raw)
    raw = raw.replace("<h2>", '<h3 style="margin-top:2em;">').replace("</h2>", "</h3>")
    raw = re.sub(r'\sdata-ke-[^>]+', '', raw)

    # 4. 소제목 기준 섹션 분할 및 감싸기
    sections_html = ""
    for sec in re.split(r'(?=<h3)', raw):
        sec = sec.strip()
        if not sec:
            continue
        sections_html += '<section class="compare-section">\n'
        parts = re.split(r'(<h3[^>]*>.*?</h3>|<table[\s\S]+?</table>)', sec)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part.startswith("<h3"):
                sections_html += part + "\n"
            elif part.startswith("<table"):
                # 첫 번째 표와 동일한 속성 추가
                styled_table = re.sub(
                    r'^<table',
                    '<table style="border-collapse: collapse; width: 100%; height: auto;" border="1" data-ke-align="alignLeft" data-ke-style="style12"',
                    part,
                    count=1
                )
                sections_html += styled_table + "\n"
            else:
                for line in part.splitlines():
                    line = line.strip()
                    if line and not line.startswith("---"):
                        sections_html += f"<p>{line}</p>\n"
        sections_html += "</section>\n"

    content += sections_html

    # 5. 맨 아래 비교 테이블 재노출
    content += compare_table

    # 6. 최하단 제품 이미지 (딥링크 포함)
    url1, url2 = extract_image_url(p1), extract_image_url(p2)
    img1 = get_real_image_url(url1) if url1 else ""
    img2 = get_real_image_url(url2) if url2 else ""
    if img1 or img2:
        content += '<p style="text-align:center;">'
        if img1:
            content += f'<a href="{link1}" target="_blank"><img src="{img1}" alt="{name1}" width="258" height="258" style="margin-right:5%;"/></a>'
        if img2:
            content += f'<a href="{link2}" target="_blank"><img src="{img2}" alt="{name2}" width="258" height="258"/></a>'
        content += '</p>'

    return content









def publish_to_tistory(playwright: Playwright, title: str, content: str, tags: List[str] = None):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    try:
        page.goto(BLOG_MANAGE_URL)
        page.get_by_role("link", name="카카오계정으로 로그인").click()
        page.get_by_placeholder("카카오메일 아이디, 이메일, 전화번호 ").fill(TISTORY_EMAIL)
        page.get_by_placeholder("비밀번호").fill(TISTORY_PASSWORD)
        page.get_by_role("button", name="로그인", exact=True).click()

        page.locator("#mFeature").get_by_role("link", name="글쓰기").click()
        page.get_by_label("기본모드").get_by_role("button", name="기본모드").click()
        page.once("dialog", lambda dialog: dialog.accept())
        page.get_by_label("기본모드 마크다운 HTML").get_by_text("HTML").click()

        page.get_by_placeholder("제목을 입력하세요").fill(title)
        page.locator("#html-editor-container").get_by_role("textbox").fill(content)

        if tags:
            tag_input = page.get_by_placeholder("태그입력")
            for tag in tags:
                tag_input.fill(tag)
                tag_input.press("Enter")

        page.get_by_role("button", name="임시저장", exact=True).click()
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        context.close()
        browser.close()

def main():
    keywords = input("비교할 두 제품명을 입력하세요 (콤마로 구분): ")
    names = [k.strip() for k in keywords.split(",") if k.strip()]
    if len(names) != 2:
        print("두 개의 제품명을 정확히 입력해 주세요.")
        return

    mgr = CoupangMgr(COUPANG_ACCESS_KEY, COUPANG_SECRET_KEY)
    products_info = []
    for name in names:
        info_list = mgr.get_product_info_for_blog(name, limit=1, sub_id=COUPANG_SUB_ID)
        try:
            product = normalize_product(info_list)
        except ValueError as ex:
            print(f"{name} 정보 형태가 올바르지 않습니다:", ex)
            return
        # 디버깅 출력: 실제 키와 값 확인
        print(">>> 상품 정보 디버깅:", {
            "product_name": product.get("product_name"),
            "product_image": product.get("product_image"),
            "coupang_deeplink": product.get("coupang_deeplink")
        })
        if "product_name" not in product:
            print(f"{name} 정보에 'product_name' 키가 없습니다.")
            return
        products_info.append(product)

    title = f"{names[0]} vs {names[1]} 완벽 비교 - {datetime.now():%Y년 %m월 %d일}"
    tags = list({*names, "비교", "리뷰", "가성비", "쿠팡"})[:10]
    content = create_blog_content(products_info)

    with sync_playwright() as pw:
        publish_to_tistory(pw, title, content, tags)

if __name__ == "__main__":
    main()
