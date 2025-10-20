# tistory_publish_perplexity.py

import os

import requests
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright
from Coupang_API.Coupang_Seaerch_API import CoupangMgr
import re
load_dotenv()  # .env 파일에서 환경변수 읽어오기

TISTORY_EMAIL = os.getenv("TISTORY_EMAIL")
TISTORY_PASSWORD = os.getenv("TISTORY_PASSWORD")
COUPANG_ACCESS_KEY = os.getenv("COUPANG_ACCESS_KEY")
COUPANG_SECRET_KEY = os.getenv("COUPANG_SECRET_KEY")
COUPANG_SUB_ID = os.getenv("COUPANG_SUB_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

BLOG_MANAGE_URL = ( #n-infor-moa2
    "https://www.tistory.com/auth/login"
    "?redirectUrl=https%3A%2F%2Fn-infor-moa2.tistory.com%2Fmanage%2Fposts"
)
#BLOG_MANAGE_URL = ( #n-infor-moa
#    "https://n-infor-moa.tistory.com/manage"
#
#)

def call_perplexity_api(query: str) -> str:
    import requests
    endpoint = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": query}]
    }
    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        result = response.json()
        spec_summary = result['choices'][0]['message']['content']
        if not spec_summary:
            return "<p>상세 스펙을 자동으로 가져오지 못했습니다.</p>"
        return spec_summary
    except requests.exceptions.RequestException as e:
        print(f"Perplexity API 호출 오류: {e}")
        return (
            "<p>상세 스펙을 자동으로 가져오지 못했습니다.</p>"
            "<p>프로세서, 메모리, 저장용량, 디스플레이, 무게 등 주요 스펙을 직접 입력해 주세요.</p>"
        )


def get_real_image_url(image_url):
    try:
        resp = requests.head(image_url, allow_redirects=True, timeout=5)
        resp.raise_for_status()
        return resp.url
    except Exception:
        return image_url

def get_product_specs(product_name: str) -> str:
    """Perplexity API로부터 상품 스펙을 받아옴"""
    query = (
        f"{product_name}의 주요 스펙을 구글 SEO에 맞춰서 간결하게 HTML <ul><li> 목록으로 작성해줘"

    )
    print(f"query: "+query)
    return call_perplexity_api(query)

