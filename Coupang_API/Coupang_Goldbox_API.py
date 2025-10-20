import hmac
import hashlib
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()  # .env에서 환경변수 로드

COUPANG_ACCESS_KEY = os.getenv("COUPANG_ACCESS_KEY")
COUPANG_SECRET_KEY = os.getenv("COUPANG_SECRET_KEY")
COUPANG_SUB_ID = os.getenv("COUPANG_SUB_ID")

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
        if data and "shortenUrl" in data[0]:
            return data[0]["shortenUrl"]
        return None

    def get_goldbox_products(self):
        method = "GET"
        endpoint = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/goldbox"
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
        if isinstance(jsondata, dict) and "data" in jsondata:
            if isinstance(jsondata["data"], dict):
                return jsondata["data"].get("productData", [])
            elif isinstance(jsondata["data"], list):
                return jsondata["data"]
        return []

    def get_goldbox_products_with_deeplink(self, sub_id=None):
        products = self.get_goldbox_products()
        results = []
        for product in products:
            product_id = product.get("productId")
            if not product_id:
                continue
            original_url = f"https://www.coupang.com/vp/products/{product_id}"
            deeplink = self.get_deeplink(original_url, sub_id)
            product["deeplink"] = deeplink if deeplink else original_url
            results.append(product)
        return results
