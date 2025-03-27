import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import ScheduleRequest
from openai_service import generate_travel_plan

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-schedule")
def generate_schedule(request: ScheduleRequest):
    result = generate_travel_plan(
        request.city, request.days, request.people, request.style
    )
    return result  # ✅ 여기 수정

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5005, reload=True)
