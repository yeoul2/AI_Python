import os
import json
import googlemaps
from openai import OpenAI
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv()
api_key = os.getenv("AI_API_KEY")
google_maps_key = os.getenv("GOOGLE_API_KEY")

client = OpenAI(api_key=api_key)
gmaps = googlemaps.Client(key=google_maps_key)


# ⛳ 좌표 보완 함수
def get_coordinates(place_name):
    try:
        geocode_result = gmaps.geocode(place_name)
        if geocode_result and len(geocode_result) > 0:
            location = geocode_result[0]["geometry"]["location"]
            return location["lat"], location["lng"]
    except Exception as e:
        print(f"[좌표 변환 오류] {place_name}: {e}")

    print(f"[⚠️ 기본 좌표 사용] {place_name}")
    return 48.8566, 2.3522  # 파리 중심 좌표 기본값
    """ return None, None """


# ✨ 핵심 여행 일정 생성 함수
def generate_travel_plan(city_or_country, days, people, style=None):
    if style:
        prompt = f"{people}명이 {days}일 동안 {city_or_country}로 여행을 갈 예정이야.\n여행 테마는 {style}야."
    else:
        prompt = f"{people}명이 {days}일 동안 {city_or_country}로 여행을 갈 예정이야.\n테마는 네가 추천해줘."

    prompt += f"""
    
아래 형식처럼 'activities' 배열을 포함한 JSON 형태로 결과를 반환해줘:

[
  {{
    "day": "DAY 1",
    "activities": [
      {{
        "time": "09:00",
        "title": "경복궁",
        "desc": "조선시대 궁궐 방문",
        "from": "호텔",
        "to": "경복궁",
        "moveType": "지하철",
        "duration": "20분",
        "latitude": 37.5796,
        "longitude": 126.9770
      }},
      ...
    ]
  }},
  ...
]

⚠️ 조건:
- 반드시 'activities' 배열을 포함할 것 (절대 null 또는 빠지면 안 됨)
- 각 활동에는 반드시 위도(latitude)와 경도(longitude)를 포함할 것
- 위치가 명확하지 않으면 구글맵 기준 대표 좌표를 임의로 삽입해도 괜찮음
- 하루에 약 4~6개의 activity를 포함할 것
- 'from', 'to', 'duration', 'latitude', 'longitude'는 반드시 포함
- 출력은 JSON 외 텍스트 없이 순수 JSON만 출력
- 모든 출력 내용(title, desc 등)은 반드시 한국어로 작성해줘
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 여행 일정 기획 전문가야."},
                {"role": "user", "content": prompt.strip()},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()
        print("📦 GPT 응답 내용 확인:\n", content)  # ✅ GPT 응답 직접 출력
        parsed = json.loads(content)

        # 🔧 좌표 누락된 경우 Google Maps로 보완
        for day in parsed:
            if "activities" in day:
                for activity in day["activities"]:
                    # 📍 강제로 Google Maps 좌표 보완 실행
                    place_name = f"{city_or_country} {activity.get('to') or activity.get('title')}"
                    lat, lng = get_coordinates(place_name)
                    print(f"[좌표 보완] {place_name} → lat: {lat}, lng: {lng}")
                    try:
                        activity["latitude"] = float(lat)
                        activity["longitude"] = float(lng)
                    except:
                        print(f"[⚠️ 강제 좌표 삽입] {activity.get('title')}")
                        activity["latitude"] = 48.8566
                        activity["longitude"] = 2.3522

                    print(
                        f"📍 마커 위치 확인: {activity.get('title')} → lat: {activity['latitude']}, lng: {activity['longitude']}"
                    )

        return parsed  # ✅ 중첩 없이 단일 JSON 배열 반환

    except Exception as e:
        return {"error": f"❌ GPT 오류 발생: {str(e)}"}
