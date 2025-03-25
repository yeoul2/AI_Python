import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()
api_key = os.getenv("AI_API_KEY")

# OpenAI 클라이언트 객체 생성
client = OpenAI(api_key=api_key)


# 여행 일정 생성 함수
def generate_travel_plan(city_or_country, days, people, style=None):
    """
    사용자 입력값을 기반으로 GPT에게 여행 일정을 요청하고,
    JSON 형태로 응답받아 파싱하여 반환하는 함수
    """

    # 국가가 입력되었을 때, 해당 국가의 주요 도시를 포함하도록 프롬프트 작성
    if style:
        prompt = f"{people}명이 {days}일 동안 {city_or_country}로 여행을 갈 예정이야.\n{style} 테마로 구성해줘."
    else:
        prompt = f"{people}명이 {days}일 동안 {city_or_country}로 여행을 갈 예정이야.\n여행 스타일은 너가 알아서 구성해줘."

    # 공통 조건 추가
    prompt += f"""
    (도시 입력이 없는 경우, 그 나라의 주요 도시를 기준으로 일정을 생성해줘)

    결과는 반드시 JSON 형식으로 아래 구조를 따르도록 출력해줘:

    [
      {{
        "day": 1,
        "time": "09:00",                  // 도착 시간
        "place": "센소지",                 // 장소 이름
        "description": "사원 관광",        // 활동 설명
        "moveType": "지하철",              // 이동 수단
        "from": "숙소",                    // 출발 지역
        "to": "센소지",                    // 도착 지역
        "duration": "15분"                 // 이동 시간
      }},
      ...
    ]
    
    조건:
    - 하루에 약 5~6개의 일정만 만들어줘
    - 시간은 HH:MM 형식으로 표시해줘 (예: 09:00, 14:30)
    - 장소 이름은 실제 존재하는 장소로
    - 이동 수단은 도보, 자차, 대중교통 중 하나로 표기
    - 첫 일정도 반드시 출발지와 목적지를 포함할 것 (숙소에서 첫 장소로 이동)
    - JSON 문법 오류 없이 정확하게 작성 (시스템이 바로 파싱할 거야)
    """

    try:
        # GPT 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 여행 일정 기획 전문가야."},
                {"role": "user", "content": prompt.strip()},
            ],
            temperature=0.7,
        )

        # 응답에서 텍스트 추출
        content = response.choices[0].message.content.strip()

        # JSON 형식으로 파싱하여 반환
        parsed = json.loads(content)
        return {"schedule": parsed}

    except Exception as e:
        # GPT 응답 실패 시 에러 반환
        return {"error": f"❌ GPT 오류 발생: {str(e)}"}
