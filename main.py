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
    """
    Generate an explainer video with integrated template-based infographics.
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

        # Generate video with integrated images (this returns final_video path)
        result = await creator.generate_video_with_integrated_images(
            prompt=req.prompt,
            target_duration=req.target_duration,
            output_dir=str(job_output_dir.parent)  # Pass parent to maintain job folder structure
        )

        if not result.get('success'):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "failed",
                    "job_id": job_id,
                    "error": result.get('error', 'Video generation failed'),
                },
            )

        # Extract local video path from generator result
        local_video_path = result.get('final_video') or result.get('video_path')
        if not local_video_path:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "job_id": job_id,
                    "message": "Video generated but local path missing",
                },
            )

        # Upload to DigitalOcean Spaces (S3-compatible) using DO_SPACES_* env vars
        do_key = os.getenv("DO_SPACES_KEY")
        do_secret = os.getenv("DO_SPACES_SECRET")
        do_endpoint = os.getenv("DO_SPACES_ENDPOINT")
        do_bucket = os.getenv("DO_SPACES_BUCKET")
        s3_prefix = os.getenv("S3_PREFIX", "videos")
        presign_expiry = int(os.getenv("S3_PRESIGN_EXPIRY", str(7*24*3600)))

        if not (do_key and do_secret and do_endpoint and do_bucket):
            print("⚠️ DO Spaces credentials not set — returning local path only")
            return {
                "status": "success",
                "job_id": job_id,
                "message": "Video generated successfully (no Spaces upload configured)",
                "video_path": str(local_video_path),
                "segments": result.get('segments_count'),
                "duration": result.get('estimated_duration'),
            }

        s3_key = f"{s3_prefix.rstrip('/')}/{Path(local_video_path).name}"

        # Create S3 client pointing to DigitalOcean Spaces endpoint
        s3_client = boto3.client(
            "s3",
            region_name=os.getenv("SPACEREGION", None),
            endpoint_url=do_endpoint,
            aws_access_key_id=do_key,
            aws_secret_access_key=do_secret,
        )

        # Upload file (run blocking boto3 in thread)
        def _upload():
            try:
                s3_client.upload_file(
                    str(local_video_path),
                    do_bucket,
                    s3_key,
                    ExtraArgs={"ContentType": "video/mp4", "ACL": "private"}
                )
                return None
            except ClientError as e:
                return str(e)

        upload_err = await asyncio.to_thread(_upload)
        if upload_err:
            print(f"❌ Upload error: {upload_err}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "job_id": job_id,
                    "message": "Failed to upload video to Spaces",
                    "error": upload_err
                },
            )

        # Generate presigned URL for download
        def _presign():
            try:
                url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": do_bucket, "Key": s3_key},
                    ExpiresIn=presign_expiry
                )
                return url, None
            except ClientError as e:
                return None, str(e)

        s3_url, presign_err = await asyncio.to_thread(_presign)
        if presign_err:
            print(f"❌ Presign error: {presign_err}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "job_id": job_id,
                    "message": "Failed to create presigned URL",
                    "error": presign_err
                },
            )

        # Cleanup local job folder (remove generated files) after successful upload/presign
        import shutil
        def _cleanup():
            try:
                video_path = Path(local_video_path)
                job_folder = video_path.parent  # Go up 2 levels to get job_1764162678
                
                if job_folder.exists():
                    shutil.rmtree(job_folder)
                    print(f"🧹 Cleaned up job folder: {job_folder}")
                return None
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
                return str(e)

        cleanup_err = await asyncio.to_thread(_cleanup)
        if cleanup_err:
            print(f"⚠️ Failed to cleanup job folder: {cleanup_err}")
        
        # Return presigned link AFTER cleanup
        return {
            "status": "success",
            "job_id": job_id,
            "message": "Video generated, uploaded to Spaces, and cleaned up",
            "video_path": s3_url,
            "segments": result.get('segments_count'),
            "duration": result.get('estimated_duration'),
        }
    except Exception as e:
        logging.error("Error generating video: %s", e)
        logging.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "job_id": locals().get('job_id') if 'job_id' in locals() else None,
                "message": str(e),
            },
        )

