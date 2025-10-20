import requests
import os

api_key = os.getenv("PERPLEXITY_API_KEY", "").strip()
endpoint = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "sonar",
    "messages": [
        {"role": "user", "content": "삼성 갤럭시 워치 8 스펙 알려줘"}
    ]
}

response = requests.post(endpoint, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print(result['choices'][0]['message']['content'])
else:
    print("API 호출 실패:", response.status_code, response.text)
