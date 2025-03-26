from pydantic import BaseModel
from typing import Optional


# 여행 일정 요청에 사용될 데이터 구조
class ScheduleRequest(BaseModel):
    city: str
    days: int
    people: int
    style: str = ""
