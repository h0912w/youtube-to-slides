# Agent C: AI 요약(Summarizer) 서비스 개발

`app/services/summarizer.py` 파일을 개발/수정하는 서브에이전트입니다.

## 담당 범위

- `summarize_for_slides(chunks: list[str], video_title: str) -> list[dict]`
  - Zhipu AI GLM-4-Flash(무료)로 자막 청크 → 슬라이드 구조 변환
  - 반환: `[{"title": "...", "bullets": ["...", "...", ...]}, ...]`

## 규칙

- `zhipuai` 패키지, `ZhipuAI(api_key=...).chat.completions.create(model="glm-4-flash", ...)`
- `app.config.settings`에서 ZHIPU_API_KEY 가져옴
- 슬라이드당 제목 + 불릿 3~5개
- 총 5~15장
- 한국어 출력
- JSON 형태로 반환
- AI API 응답 파싱 실패 시 적절한 에러 처리

## 작업 지시

사용자의 요청에 따라 `app/services/summarizer.py`를 수정하세요.
API 키가 필요하므로 단위 테스트는 mock을 사용하세요.
