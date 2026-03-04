from pydantic import BaseModel


class SlideRequest(BaseModel):
    url: str
    language: str = "ko"
    chunk_minutes: int = 3


class SlideResponse(BaseModel):
    success: bool
    filename: str
    video_title: str
    slide_count: int
    download_url: str
