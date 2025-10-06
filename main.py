import sys
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from pathlib import Path
import time
import traceback
from create_explainer_video import ExplainerVideoCreator

# Windows compatibility
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

# Serve static files (for preview access)
BASE_DIR = Path(__file__).resolve().parent
videos_dir = (BASE_DIR / "generated_videos").resolve()
videos_dir.mkdir(parents=True, exist_ok=True)
app.mount("/videos", StaticFiles(directory=videos_dir), name="videos")

# Input schema
class VideoRequest(BaseModel):
    text_content: str
    target_duration: int = 60
    segments_count: int


@app.post("/generate")
def generate_video(req: VideoRequest):
    try:
        # Unique job folder
        job_id = str(int(time.time()))
        job_output_dir = (videos_dir / f"job_{job_id}").resolve()
        job_output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize video creation pipeline
        creator = ExplainerVideoCreator(output_dir=job_output_dir)

        # Generate assets & video
        assets = creator.create_complete_video_assets(
            text_content=req.text_content,
            target_duration=req.target_duration,
            segments_count=req.segments_count,
            enable_tts=True,
            tts_service="gtts",
            tts_kwargs={"lang": "en", "voice": "en-US-AriaNeural"},
        )

        # Validate final video path
        if assets and assets.get("final_video") and Path(assets["final_video"]).exists():
            video_path = Path(assets["final_video"]).resolve()
            preview_url = f"/videos/{job_output_dir.name}/{video_path.name}"
            download_url = f"/download/{job_output_dir.name}/{video_path.name}"
            return {
                "status": "success",
                "job_id": job_id,
                "preview_url": preview_url,
                "download_url": download_url,
            }

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Video creation failed",
                "details": assets or "No assets returned",
            },
        )

    except Exception as e:
        traceback_str = "".join(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e), "traceback": traceback_str},
        )


# ✅ NEW: Download endpoint
@app.get("/download/{job_id}/{filename}")
def download_video(job_id: str, filename: str):
    """
    Force the browser to download the video instead of streaming it.
    """
    file_path = videos_dir / job_id / filename

    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
