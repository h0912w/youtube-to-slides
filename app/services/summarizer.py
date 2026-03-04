import json
import re

from zhipuai import ZhipuAI

from app.config import settings


def summarize_for_slides(chunks: list[str], video_title: str) -> list[dict]:
    client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)

    combined_transcript = "\n\n".join(
        f"[섹션 {i + 1}]\n{chunk}" for i, chunk in enumerate(chunks)
    )

    prompt = f"""당신은 YouTube 영상 자막을 PowerPoint 슬라이드로 변환하는 전문가입니다.

다음은 "{video_title}" 영상의 자막입니다:

{combined_transcript}

위 자막을 바탕으로 발표용 슬라이드를 구성해주세요.

규칙:
- 총 슬라이드 수: 5~15장
- 각 슬라이드는 제목(title)과 불릿 포인트(bullets) 3~5개로 구성
- 내용은 반드시 한국어로 작성
- 핵심 내용을 간결하게 요약

반드시 아래 JSON 형식으로만 응답하세요. 다른 설명 없이 JSON만 반환하세요:
[
  {{
    "title": "슬라이드 제목",
    "bullets": [
      "핵심 내용 1",
      "핵심 내용 2",
      "핵심 내용 3"
    ]
  }}
]"""

    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content.strip()

    # Try to extract JSON from markdown code blocks if present
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    if code_block_match:
        content = code_block_match.group(1).strip()

    try:
        slides = json.loads(content)
    except json.JSONDecodeError:
        # Try to find a JSON array anywhere in the response
        array_match = re.search(r"\[[\s\S]*\]", content)
        if array_match:
            slides = json.loads(array_match.group(0))
        else:
            raise ValueError(f"Failed to parse JSON from AI response: {content[:200]}")

    result = []
    for slide in slides:
        result.append({
            "title": str(slide.get("title", "")),
            "bullets": [str(b) for b in slide.get("bullets", [])],
        })

    return result
