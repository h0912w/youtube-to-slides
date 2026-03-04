# Agent B: 자막(Transcript) 서비스 개발

`app/services/transcript.py` 파일을 개발/수정하는 서브에이전트입니다.

## 담당 범위

- `get_transcript(video_id: str, language: str = "ko") -> list[dict]`
  - 자막 추출 (한국어 → 영어 → 자동생성 자막 순서로 폴백)
  - 반환: `[{"text": ..., "start": ..., "duration": ...}, ...]`
  - 자막 없으면 RuntimeError
- `chunk_transcript(transcript: list[dict], chunk_minutes: int = 3) -> list[str]`
  - 시간 단위 청크 분할
  - 빈 리스트 입력 시 빈 리스트 반환

## 규칙

- `youtube_transcript_api` 패키지 사용
- 다른 서비스 모듈을 import하지 않음 (독립 모듈)
- 테스트: `tests/test_transcript.py`

## 작업 지시

사용자의 요청에 따라 `app/services/transcript.py`를 수정하세요.
수정 후 `python -m pytest tests/test_transcript.py -v`로 테스트를 실행하세요.
