import os
import boto3
from botocore.client import Config
from dotenv import load_dotenv
import shutil

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "local")
DO_SPACES_KEY = os.getenv("DO_SPACES_KEY")
DO_SPACES_SECRET = os.getenv("DO_SPACES_SECRET")
DO_SPACES_REGION = os.getenv("DO_SPACES_REGION", "sfo3")
DO_SPACES_BUCKET = os.getenv("DO_SPACES_BUCKET")

# ✅ Initialize client once
s3 = boto3.client(
    "s3",
    region_name=DO_SPACES_REGION,
    endpoint_url=f"https://sfo3.digitaloceanspaces.com",
    aws_access_key_id=DO_SPACES_KEY,
    aws_secret_access_key=DO_SPACES_SECRET,
    config=Config(signature_version="s3v4"),
)


def upload_to_spaces(file_path: str, object_name: str) -> str:
    """Uploads file to DigitalOcean Spaces and returns public URL"""
    s3.upload_file(
        Filename=file_path,
        Bucket=DO_SPACES_BUCKET,
        Key=object_name,
        ExtraArgs={"ACL": "public-read", "ContentType": "video/mp4"},
    )
    return f"https://{DO_SPACES_BUCKET}.sfo3.digitaloceanspaces.com/{object_name}"


def cleanup_local_folder(path: str):
    """Deletes local folder only in production"""
    if APP_ENV == "production":
        shutil.rmtree(path, ignore_errors=True)
        print(f"🧹 Deleted local folder: {path}")
    else:
        print(f"💾 Skipped deletion (APP_ENV={APP_ENV}) — keeping local files for testing.")