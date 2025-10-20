import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # .env 파일에서 환경변수 읽기

# 클라이언트 인스턴스 생성 (환경변수에서 API 키 자동 로드)
client = OpenAI()

def get_specs(query: str) -> str:
    # chat completions 호출
    response = client.chat.completions.create(
        model="gpt-4o",  # 또는 gpt-3.5-turbo
        messages=[{"role": "user", "content": query}],
        temperature=0.7,
        max_tokens=500
    )
    # 응답에서 메시지 내용 추출
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    specs = get_specs("삼성 갤럭시 워치 8 스펙 알려줘")
    print(specs)