# YouTube to Slides (PPT) 변환기

YouTube 영상에서 핵심 내용을 추출하여 PowerPoint(PPT) 슬라이드로 자동 변환하는 프로젝트입니다.

---

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [기술 스택](#기술-스택)
4. [설치 방법](#설치-방법)
5. [프로젝트 구조](#프로젝트-구조)
6. [구현 가이드](#구현-가이드)
7. [API 명세](#api-명세)
8. [사용 방법](#사용-방법)
9. [트러블슈팅](#트러블슈팅)

---

## 프로젝트 개요

### 핵심 기능

- YouTube 영상 URL을 입력하면 자동으로 PPT 파일 생성
- 영상의 자막(transcript)을 추출하여 텍스트 기반 슬라이드 생성
- 영상의 주요 장면을 캡처하여 이미지 슬라이드 생성
- AI를 활용한 내용 요약 및 슬라이드 구성

### 처리 흐름

```
YouTube URL 입력
    ↓
영상 메타데이터 추출 (제목, 설명, 길이 등)
    ↓
자막(Transcript) 추출
    ↓
주요 장면 캡처 (썸네일/프레임)
    ↓
AI 요약 및 슬라이드 구조화
    ↓
PPT 파일 생성
    ↓
다운로드
```

---

## 시스템 아키텍처

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  YouTube API │
│  (React/Next)│◀────│  (FastAPI)   │◀────│  / yt-dlp    │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────▼─────┐ ┌─────▼─────┐
              │  OpenAI   │ │  python-  │
              │  API      │ │  pptx     │
              └───────────┘ └───────────┘
```

---

## 기술 스택

### Backend

| 기술 | 용도 | 설치 |
|------|------|------|
| **Python 3.10+** | 메인 언어 | `pyenv install 3.10` |
| **FastAPI** | REST API 서버 | `pip install fastapi` |
| **yt-dlp** | YouTube 영상/자막 다운로드 | `pip install yt-dlp` |
| **youtube-transcript-api** | 자막 추출 | `pip install youtube-transcript-api` |
| **python-pptx** | PPT 파일 생성 | `pip install python-pptx` |
| **OpenAI API** | AI 요약 및 구조화 | `pip install openai` |
| **Pillow** | 이미지 처리 | `pip install Pillow` |
| **uvicorn** | ASGI 서버 | `pip install uvicorn` |

### Frontend (선택)

| 기술 | 용도 |
|------|------|
| **Next.js / React** | 웹 UI |
| **Tailwind CSS** | 스타일링 |
| **Axios** | HTTP 요청 |

---

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/h0912w/youtube-to-slides.git
cd youtube-to-slides
```

### 2. Python 가상환경 설정

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env` 파일을 프로젝트 루트에 생성합니다:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

---

## 프로젝트 구조

```
youtube-to-slides/
├── README.md
├── requirements.txt
├── .env                     # 환경변수 (git에 포함하지 않음)
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 엔트리포인트
│   ├── config.py            # 설정 관리
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── slides.py        # /api/slides 엔드포인트
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── youtube.py       # YouTube 데이터 추출 서비스
│   │   ├── transcript.py    # 자막 추출 서비스
│   │   ├── summarizer.py    # AI 요약 서비스
│   │   ├── screenshot.py    # 영상 캡처 서비스
│   │   └── pptx_builder.py  # PPT 생성 서비스
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic 스키마
│   │
│   └── utils/
│       ├── __init__.py
│       └── helpers.py        # 유틸리티 함수
│
├── templates/
│   └── default.pptx          # PPT 템플릿 파일
│
├── output/                    # 생성된 PPT 저장 폴더
│
└── tests/
    ├── test_youtube.py
    ├── test_transcript.py
    └── test_pptx_builder.py
```

---

## 구현 가이드

### Step 1: 프로젝트 초기 설정

**requirements.txt** 생성:

```txt
fastapi==0.109.0
uvicorn==0.27.0
yt-dlp==2024.01.0
youtube-transcript-api==0.6.2
python-pptx==0.6.23
openai==1.12.0
python-dotenv==1.0.1
Pillow==10.2.0
httpx==0.27.0
```

**.gitignore** 생성:

```
venv/
__pycache__/
*.pyc
.env
output/*.pptx
.DS_Store
```

---

### Step 2: YouTube 데이터 추출 (`app/services/youtube.py`)

YouTube URL에서 영상 정보를 추출하는 서비스입니다.

```python
import re
from yt_dlp import YoutubeDL


def extract_video_id(url: str) -> str:
    """YouTube URL에서 video ID를 추출합니다."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("유효하지 않은 YouTube URL입니다.")


def get_video_info(url: str) -> dict:
    """YouTube 영상의 메타데이터를 가져옵니다."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "description": info.get("description"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "channel": info.get("channel"),
        }
```

---

### Step 3: 자막 추출 (`app/services/transcript.py`)

YouTube 자막을 추출하여 시간대별로 텍스트를 가져옵니다.

```python
from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id: str, language: str = "ko") -> list[dict]:
    """
    YouTube 영상의 자막을 가져옵니다.

    Returns:
        [{"text": "안녕하세요", "start": 0.0, "duration": 2.5}, ...]
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=[language, "en"]
        )
        return transcript
    except Exception:
        # 자동 생성 자막 시도
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript([language, "en"])
        return transcript.fetch()


def chunk_transcript(transcript: list[dict], chunk_minutes: int = 3) -> list[str]:
    """
    자막을 시간 단위로 묶어 청크로 나눕니다.
    각 청크가 하나의 슬라이드 후보가 됩니다.
    """
    chunks = []
    current_chunk = []
    chunk_seconds = chunk_minutes * 60
    chunk_start = 0

    for entry in transcript:
        if entry["start"] - chunk_start >= chunk_seconds and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            chunk_start = entry["start"]
        current_chunk.append(entry["text"])

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
```

---

### Step 4: AI 요약 서비스 (`app/services/summarizer.py`)

OpenAI API를 사용하여 자막 내용을 슬라이드에 적합한 형태로 요약합니다.

```python
from openai import OpenAI
from app.config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def summarize_for_slides(chunks: list[str], video_title: str) -> list[dict]:
    """
    자막 청크들을 슬라이드 구조로 변환합니다.

    Returns:
        [{"title": "슬라이드 제목", "bullets": ["요점1", "요점2", ...]}, ...]
    """
    all_text = "\n\n---\n\n".join(
        [f"[구간 {i+1}] {chunk}" for i, chunk in enumerate(chunks)]
    )

    prompt = f"""다음은 YouTube 영상 "{video_title}"의 자막을 시간대별로 나눈 것입니다.
이 내용을 프레젠테이션 슬라이드로 구성해주세요.

규칙:
1. 각 슬라이드에는 제목(title)과 핵심 포인트(bullets) 3-5개를 포함
2. 슬라이드는 5-15장 사이로 구성
3. 첫 슬라이드는 제목 슬라이드, 마지막은 요약 슬라이드
4. 한국어로 작성
5. JSON 배열 형태로 반환

자막 내용:
{all_text}

응답 형식 (JSON만 반환):
[
  {{"title": "슬라이드 제목", "bullets": ["포인트1", "포인트2", "포인트3"]}}
]"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    import json
    result = json.loads(response.choices[0].message.content)

    # 응답이 {"slides": [...]} 형태일 수 있음
    if isinstance(result, dict):
        return result.get("slides", list(result.values())[0])
    return result
```

---

### Step 5: PPT 생성 (`app/services/pptx_builder.py`)

python-pptx를 사용하여 실제 PPT 파일을 생성합니다.

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os


def create_pptx(
    slides_data: list[dict],
    video_title: str,
    output_path: str = "output/result.pptx",
) -> str:
    """
    슬라이드 데이터를 기반으로 PPT 파일을 생성합니다.

    Args:
        slides_data: [{"title": "...", "bullets": ["...", ...]}, ...]
        video_title: 영상 제목
        output_path: 저장 경로

    Returns:
        생성된 파일 경로
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # --- 표지 슬라이드 ---
    slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(slide_layout)

    # 배경색 설정
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    # 제목 텍스트
    txBox = slide.shapes.add_textbox(
        Inches(1), Inches(2.5), Inches(11.333), Inches(2)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = video_title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p.alignment = PP_ALIGN.CENTER

    # --- 내용 슬라이드 ---
    for slide_data in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # 배경
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        # 슬라이드 제목
        title_box = slide.shapes.add_textbox(
            Inches(0.8), Inches(0.5), Inches(11.7), Inches(1)
        )
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide_data["title"]
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

        # 구분선
        line = slide.shapes.add_shape(
            1, Inches(0.8), Inches(1.6), Inches(11.7), Emu(0)
        )
        line.line.color.rgb = RGBColor(0x44, 0x44, 0xCC)
        line.line.width = Pt(2)

        # 불릿 포인트
        bullet_box = slide.shapes.add_textbox(
            Inches(1.0), Inches(2.0), Inches(11.0), Inches(4.5)
        )
        tf = bullet_box.text_frame
        tf.word_wrap = True

        for i, bullet in enumerate(slide_data.get("bullets", [])):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"•  {bullet}"
            p.font.size = Pt(18)
            p.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            p.space_after = Pt(12)

    # 파일 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    return output_path
```

---

### Step 6: FastAPI 엔드포인트 (`app/main.py`)

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os

from app.services.youtube import extract_video_id, get_video_info
from app.services.transcript import get_transcript, chunk_transcript
from app.services.summarizer import summarize_for_slides
from app.services.pptx_builder import create_pptx


app = FastAPI(title="YouTube to Slides API")


class SlideRequest(BaseModel):
    url: str
    language: str = "ko"
    chunk_minutes: int = 3


@app.post("/api/slides")
async def create_slides(request: SlideRequest):
    """YouTube URL을 받아 PPT 파일을 생성합니다."""
    try:
        # 1. Video ID 추출
        video_id = extract_video_id(request.url)

        # 2. 영상 정보 가져오기
        video_info = get_video_info(request.url)

        # 3. 자막 추출
        transcript = get_transcript(video_id, request.language)

        # 4. 자막을 청크로 분할
        chunks = chunk_transcript(transcript, request.chunk_minutes)

        # 5. AI 요약
        slides_data = summarize_for_slides(chunks, video_info["title"])

        # 6. PPT 생성
        filename = f"{uuid.uuid4().hex[:8]}.pptx"
        output_path = f"output/{filename}"
        create_pptx(slides_data, video_info["title"], output_path)

        return {
            "success": True,
            "filename": filename,
            "video_title": video_info["title"],
            "slide_count": len(slides_data),
            "download_url": f"/api/slides/download/{filename}",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 중 오류: {str(e)}")


@app.get("/api/slides/download/{filename}")
async def download_slides(filename: str):
    """생성된 PPT 파일을 다운로드합니다."""
    filepath = f"output/{filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename,
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

---

### Step 7: 설정 관리 (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OUTPUT_DIR: str = "output"

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## API 명세

### POST `/api/slides`

YouTube URL로 PPT를 생성합니다.

**Request Body:**

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language": "ko",
  "chunk_minutes": 3
}
```

**Response:**

```json
{
  "success": true,
  "filename": "a1b2c3d4.pptx",
  "video_title": "영상 제목",
  "slide_count": 10,
  "download_url": "/api/slides/download/a1b2c3d4.pptx"
}
```

### GET `/api/slides/download/{filename}`

생성된 PPT 파일을 다운로드합니다.

---

## 사용 방법

### CLI로 테스트

```bash
# 서버 실행
uvicorn app.main:app --reload --port 8000

# API 호출 (다른 터미널에서)
curl -X POST http://localhost:8000/api/slides \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# PPT 다운로드
curl -O http://localhost:8000/api/slides/download/FILENAME.pptx
```

### Python 스크립트로 직접 실행

```python
from app.services.youtube import extract_video_id, get_video_info
from app.services.transcript import get_transcript, chunk_transcript
from app.services.summarizer import summarize_for_slides
from app.services.pptx_builder import create_pptx

url = "https://www.youtube.com/watch?v=VIDEO_ID"

video_id = extract_video_id(url)
video_info = get_video_info(url)
transcript = get_transcript(video_id)
chunks = chunk_transcript(transcript)
slides = summarize_for_slides(chunks, video_info["title"])
create_pptx(slides, video_info["title"], "output/my_slides.pptx")

print("PPT 생성 완료!")
```

---

## 트러블슈팅

### 자주 발생하는 문제

| 문제 | 원인 | 해결 방법 |
|------|------|-----------|
| `자막을 찾을 수 없습니다` | 영상에 자막이 없음 | 자동 생성 자막이 있는 영상 사용 |
| `OPENAI_API_KEY 오류` | API 키 미설정 | `.env` 파일에 키 설정 |
| `yt-dlp 오류` | 버전이 오래됨 | `pip install -U yt-dlp` |
| `PPT 파일이 깨짐` | 인코딩 문제 | 텍스트에 특수문자 제거 처리 추가 |

### ffmpeg 설치 (영상 캡처 기능 사용 시)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

---

## 라이선스

MIT License
