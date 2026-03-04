# YouTube to Slides (PPT) 변환기 - 구현 계획

YouTube 영상에서 핵심 내용을 추출하여 PowerPoint(PPT) 슬라이드로 자동 변환하는 프로젝트.

---

## 시스템 아키텍처

```
YouTube URL 입력
    ↓
영상 메타데이터 추출 (제목, 설명, 길이 등)
    ↓
자막(Transcript) 추출
    ↓
AI 요약 및 슬라이드 구조화
    ↓
PPT 파일 생성
    ↓
다운로드
```

```
Frontend (React/Next) ↔ Backend (FastAPI) ↔ YouTube API / yt-dlp
                           ↓
                    ┌──────┴───────┐
                    │              │
              ┌─────▼─────┐ ┌─────▼─────┐
              │  Zhipu AI │ │  python-  │
              │ GLM-4.5-  │ │  pptx     │
              │  Flash    │ │           │
              └───────────┘ └───────────┘
```

---

## 기술 스택

| 기술 | 용도 |
|------|------|
| Python 3.10+ | 메인 언어 |
| FastAPI 0.109.0 | REST API 서버 |
| yt-dlp 2024.01.0 | YouTube 영상/자막 다운로드 |
| youtube-transcript-api 0.6.2 | 자막 추출 |
| python-pptx 0.6.23 | PPT 파일 생성 |
| zhipuai | AI 요약 및 구조화 (GLM-4.5-Flash, 무료) |
| Pillow 10.2.0 | 이미지 처리 |
| uvicorn 0.27.0 | ASGI 서버 |
| httpx 0.27.0 | HTTP 클라이언트 |
| pydantic-settings | 환경변수 설정 관리 |

---

## 프로젝트 구조

```
youtube-to-slides/
├── CLAUDE.md                 # 프로젝트 계획 및 가이드
├── requirements.txt          # 의존성
├── .env                      # 환경변수 (git 미포함)
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 엔트리포인트
│   ├── config.py            # 설정 관리 (Pydantic Settings)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── slides.py        # /api/slides 엔드포인트
│   ├── services/
│   │   ├── __init__.py
│   │   ├── youtube.py       # YouTube 데이터 추출
│   │   ├── transcript.py    # 자막 추출
│   │   ├── summarizer.py    # AI 요약
│   │   └── pptx_builder.py  # PPT 생성
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic 스키마
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── output/                   # 생성된 PPT 저장 폴더
└── tests/
    ├── test_youtube.py
    ├── test_transcript.py
    └── test_pptx_builder.py
```

---

## 구현 계획

### Phase 1: 기반 작업 (순차)

모든 서비스가 공통으로 의존하는 뼈대를 먼저 세운다.

| # | 파일 | 내용 |
|---|---|---|
| 1-1 | `requirements.txt` | 10개 패키지 의존성 정의 (openai → zhipuai) |
| 1-2 | `.gitignore` | venv, __pycache__, .env, output 등 |
| 1-3 | 디렉토리 생성 | app/, routers/, services/, models/, utils/, output/, tests/ + 각 `__init__.py` |
| 1-4 | `app/config.py` | Pydantic Settings: ZHIPU_API_KEY, OUTPUT_DIR |
| 1-5 | `app/models/schemas.py` | SlideRequest, SlideResponse 모델 |
| 1-6 | `app/utils/helpers.py` | 유틸리티 함수 (필요시) |

**완료 기준:** `pip install -r requirements.txt` 가능, import 경로 정상

---

### Phase 2: 핵심 서비스 구현 (병렬 - 서브에이전트 4개)

각 서비스는 서로 import하지 않으므로 완전히 독립적. 동시 작업 가능.

#### Agent A: `app/services/youtube.py`
- `extract_video_id(url: str) -> str` — URL에서 video ID 파싱
- `get_video_info(url: str) -> dict` — yt-dlp로 메타데이터 추출 (title, description, duration, thumbnail, channel)

#### Agent B: `app/services/transcript.py`
- `get_transcript(video_id: str, language: str = "ko") -> list[dict]` — 자막 추출 (한국어→영어 폴백, 자동생성 자막 폴백)
- `chunk_transcript(transcript: list[dict], chunk_minutes: int = 3) -> list[str]` — 시간 단위 청크 분할

