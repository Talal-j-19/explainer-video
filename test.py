import boto3
import os
from dotenv import load_dotenv
from botocore.client import Config

print("🔍 Testing connection to DigitalOcean Space...")

# Load environment variables
load_dotenv()

ACCESS_KEY = os.getenv("DO_SPACES_KEY")
SECRET_KEY = os.getenv("DO_SPACES_SECRET")
REGION = os.getenv("DO_SPACES_REGION", "us-east-1")
BUCKET_NAME = os.getenv("DO_SPACES_BUCKET")

# Automatically build endpoint URL from region
ENDPOINT_URL = f"https://sfo3.digitaloceanspaces.com"

try:
    # Use a boto3 session for consistency and flexibility
    session = boto3.session.Session()
    s3 = session.client(
        "s3",
        region_name=REGION,
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4")
    )

    # Test by listing objects in the bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    print(f"✅ Successfully connected to bucket: {BUCKET_NAME}")

    count = len(response.get("Contents", []))
    print(f"📦 Found {count} objects in the bucket.")

    # Optionally print object keys
    for obj in response.get("Contents", []):
        print(" -", obj["Key"])

except Exception as e:
    print("❌ Connection failed:", e)
