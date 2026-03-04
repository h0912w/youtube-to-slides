from fastapi import FastAPI

from app.routers import slides

app = FastAPI(title="YouTube to Slides", version="1.0.0")

app.include_router(slides.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
