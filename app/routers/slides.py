import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import SlideRequest, SlideResponse
from app.services.youtube import extract_video_id, get_video_info
from app.services.transcript import get_transcript, chunk_transcript
from app.services.summarizer import summarize_for_slides
from app.services.pptx_builder import create_pptx
from app.utils.helpers import generate_filename

router = APIRouter(prefix="/api/slides", tags=["slides"])


@router.post("", response_model=SlideResponse)
async def create_slides(request: SlideRequest):
    try:
        video_id = extract_video_id(request.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        video_info = get_video_info(request.url)
        transcript = get_transcript(video_id, language=request.language)
        chunks = chunk_transcript(transcript, chunk_minutes=request.chunk_minutes)
        slides_data = summarize_for_slides(chunks, video_title=video_info["title"])

        filename = generate_filename()
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(settings.OUTPUT_DIR, filename)
        create_pptx(slides_data, video_title=video_info["title"], output_path=output_path)

        return SlideResponse(
            success=True,
            filename=filename,
            video_title=video_info["title"],
            slide_count=len(slides_data) + 1,  # +1 for cover slide
            download_url=f"/api/slides/download/{filename}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_slides(filename: str):
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename,
    )
