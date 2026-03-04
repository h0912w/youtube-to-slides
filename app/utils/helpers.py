import re
import uuid


def generate_filename() -> str:
    """고유한 파일명 생성."""
    return f"{uuid.uuid4().hex[:8]}.pptx"


def sanitize_text(text: str) -> str:
    """PPT에 들어갈 텍스트에서 문제되는 특수문자 제거."""
    # XML 제어 문자 제거 (0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F)
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
