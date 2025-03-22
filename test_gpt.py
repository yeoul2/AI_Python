# test_gpt.py

from openai_service import generate_travel_plan

# 테스트용 사용자 입력
city = "도쿄"
days = 3
people = 2
style = "먹방 중심"

# AI 일정 생성 호출
result = generate_travel_plan(city, days, people, style)

# 결과 출력
print("📅 생성된 여행 일정:\n")
print(result)
