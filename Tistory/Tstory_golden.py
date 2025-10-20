import os
import re
from datetime import datetime
from dotenv import load_dotenv
from typing import List
from playwright.sync_api import Playwright, sync_playwright
from Coupang_API.Coupang_Goldbox_API import CoupangMgr
import requests

load_dotenv()

TISTORY_EMAIL = os.getenv("TISTORY_EMAIL")
TISTORY_PASSWORD = os.getenv("TISTORY_PASSWORD")
COUPANG_ACCESS_KEY = os.getenv("COUPANG_ACCESS_KEY")
COUPANG_SECRET_KEY = os.getenv("COUPANG_SECRET_KEY")
COUPANG_SUB_ID = os.getenv("COUPANG_SUB_ID")

BLOG_MANAGE_URL = (
    "https://www.tistory.com/auth/login"
    "?redirectUrl=https%3A%2F%2Fn-infor-moa2.tistory.com%2Fmanage%2Fposts"
)

def get_real_image_url(image_url):
    try:
        resp = requests.head(image_url, allow_redirects=True, timeout=5)
        resp.raise_for_status()
        return resp.url
    except Exception:
        return image_url

def clean_text(text: str) -> str:
    # 코드블록 전체 제거 (``````)
    text = re.sub(r'``````', '', text, flags=re.DOTALL)

    # 대괄호 안 숫자 제거 ([숫자])
    text = re.sub(r'\[\d+\]', '', text)

    # [주요 근거: 숫자] 제거
    text = re.sub(r'\[주요 근거: \d+\]', '', text)

    # ** 강조 마크다운 제거
    text = text.replace('**', '')

    # ```
    text = re.sub(r'```[\s]*', '', text)

    return text.strip()

def create_blog_content(products_info):
    content = """
<p>[##_Image|kage@cyUIgT/dJMb9YJ0y8z/AAAAAAAAAAAAAAAAAAAAANxAtwHUPwXwSMUO3r9lwYprlTX6L_F8Tlmh2Tz6uXbg/img.png|CDM|1.3|{"originWidth":890,"originHeight":43,"style":"alignCenter","filename":"티스토리쿠팡문구.png"}_##]</p>

<!-- Coupang 광고 배너 추가 -->
<a href="https://link.coupang.com/a/cXLbn2" target="_blank" referrerpolicy="unsafe-url">
  <img src="https://ads-partners.coupang.com/banners/933834?subId=&traceId=V0-301-969b06e95b87326d-I933834&w=728&h=90" alt="">
</a>

<!-- 문구 추가 -->
<div style="background:#fff3cd; border-left:4px solid #ffc107; padding:15px; margin:20px 0; line-height:1.8;">
  <p style="margin:0 0 10px 0; font-size:16px; font-weight:bold; color:#333;">
    ⏰ 매일 자정, 단 하루만 열리는 특가의 문! 골드박스에서 최대 90% 할인된 인기 상품을 만나보세요.
  </p>
  <p style="margin:0 0 10px 0; font-size:16px; color:#555;">
    🔥 한정 수량, 한정 시간! 놓치면 내일까지 기다려야 하는 오늘만의 초특가 딜을 지금 바로 확인하세요.
  </p>
  <p style="margin:0; font-size:16px; color:#555;">
    💎 베스트셀러부터 숨은 보석 아이템까지, 매일 새로운 상품이 골드박스에서 여러분을 기다립니다!
  </p>
</div>

<style>
  .product-table { width:100%; border-collapse:collapse; margin:20px 0; }
  .product-table th, .product-table td { border:1px solid #ddd; padding:12px; text-align:center; }
  .product-table th { background:#f5f5f5; font-weight:bold; }
  .product-table img { max-width:150px; height:auto; display:block; margin:0 auto; }
  .product-name { max-width:200px; word-break: break-word; }
  .btn-buy {
    background: #f0f0f0;  
    color: #666;          
    padding: 8px 16px;
    border-radius: 4px;
    text-decoration: none;
  }
  .btn-buy:hover { background: #dcdcdc; }
  .disclaimer { font-size:0.85em; color:#999; text-align:center; margin-top:30px; }
</style>

<h2>오늘의 추천 상품</h2>
<table class="product-table">
  <thead>
    <tr><th>순번</th><th>제품 이미지</th><th>제품명</th><th>제품 가격</th><th>구매</th></tr>
  </thead>
  <tbody>
"""
    seen = set()
    unique_products = []
    for p in products_info:
        if p.get("productName") not in seen:
            seen.add(p.get("productName"))
            unique_products.append(p)

    for i, product in enumerate(unique_products, 1):
        img_url = get_real_image_url(product.get("productImage", ""))
        link = product.get("deeplink") or product.get("productUrl", "#")
        content += f"""    <tr>
      <td>{i}</td>
      <td><img src="{img_url}" data-ke-src="{img_url}" alt="{product.get('productName', '')}"/></td>
      <td class="product-name">{product.get('productName', '')}</td>
      <td>{int(product.get('productPrice', 0)):,}원</td>
      <td><a href="{link}" target="_blank" class="btn-buy">구매하기</a></td>
    </tr>
"""

    content += """  </tbody>
</table>

<p class="disclaimer">
  ※ 이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
</p>
"""

    return content

def publish_to_tistory(playwright: Playwright, title: str, content: str, tags: List[str] = None):
    browser = playwright.chromium.launch(headless=True)
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
        page.get_by_placeholder("제목을 입력하세요").press("Tab")
        page.locator("#html-editor-container").get_by_text("HTML더보기").press("Tab")
        page.locator("#html-editor-container").get_by_role("textbox").fill(content)

        if tags:
            tag_input = page.get_by_placeholder("태그입력")
            for tag in tags[:10]:  # 최대 10개만 입력
                tag_input.fill(tag)
                tag_input.press("Enter")

        page.get_by_role("button", name="임시저장", exact=True).click()
        print("블로그 포스팅 완료")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        context.close()
        browser.close()

def main():
    mgr = CoupangMgr(COUPANG_ACCESS_KEY, COUPANG_SECRET_KEY)
    products_info = mgr.get_goldbox_products_with_deeplink(COUPANG_SUB_ID)
    if not products_info:
        print("상품 정보를 가져오지 못했습니다.")
        return

    title = f"오늘의 골드박스 상품 추천 TOP {len(products_info)} - {datetime.now():%Y년 %m월 %d일} (매일 오전 7시 오픈,한정수량)"

    product_tags = set()
    for p in products_info:
        words = p.get("productName", "").split()
        product_tags.update([w for w in words if len(w) >= 2])
    related_tags = ["쿠팡", "골드박스", "추천", "특가", "핫딜"]
    tags = list(product_tags)[:7] + related_tags

    blog_content = create_blog_content(products_info)

    with sync_playwright() as pw:
        publish_to_tistory(pw, title, blog_content, tags)

if __name__ == "__main__":
    main()
