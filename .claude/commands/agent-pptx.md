# Agent D: PPT 생성(PPTX Builder) 서비스 개발

`app/services/pptx_builder.py` 파일을 개발/수정하는 서브에이전트입니다.

## 담당 범위

- `create_pptx(slides_data: list[dict], video_title: str, output_path: str) -> str`
  - PPT 파일 생성 후 저장 경로 반환

## 디자인 스펙

- 슬라이드 크기: 13.333 x 7.5 인치 (와이드스크린)
- **표지**: 다크 배경(#1A1A2E), 흰색 제목 40pt, 중앙 정렬
- **내용**: 흰색 배경, 제목 28pt(#1A1A2E), 파란 구분선(#4444CC), 불릿 18pt(#333333)

## 규칙

- `python-pptx` 패키지 사용
- `app.utils.helpers.sanitize_text`로 텍스트 정제
- slides_data: `[{"title": "...", "bullets": ["...", ...]}, ...]`
- 테스트: `tests/test_pptx_builder.py`

## 작업 지시

사용자의 요청에 따라 `app/services/pptx_builder.py`를 수정하세요.
수정 후 `python -m pytest tests/test_pptx_builder.py -v`로 테스트를 실행하세요.
