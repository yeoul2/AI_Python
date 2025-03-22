@echo off
echo 🚀 프로젝트 환경 설정 시작...

:: 1. 가상환경 생성
if not exist venv (
    echo 🔹 가상환경이 없습니다. 생성 중...
    python -m venv venv
)

:: 2. 가상환경 실행
call venv\Scripts\activate

:: 3. 패키지 설치
pip install -r requirements.txt

echo ✅ 프로젝트 설정 완료!
echo ------------------------------------------
echo ▶ FastAPI 서버 실행 명령어:
echo uvicorn main:app --reload --port=9009
pause
