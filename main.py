import sys
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import time
import traceback
from create_explainer_video import ExplainerVideoCreator

# ✅ Windows compatibility
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

# ✅ Base directory for temporary generation
BASE_DIR = Path(__file__).resolve().parent
videos_dir = (BASE_DIR / "generated_videos").resolve()
videos_dir.mkdir(parents=True, exist_ok=True)

# ✅ Input schema
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

        # Generate assets & video (with upload to cloud)
        assets = creator.create_complete_video_assets(
            text_content=req.text_content,
            target_duration=req.target_duration,
            segments_count=req.segments_count,
            enable_tts=True,
            tts_service="gtts",
            tts_kwargs={"lang": "en", "voice": "en-US-AriaNeural"},
        )

        # ✅ Return only the public cloud URL
        if assets and assets.get("public_url"):
            return {
                "status": "success",
                "job_id": job_id,
                "public_url": assets["public_url"],
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
            content={
                "status": "error",
                "message": str(e),
                "traceback": traceback_str,
            },
        )
