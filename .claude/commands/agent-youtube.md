# Agent A: YouTube 서비스 개발

`app/services/youtube.py` 파일을 개발/수정하는 서브에이전트입니다.

## 담당 범위

- `extract_video_id(url: str) -> str` — 다양한 YouTube URL 형식에서 video ID 파싱
  - youtube.com/watch?v=, youtu.be/, youtube.com/embed/, youtube.com/shorts/
  - 잘못된 URL은 ValueError 발생
- `get_video_info(url: str) -> dict` — yt-dlp로 메타데이터 추출
  - 반환 키: title, description, duration, thumbnail, channel

## 규칙

- `yt_dlp` 패키지만 사용 (외부 API 호출 없음)
- 다른 서비스 모듈을 import하지 않음 (독립 모듈)
- 에러 처리: DownloadError → ValueError로 변환
- 테스트: `tests/test_youtube.py` 수정 시 함께 업데이트

## 작업 지시

사용자의 요청에 따라 `app/services/youtube.py`를 수정하세요.
수정 후 `python -m pytest tests/test_youtube.py -v`로 테스트를 실행하세요.
