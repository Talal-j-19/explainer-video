from enum import Enum
from typing import Dict

class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"

# Global job store: job_id -> status/info
jobs: Dict[str, dict] = {}

import sys
import asyncio
import os
import logging
import boto3
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from tts_processor import TTSProcessor
from pydantic import BaseModel
from pathlib import Path
import time
import traceback
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError


# Suppress gRPC warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GCLOUD_PYTHON_LOGGING_LEVEL'] = 'ERROR'
logging.getLogger('grpc').setLevel(logging.ERROR)
logging.getLogger('googleapis.gapic').setLevel(logging.ERROR)

from create_explainer_video_integrated import IntegratedExplainerVideoCreator

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
    target_duration: int = 30
    color_scheme: str = "techBlue"


def update_progress(job_id: str, value: int, message: str = None):
    jobs[job_id]["progress"] = value
    if message:
        jobs[job_id]["message"] = message


@app.post("/generate")
async def generate_video(req: VideoRequest):
    """Queue a video generation job and return job_id immediately."""
    job_id = str(int(time.time() * 1000))
    jobs[job_id] = {
    "status": JobStatus.pending,
    "progress": 0,
    "video_path": None,
    "message": None,
    "start_time": time.time(),
    "total_time": None
    }

    async def run_job():
        jobs[job_id]["status"] = JobStatus.running
        jobs[job_id]["progress"] = 5
        try:
            def _blocking_job():
                creator = IntegratedExplainerVideoCreator(use_integrated=True)
                return creator.generate_video_sync(
                    prompt=req.prompt,
                    target_duration=req.target_duration,
                    output_dir=str(videos_dir),
                    color_scheme=req.color_scheme, 
                    progress_callback=lambda p, m=None: update_progress(job_id, p, m)
                )

            result = await asyncio.to_thread(_blocking_job)

            if not result.get('success'):
                jobs[job_id]["status"] = JobStatus.failed
                jobs[job_id]["message"] = result.get('error', 'Video generation failed')
                jobs[job_id]["progress"] = 0
                return

            local_video_path = result.get('final_video') or result.get('video_path')
            if not local_video_path:
                jobs[job_id]["status"] = JobStatus.failed
                jobs[job_id]["message"] = "Video generated but local path missing"
                return

            # Upload to DO Spaces (same as your existing code)
            do_key = os.getenv("DO_SPACES_KEY")
            do_secret = os.getenv("DO_SPACES_SECRET")
            do_endpoint = os.getenv("DO_SPACES_ENDPOINT")
            do_bucket = os.getenv("DO_SPACES_BUCKET")
            s3_prefix = os.getenv("S3_PREFIX", "videos")
            presign_expiry = int(os.getenv("S3_PRESIGN_EXPIRY", str(7*24*3600)))

            if do_key and do_secret and do_endpoint and do_bucket:
                s3_client = boto3.client(
                    "s3",
                    region_name=os.getenv("SPACEREGION", None),
                    endpoint_url=do_endpoint,
                    aws_access_key_id=do_key,
                    aws_secret_access_key=do_secret,
                )
                s3_key = f"{s3_prefix.rstrip('/')}/{Path(local_video_path).name}"

                def _upload():
                    s3_client.upload_file(
                        str(local_video_path),
                        do_bucket,
                        s3_key,
                        ExtraArgs={"ContentType": "video/mp4", "ACL": "private"}
                    )
                await asyncio.to_thread(_upload)

                def _presign():
                    return s3_client.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": do_bucket, "Key": s3_key},
                        ExpiresIn=presign_expiry
                    )
                s3_url = await asyncio.to_thread(_presign)
            else:
                s3_url = str(local_video_path)

            jobs[job_id]["status"] = JobStatus.success
            jobs[job_id]["progress"] = 100
            jobs[job_id]["video_path"] = s3_url
            jobs[job_id]["total_time"] = round(time.time() - jobs[job_id]["start_time"], 2)
            jobs[job_id]["message"] = "Video generated successfully"

        except Exception as e:
            jobs[job_id]["status"] = JobStatus.failed
            jobs[job_id]["message"] = str(e)
            jobs[job_id]["total_time"] = round(time.time() - jobs[job_id]["start_time"], 2)

    # Start background task
    asyncio.create_task(run_job())

    # Immediately return job ID
    return {"status": "queued", "job_id": job_id}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"status": "error", "message": "Job ID not found"}
    return job

# @app.post("/generate_audio")
# async def generate_audio():
#     tts = TTSProcessor(video_segments_dir="video_segments")
#     narrations = tts.clean_all_narrations()
#     print(f'Narations: {narrations}')
#     if not narrations:
#         return {"success": False, "message": "No narration files found"}

#     for narration in narrations:
#         text = narration["clean_text"].strip()
#         if not text:
#             narration["audio_generated"] = False
#             continue
#         # Generate audio
#         narration["audio_generated"] = await tts._generate_edge_tts(
#             text,
#             narration["output_audio"],
#             voice="en-AU-NatashaNeural"
#         )
#         if narration["audio_generated"]:
#             narration["audio_file_size"] = Path(narration["output_audio"]).stat().st_size
#             narration["tts_service"] = "edge_tts"

#     summary_file = tts.create_audio_summary(narrations)
#     return {"success": True, "summary_file": summary_file}

