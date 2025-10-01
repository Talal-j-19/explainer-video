# Explainer Video API

This API allows you to generate explainer videos from text using **FastAPI** + **Uvicorn**.

---

## 🚀 Run the Server

1. Install dependencies:

```bash
pip install fastapi uvicorn
```

2. Start the server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📂 Endpoints

### `POST /generate`

Generates a new explainer video from input text.

- **Request Body (JSON):**
```json
{
  "text_content": "Cloud computing is the delivery of computing services...",
  "target_duration": 60,
  "segments_count": null,
  "enable_tts": true,
  "tts_service": "gtts",
  "lang": "en",
  "voice": "en-US-AriaNeural"
}
```

- **Response (JSON):**
```json
{
  "status": "success",
  "job_id": "1727693820",
  "download_url": "/videos/job_1727693820/final_video.mp4"
}
```

You can then download the generated video at:

```
http://127.0.0.1:8000/videos/job_1727693820/final_video.mp4
```

---

### `GET /videos/{job_id}/final_video.mp4`

Serves the generated video file for download.

---

## 🛠 Example Usage

### cURL

```bash
curl -X POST "http://127.0.0.1:8000/generate"      -H "Content-Type: application/json"      -d '{
           "text_content": "Cloud computing is the delivery of computing services...",
           "target_duration": 30,
           "enable_tts": true,
           "tts_service": "gtts",
           "lang": "en"
         }'
```

### Python Client

```python
import requests

url = "http://127.0.0.1:8000/generate"
data = {
    "text_content": "AI is transforming industries by automating tasks...",
    "target_duration": 45,
    "enable_tts": True,
    "tts_service": "gtts",
    "lang": "en"
}

res = requests.post(url, json=data)
print(res.json())
```

---

## ⚠️ Notes

- Video generation may take **several minutes** depending on the length of the script.  
- By default, all videos are stored in the `generated_videos/` folder.  
- The `download_url` is relative — prefix it with your server address.  