#### Agent C: `app/services/summarizer.py`
- `summarize_for_slides(chunks: list[str], video_title: str) -> list[dict]` — Zhipu AI GLM-4.5-Flash(무료)로 자막 청크 → 슬라이드 구조 변환
- 규칙: 슬라이드당 제목 + 불릿 3~5개, 총 5~15장, 한국어, JSON 반환
- `app.config.settings` 에서 ZHIPU_API_KEY 가져옴
- SDK: `zhipuai` 패키지, `ZhipuAI(api_key=...).chat.completions.create(model="glm-4-flash", ...)`

#### Agent D: `app/services/pptx_builder.py`
- `create_pptx(slides_data: list[dict], video_title: str, output_path: str) -> str` — PPT 생성
- 슬라이드 크기: 13.333 x 7.5 인치
- 표지: 다크 배경(#1A1A2E), 흰색 제목, 40pt
- 내용: 흰색 배경, 제목 28pt(#1A1A2E), 파란 구분선(#4444CC), 불릿 18pt(#333333)

**완료 기준:** 각 서비스가 독립적으로 import 가능

---

### Phase 3: 통합 & 마무리 (순차)

| # | 파일 | 내용 |
|---|---|---|
| 3-1 | `app/routers/slides.py` | POST /api/slides, GET /api/slides/download/{filename} |
| 3-2 | `app/main.py` | FastAPI 앱, 라우터 등록, GET /health |
| 3-3 | `tests/` | youtube URL 파싱, transcript 청크, pptx 생성 테스트 |
| 3-4 | commit & push | 전체 커밋 후 브랜치에 push |

---

## 의존 관계

```
Phase 1 (순차)
  ├── requirements.txt
  ├── .gitignore
  ├── 디렉토리 + __init__.py
  ├── config.py        ←── Phase 2의 summarizer.py가 import
  └── schemas.py       ←── Phase 3의 라우터가 import

Phase 2 (병렬) ← Phase 1 완료 후
  ├── Agent A: youtube.py     (독립)
  ├── Agent B: transcript.py  (독립)
  ├── Agent C: summarizer.py  (config.py만 의존)
  └── Agent D: pptx_builder.py(독립)

Phase 3 (순차) ← Phase 2 전체 완료 후
  ├── routers/slides.py  (4개 서비스 모두 import)
  ├── main.py            (라우터 import)
  ├── tests/
  └── commit & push
```

---

## API 명세

### POST `/api/slides`

YouTube URL로 PPT를 생성.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language": "ko",
  "chunk_minutes": 3
}
```

**Response (200):**
```json
{
  "success": true,
  "filename": "a1b2c3d4.pptx",
  "video_title": "영상 제목",
  "slide_count": 10,
  "download_url": "/api/slides/download/a1b2c3d4.pptx"
}
```

**Error:** 400 (잘못된 URL), 500 (처리 오류)

### GET `/api/slides/download/{filename}`

생성된 PPT 파일 다운로드. 404 if not found.

### GET `/health`

```json
{"status": "ok"}
```

---

## 환경 변수

| 변수 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| ZHIPU_API_KEY | O | - | Zhipu AI API 키 (zhipuai.cn에서 무료 발급) |
| OUTPUT_DIR | X | "output" | PPT 저장 디렉토리 |

---

## 실행 방법

```bash
# 가상환경 설정
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# .env 설정 (zhipuai.cn 에서 무료 API 키 발급)
echo "ZHIPU_API_KEY=your_key" > .env

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

---

## 트러블슈팅

| 문제 | 해결 방법 |
|------|-----------|
| 자막을 찾을 수 없음 | 자동 생성 자막이 있는 영상 사용 |
| ZHIPU_API_KEY 오류 | .env 파일에 키 설정 (zhipuai.cn 무료 발급) |
| yt-dlp 오류 | `pip install -U yt-dlp` |
| PPT 파일이 깨짐 | 텍스트 특수문자 제거 처리 |
