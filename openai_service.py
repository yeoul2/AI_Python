import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()
api_key = os.getenv("AI_API_KEY")

# OpenAI 클라이언트 객체 생성
client = OpenAI(api_key=api_key)

# GPT를 호출해 여행 일정을 생성하는 함수
def generate_travel_plan(city, days, people, style=None):
    """
    사용자 입력을 기반으로 GPT에게 여행 일정을 요청하고 JSON으로 반환
    """

    # 프롬프트 조건: 스타일 유무에 따라 다르게 구성
    if style:
        prompt = f"""{people}명이 {days}일 동안 {city}로 여행을 갈 예정이야.
{style} 컨셉의 일정으로 구성해줘.
"""
    else:
        prompt = f"""{people}명이 {days}일 동안 {city}로 여행을 갈 예정이야.
여행 스타일은 너가 알아서 판단해서 구성해줘.
"""

    # 공통 조건 추가
    prompt += """
결과는 반드시 JSON 형식으로 아래 구조를 따르도록 출력해줘:
※ JSON을 문자열처럼 출력하지 말고 실제 JSON 배열 그대로 출력해줘.

[
  {
    "day": 1,
    "time": "09:00",
    "category": "명소 방문",
    "description": "서울 주요 관광지 방문"
  },
  ...
]

조건:
- 하루에 약 5~6개의 일정만 만들어줘
- 시간은 HH:MM 형식으로 표시해줘 (예: 09:00, 14:30)
- category는 예: 아침, 점심, 저녁, 명소 방문, 문화 체험 등
- description은 장소에서 하는 일을 간결하게 작성
- JSON 문법 오류 없이 정확하게 작성 (시스템이 바로 파싱할 거야)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 여행 일정 기획 전문가야."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        return {"schedule": parsed}

    except Exception as e:
        return {"error": f"❌ 오류 발생: {e}"}
