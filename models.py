from pydantic import BaseModel
from typing import Optional

# 여행 일정 요청에 사용될 데이터 구조
class ScheduleRequest(BaseModel):
    city: str        # 여행 도시
    days: int        # 여행 일수
    people: int      # 여행 인원
    style: Optional[str] = None  # 여행 스타일 (선택 사항)
