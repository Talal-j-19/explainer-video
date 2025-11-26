import sys
import asyncio
import os
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import time
import traceback
from dotenv import load_dotenv

# Suppress gRPC warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GCLOUD_PYTHON_LOGGING_LEVEL'] = 'ERROR'
logging.getLogger('grpc').setLevel(logging.ERROR)
logging.getLogger('googleapis.gapic').setLevel(logging.ERROR)

from create_explainer_video_integrated import IntegratedExplainerVideoCreator

# ✅ Windows compatibility
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
env_path = Path(__file__).resolve().parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

app = FastAPI(title="Explainer Video Generator API", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Base directory for temporary generation
BASE_DIR = Path(__file__).resolve().parent
videos_dir = (BASE_DIR / "generated_videos").resolve()
videos_dir.mkdir(parents=True, exist_ok=True)

# ✅ Input schema
class VideoRequest(BaseModel):
    prompt: str
    target_duration: int = 60
    color_scheme: str = "techBlue"




@app.post("/generate")
async def generate_video(req: VideoRequest):
    """
    Generate an explainer video with integrated template-based infographics.
    
    Args:
        prompt: Topic/subject for the video
        target_duration: Target video length in seconds (default: 60)
        color_scheme: Optional color scheme (techBlue, forestGreen, etc.)
    
    Returns:
        Job ID and status
    """
    try:
        # Unique job folder
        job_id = str(int(time.time() * 1000))
        job_output_dir = (videos_dir / f"job_{job_id}").resolve()
        job_output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📹 Starting video generation job: {job_id}")
        print(f"   Topic: {req.prompt}")
        print(f"   Duration: {req.target_duration}s")
        if req.color_scheme:
            print(f"   Color Scheme: {req.color_scheme}")

        # Initialize integrated video creator
        creator = IntegratedExplainerVideoCreator(use_integrated=True)

        # Generate video with integrated images
        result = await creator.generate_video_with_integrated_images(
            prompt=req.prompt,
            target_duration=req.target_duration,
            output_dir=str(job_output_dir.parent)  # Pass parent to maintain job folder structure
        )

        if result.get('success'):
            return {
                "status": "success",
                "job_id": job_id,
                "message": "Video generated successfully",
                "video_path": result.get('video_path'),
                "segments": result.get('segments_count'),
                "duration": result.get('estimated_duration'),
            }
        
        return JSONResponse(
            status_code=400,
            content={
                "status": "failed",
                "job_id": job_id,
                "error": result.get('error', 'Video generation failed'),
            },
        )

    except Exception as e:
        traceback_str = "".join(traceback.format_exc())
        print(f"❌ Error in video generation: {str(e)}")
        print(traceback_str)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "traceback": traceback_str,
            },
        )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "explainer-video-generator", "version": "2.0"}


@app.get("/")
def root():
    """Root endpoint with API documentation"""
    return {
        "service": "Explainer Video Generator API v2.0",
        "endpoints": {
            "POST /generate": {
                "description": "Generate explainer video with integrated infographics",
                "schema": {
                    "prompt": "string (required) - Topic for the video",
                    "target_duration": "integer (optional, default: 60) - Video length in seconds",
                    "color_scheme": "string (optional) - Color scheme name"
                }
            },
            "GET /health": "Health check endpoint",
            "GET /": "This documentation"
        },
        "example_request": {
            "prompt": "Renewable Energy and Solar Power",
            "target_duration": 60,
            "color_scheme": "forestGreen"
        }
    }

