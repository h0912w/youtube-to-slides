# YouTube to Slides (PPT) 변환기

YouTube 영상의 자막을 AI로 요약하여 PowerPoint 슬라이드로 자동 변환하는 서비스입니다.

---

## 사전 준비

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 발급

[zhipuai.cn](https://zhipuai.cn)에서 무료 API 키를 발급받고 `.env` 파일에 설정합니다.

```bash
echo "ZHIPU_API_KEY=your_api_key_here" > .env
```

### 3. 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

서버가 정상 동작하는지 확인:

```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

---

## 사용 방법

### YouTube URL 입력

`POST /api/slides` 엔드포인트에 YouTube URL을 JSON으로 전송합니다.

#### 기본 요청 (curl)

```bash
curl -X POST http://localhost:8000/api/slides \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

#### 옵션 포함 요청

```bash
curl -X POST http://localhost:8000/api/slides \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "language": "ko",
    "chunk_minutes": 5
  }'
```

#### 요청 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `url` | string | O | - | YouTube 영상 URL |
| `language` | string | X | `"ko"` | 자막 언어 (ko, en 등) |
| `chunk_minutes` | int | X | `3` | 자막을 몇 분 단위로 나눌지 |

#### 지원하는 URL 형식

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://www.youtube.com/embed/dQw4w9WgXcQ
https://www.youtube.com/shorts/dQw4w9WgXcQ
```

---

### 출력 결과

#### 1단계: PPT 생성 응답

요청이 성공하면 아래와 같은 JSON 응답을 받습니다.

```json
{
  "success": true,
  "filename": "a1b2c3d4.pptx",
  "video_title": "파이썬 기초 강의",
  "slide_count": 10,
  "download_url": "/api/slides/download/a1b2c3d4.pptx"
}
```

| 필드 | 설명 |
|------|------|
| `success` | 성공 여부 |
| `filename` | 생성된 PPT 파일명 |
| `video_title` | YouTube 영상 제목 |
| `slide_count` | 총 슬라이드 수 (표지 포함) |
| `download_url` | PPT 다운로드 경로 |

#### 2단계: PPT 파일 다운로드

응답의 `download_url`을 사용하여 파일을 다운로드합니다.

```bash
curl -O http://localhost:8000/api/slides/download/a1b2c3d4.pptx
```

브라우저에서 직접 접속해도 다운로드됩니다:

```
http://localhost:8000/api/slides/download/a1b2c3d4.pptx
```

#### 생성되는 PPT 구조

| 슬라이드 | 디자인 |
|----------|--------|
| **표지** (1장) | 다크 배경(#1A1A2E), 영상 제목 흰색 40pt |
| **내용** (5~15장) | 흰색 배경, 제목 28pt, 파란 구분선, 불릿 3~5개 |

---

### 전체 사용 흐름 예시

```bash
# 1. 서버 실행
uvicorn app.main:app --reload --port 8000

# 2. PPT 생성 요청
curl -X POST http://localhost:8000/api/slides \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "language": "ko"}'

# 응답 예시:
# {
#   "success": true,
#   "filename": "a1b2c3d4.pptx",
#   "video_title": "Rick Astley - Never Gonna Give You Up",
#   "slide_count": 8,
#   "download_url": "/api/slides/download/a1b2c3d4.pptx"
# }

# 3. PPT 다운로드
curl -O http://localhost:8000/api/slides/download/a1b2c3d4.pptx
```

---

### Python 코드로 사용

```python
import httpx

# PPT 생성 요청
response = httpx.post("http://localhost:8000/api/slides", json={
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "language": "ko",
    "chunk_minutes": 3,
})
result = response.json()
print(result)

# PPT 다운로드
download = httpx.get(f"http://localhost:8000{result['download_url']}")
with open(result["filename"], "wb") as f:
    f.write(download.content)
print(f"저장 완료: {result['filename']}")
```

---

### Swagger UI (자동 문서)

서버 실행 후 브라우저에서 아래 주소로 접속하면 API를 직접 테스트할 수 있습니다.

```
http://localhost:8000/docs
```

---

## 에러 응답

| HTTP 코드 | 원인 | 예시 |
|-----------|------|------|
| **400** | 잘못된 YouTube URL | `{"detail": "Could not extract video ID from URL: ..."}` |
| **404** | 파일을 찾을 수 없음 | `{"detail": "File not found"}` |
| **500** | 서버 처리 오류 (자막 없음, AI 오류 등) | `{"detail": "No transcript found for video: ..."}` |

---

## 내부 처리 흐름

```
YouTube URL 입력
    ↓
1. URL에서 Video ID 추출 (youtube.py)
    ↓
2. 영상 메타데이터 추출 - 제목, 설명, 길이 등 (youtube.py + yt-dlp)
    ↓
3. 자막 추출 - 한국어 → 영어 → 자동생성 순 폴백 (transcript.py)
    ↓
4. 자막을 시간 단위로 분할 (기본 3분) (transcript.py)
    ↓
5. AI가 각 청크를 슬라이드 구조로 요약 (summarizer.py + Zhipu AI)
    ↓
6. PPT 파일 생성 - 표지 + 내용 슬라이드 (pptx_builder.py)
    ↓
7. 파일 저장 (output/ 디렉토리) → 다운로드 URL 반환
```

---

## 환경 변수

| 변수 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `ZHIPU_API_KEY` | O | - | Zhipu AI API 키 ([zhipuai.cn](https://zhipuai.cn)에서 무료 발급) |
| `OUTPUT_DIR` | X | `"output"` | 생성된 PPT 저장 디렉토리 |

---

## 트러블슈팅

| 문제 | 해결 방법 |
|------|-----------|
| 자막을 찾을 수 없음 | 자동 생성 자막이 있는 영상을 사용하세요 |
| ZHIPU_API_KEY 오류 | `.env` 파일에 키가 설정되어 있는지 확인 |
| yt-dlp 오류 | `pip install -U yt-dlp`로 최신 버전 업데이트 |
| PPT 파일이 깨짐 | 특수문자 이슈 → 이슈 리포트 부탁드립니다 |
| 자막 언어가 안 맞음 | `language` 파라미터를 `"en"` 등으로 변경 |
