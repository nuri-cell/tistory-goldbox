# Coupang_Seaerch_API.py

import hmac
import hashlib
import os
import time
import requests
import urllib.parse
from dotenv import load_dotenv


load_dotenv()  # .env 파일에서 환경변수 읽어오기

TISTORY_EMAIL = os.getenv("TISTORY_EMAIL")
TISTORY_PASSWORD = os.getenv("TISTORY_PASSWORD")
COUPANG_ACCESS_KEY = os.getenv("COUPANG_ACCESS_KEY")
COUPANG_SECRET_KEY = os.getenv("COUPANG_SECRET_KEY")
COUPANG_SUB_ID = os.getenv("COUPANG_SUB_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

class CoupangMgr:
    def __init__(self, access_key, secret_key):
        self.DOMAIN = "https://api-gateway.coupang.com"
        self.access_key = access_key
        self.secret_key = secret_key

    def generate_hmac(self, method, url):
        path, *query = url.split("?")
        os.environ["TZ"] = "GMT+0"
        timestamp = time.strftime('%y%m%d') + 'T' + time.strftime('%H%M%S') + 'Z'
        message = timestamp + method + path + (query[0] if query else "")
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return f"CEA algorithm=HmacSHA256, access-key={self.access_key}, signed-date={timestamp}, signature={signature}"

    def get_products_data(self, keyword, limit):
        method = "GET"
        endpoint = (
            "/v2/providers/affiliate_open_api/apis/openapi/products/search"
            f"?keyword={urllib.parse.quote(keyword)}&limit={limit}"
        )
        url = self.DOMAIN + endpoint
        authorization = self.generate_hmac(method, endpoint)

        response = requests.get(
            url,
            headers={
                "Authorization": authorization,
                "Content-Type": "application/json;charset=UTF-8"
            }
        )
        response.raise_for_status()
        jsondata = response.json()
        return jsondata.get("data", {}).get("productData", [])

    def get_deeplink(self, original_url, sub_id=None):
        method = "POST"
        endpoint = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
        url = self.DOMAIN + endpoint
        authorization = self.generate_hmac(method, endpoint)

        payload = {
            "coupangUrls": [original_url]
        }
        if sub_id:
            payload["subId"] = sub_id

        response = requests.post(
            url,
            headers={
                "Authorization": authorization,
                "Content-Type": "application/json;charset=UTF-8"
            },
            json=payload
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        if data:
            return data[0].get("shortenUrl")
        return None

    def get_product_info_for_blog(self, keyword, limit=10, sub_id=COUPANG_SUB_ID):
        """
        블로그 작성용 상품 정보를 반환하는 메서드
        """
        products = self.get_products_data(keyword, limit)
        print(f"실제 받아온 상품 수: {len(products)}")

        blog_products = []

        for blog_data in products:
            product_id = blog_data.get("productId")
            product_name = blog_data.get("productName")
            product_price = blog_data.get("productPrice")
            product_image = blog_data.get("productImage")
            original_url = f"https://www.coupang.com/vp/products/{product_id}"

            coupang_deeplink = self.get_deeplink(original_url, sub_id)

            # 딥링크가 없으면 건너뜀
            if not coupang_deeplink:
                print(f"딥링크가 없어 제외된 제품: {blog_data.get('productName')}")
                continue

            blog_products.append({
                "product_id": product_id,
                "product_name": product_name,
                "product_price": product_price,
                "product_image": product_image,
                "coupang_deeplink": coupang_deeplink
            })

        return blog_products

