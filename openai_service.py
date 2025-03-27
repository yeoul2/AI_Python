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
    return None, None


# 🧭 이동 시간 및 수단 보완 함수 (Google Directions API)
def get_duration_and_mode(from_coord, to_coord):
    try:
        directions = gmaps.directions(
            origin=from_coord, destination=to_coord, mode="transit", language="ko"
        )
        if directions:
            leg = directions[0]["legs"][0]
            duration = leg["duration"]["text"]
            steps = leg["steps"]
            mode = steps[0]["travel_mode"].lower()
            if mode == "walking":
                return duration, "도보"
            elif mode == "driving":
                return duration, "자차"
            elif mode == "transit":
                vehicle = (
                    steps[0]
                    .get("transit_details", {})
                    .get("line", {})
                    .get("vehicle", {})
                    .get("type", "")
                    .lower()
                )
                if "bus" in vehicle:
                    return duration, "버스"
                elif "subway" in vehicle or "metro" in vehicle:
                    return duration, "지하철"
                else:
                    return duration, "대중교통"
        return "이동 시간 없음", "도보"
    except Exception as e:
        print(f"[⛔ 이동 정보 실패] {from_coord} → {to_coord}: {e}")
        return "이동 시간 없음", "도보"


# ✨ 여행 일정 생성 함수
def generate_travel_plan(city_or_country, days, people, style=None):
    if style:
        prompt = f"{people}명이 {days}일 동안 {city_or_country}로 여행을 갈 예정이야.\n여행 테마는 {style}야."
    else:
        prompt = f"{people}명이 {days}일 동안 {city_or_country}로 여행을 갈 예정이야.\n테마는 네가 추천해줘."

    prompt += """

아래 형식처럼 'activities' 배열을 포함한 JSON 형태로 결과를 반환해줘:

[
  {
    "day": "DAY 1",
    "activities": [
      {
        "time": "09:00",
        "title": "경복궁",
        "desc": "조선시대 궁궐 방문",
        "from": "호텔",
        "to": "경복궁",
        "moveType": "지하철",
        "duration": "20분",
        "latitude": 37.5796,
        "longitude": 126.9770
      }
    ]
  }
]

⚠️ 조건:
- 'activities' 배열은 필수
- 각 항목에 time, title, desc, from, to, moveType, duration, latitude, longitude 포함
- 위치 불명확하면 대표 장소 좌표 임의 삽입
- 하루 4~6개 activity
- 출력은 순수 JSON만
- 모든 텍스트는 반드시 한국어
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
        parsed = json.loads(content)

        # 🔧 좌표 및 이동 정보 보완
        for day in parsed:
            if "activities" in day:
                activities = day["activities"]
                for i, activity in enumerate(activities):
                    place_name = f"{city_or_country} {activity.get('to') or activity.get('title')}"
                    lat, lng = get_coordinates(place_name)
                    activity["latitude"] = lat
                    activity["longitude"] = lng

                    if i > 0:
                        prev = activities[i - 1]
                        if prev["latitude"] and prev["longitude"] and lat and lng:
                            duration, move_type = get_duration_and_mode(
                                (prev["latitude"], prev["longitude"]), (lat, lng)
                            )
                            activity["duration"] = duration
                            activity["moveType"] = move_type
                        else:
                            activity["duration"] = "이동 시간 없음"
                            activity["moveType"] = "도보"

        return parsed

    except Exception as e:
        return {"error": f"❌ GPT 오류: {str(e)}"}
