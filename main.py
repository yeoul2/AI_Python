import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import ScheduleRequest  # 사용자 요청 모델 (city, days, people, style)
from openai_service import generate_travel_plan  # OpenAI GPT 호출 함수

# FastAPI 애플리케이션 생성
app = FastAPI()

# CORS 설정 – 프론트엔드(React 등)에서 접근 가능하도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프론트 주소로 제한하려면 예: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# POST API 엔드포인트 – 여행 일정 생성 요청 처리
@app.post("/generate-schedule")
def generate_schedule(request: ScheduleRequest):
    """
    [POST] /generate-schedule

    📌 기능:
    - 사용자가 입력한 도시, 여행일 수, 인원수, 여행 스타일을 바탕으로
      GPT에게 여행 일정을 생성 요청하고 JSON 형식으로 반환

    📝 입력:
    - city: 여행 도시 (예: "도쿄")
    - days: 여행 기간 (예: 3)
    - people: 인원수 (예: 2)
    - style: 여행 스타일 (예: "맛집 중심")

    ✅ 출력:
    - schedule: GPT가 생성한 JSON 리스트 (day, time, category, description)
    """
    result = generate_travel_plan(
        request.city, request.days, request.people, request.style
    )
    return {"schedule": result}


# 개발용 서버 실행 설정 (포트 5005번 사용)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5005, reload=True)