def remove_codeblock_markup(text: str) -> str:
    """```html`````` 코드블록 표기 제거"""
    return text.replace("``````", "").strip()


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
<p>[##_Image|kage@cyUIgT/dJMb9YJ0y8z/AAAAAAAAAAAAAAAAAAAAANxAtwHUPwXwSMUO3r9lwYprlTX6L_F8Tlmh2Tz6uXbg/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&amp;expires=1761922799&amp;allow_ip=&amp;allow_referer=&amp;signature=GRe0sMZbMnUWcCmFhEk9ye%2Bu4Zk%3D|CDM|1.3|{"originWidth":890,"originHeight":43,"style":"alignCenter","filename":"티스토리쿠팡문구.png"}_##]</p>
<style>
  .product-table { width:100%; border-collapse:collapse; margin:20px 0; }
  .product-table th, .product-table td {
    border:1px solid #ddd; padding:12px; text-align:center;
  }
  .product-table th { background:#f5f5f5; font-weight:bold; }
  .product-table img { max-width:150px; height:auto; display:block; margin:0 auto; }
  .product-name {
    max-width:200px;
    word-break: break-word;
  }
  .btn-buy {
  background: #f0f0f0;  /* 연한 회색 */
  color: #666;          /* 글자색도 조금 어두운 회색으로 조절 */
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
}
.btn-buy:hover {
  background: #dcdcdc;  /* 마우스 오버 시 조금 더 진한 회색 */
}
  .product-detail { margin:40px 0; padding:20px; background:#f9f9f9; border-radius:8px; }
  .product-detail h3 { margin-bottom:10px; color:#333; }
  .disclaimer { font-size:0.85em; color:#999; text-align:center; margin-top:30px; }
</style>

<h2>오늘의 추천 상품</h2>
<table class="product-table">
  <thead>
    <tr>
      <th>순번</th><th>제품 이미지</th><th>제품명</th><th>제품 가격</th><th>구매</th>
    </tr>
  </thead>
  <tbody>
"""
    seen = set()
    unique_products = []
    for p in products_info:
        if p["product_name"] not in seen:
            seen.add(p["product_name"])
            unique_products.append(p)

    for i, product in enumerate(unique_products, 1):
        img_url = get_real_image_url(product["product_image"])
        content += f"""    <tr>
      <td>{i}</td>
      <td><img src="{img_url}" data-ke-src="{img_url}" alt="{product['product_name']}"/></td>
      <td class="product-name">{product['product_name']}</td>
      <td>₩{product['product_price']:,}</td>
      <td><a href="{product['coupang_deeplink']}" target="_blank" class="btn-buy">구매하기</a></td>
    </tr>
"""
    content += """  </tbody>
</table>

<h2>상세 제품 스펙</h2>
"""
    for i, product in enumerate(unique_products, 1):
        specs_raw = get_product_specs(product["product_name"])
        specs_cleaned = clean_text(specs_raw)
        content += f"""
<div class="product-detail">
  <h3>{i}. {product['product_name']}</h3>
  {specs_cleaned}
</div>
"""
    content += """
<p class="disclaimer">
  ※ 이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
</p>
"""
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

        #page.once("dialog", lambda dialog: dialog.dismiss())
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
            for tag in tags:
                tag_input.fill(tag)
                tag_input.press("Enter")

        page.get_by_role("button", name="임시저장", exact=True).click()
        print("블로그 포스팅 완료")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        context.close()
        browser.close()

#단독 키워드
#def main():
#    keyword = input("검색할 키워드를 입력하세요: ")
#
#    mgr = CoupangMgr(COUPANG_ACCESS_KEY, COUPANG_SECRET_KEY)
#    products_info = mgr.get_product_info_for_blog(keyword, limit=5, sub_id=COUPANG_SUB_ID)
#    if not products_info:
#        print("상품 정보를 가져오지 못했습니다.")
#        return
#
#    title = f"{keyword} 추천 상품 TOP {len(products_info)} - {datetime.now():%Y년 %m월 %d일}"
#
#    # 제품명에서 태그 추출 (예: 공백 기준 분리 후 짧은 키워드만)
#    product_tags = []
#    for p in products_info:
#        # 긴 제품명은 띄어쓰기 기준으로 적당히 분리, 중복 제거
#        words = p["product_name"].split()
#        for w in words:
#            if len(w) >= 2 and w not in product_tags:
#                product_tags.append(w)
#
#    # 키워드 기반 태그도 추가
#    related_tags = [keyword, "쿠팡", "추천", "리뷰", "가성비", "인기상품"]
#
#    # 중복 제외해 최대 10개 태그 조합
#    tags = []
#    for t in product_tags + related_tags:
#        if t not in tags:
#            tags.append(t)
#        if len(tags) >= 10:
#            break
#
#    content = create_blog_content(products_info)
#
#    with sync_playwright() as pw:
#        publish_to_tistory(pw, title, content, tags)

#여러 키워드
def main():
    keywords_input = input("검색할 키워드를 여러 개 입력하세요 (쉼표로 구분): ")
    keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

    if not keywords:
        print("입력된 키워드가 없습니다.")
        return

    mgr = CoupangMgr(COUPANG_ACCESS_KEY, COUPANG_SECRET_KEY)
    for keyword in keywords:
        products_info = mgr.get_product_info_for_blog(keyword, limit=5, sub_id=COUPANG_SUB_ID)
        if not products_info:
            print("상품 정보를 가져오지 못했습니다.")
            return

        title = f"{keyword} 추천 상품 TOP {len(products_info)} - {datetime.now():%Y년 %m월 %d일}"

        # 제품명에서 태그 추출 (예: 공백 기준 분리 후 짧은 키워드만)
        product_tags = []
        for p in products_info:
            # 긴 제품명은 띄어쓰기 기준으로 적당히 분리, 중복 제거
            words = p["product_name"].split()
            for w in words:
                if len(w) >= 2 and w not in product_tags:
                    product_tags.append(w)

        # 키워드 기반 태그도 추가
        related_tags = [keyword, "쿠팡", "추천", "리뷰", "가성비", "인기상품"]

        # 중복 제외해 최대 10개 태그 조합
        tags = []
        for t in product_tags + related_tags:
            if t not in tags:
                tags.append(t)
            if len(tags) >= 10:
                break

        content = create_blog_content(products_info)

        with sync_playwright() as pw:
            publish_to_tistory(pw, title, content, tags)


if __name__ == "__main__":
    main()