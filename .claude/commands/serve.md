# 서버 실행 확인

FastAPI 서버가 정상 동작하는지 확인합니다.

## 작업

1. `uvicorn app.main:app --port 8000`으로 서버 시작
2. `/health` 엔드포인트 호출하여 `{"status": "ok"}` 확인
3. 문제가 있으면 진단 및 수정
