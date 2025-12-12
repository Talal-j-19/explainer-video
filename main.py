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
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
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
            # Original video generation code
            creator = IntegratedExplainerVideoCreator(use_integrated=True)
            jobs[job_id]["progress"] = 10
            result = await creator.generate_video_with_integrated_images(
                prompt=req.prompt,
                target_duration=req.target_duration,
                output_dir=str(videos_dir)
            )
            jobs[job_id]["progress"] = 50

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
                import boto3
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
                jobs[job_id]["progress"] = 80

                def _presign():
                    return s3_client.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": do_bucket, "Key": s3_key},
                        ExpiresIn=presign_expiry
                    )
                s3_url = await asyncio.to_thread(_presign)
            else:
                s3_url = str(local_video_path)
                jobs[job_id]["progress"] = 90


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


