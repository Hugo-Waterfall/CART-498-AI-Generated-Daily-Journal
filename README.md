# CART-498-AI-Generated-Daily-Journal

A Python project for generating daily-journal style narratives from images, plus a Flask web app that runs the same pipeline and serves results. There is also a director pipeline that plans shots and generates video clips.

## What This Repo Contains

- `app.py`: Flask web app for uploading images and running the pipeline.
- `director_pipeline.py`: CLI pipeline that analyzes images, plans shots, and generates videos.
- `make_final_video.ps1`: PowerShell helper to stitch clips and optional audio with `ffmpeg`.

## Requirements

- Python 3.11+
- `ffmpeg` on your PATH (needed for stitching clips and audio)
- API keys in `.env` (see below)

## Local Setup

1. Create and activate a virtual environment.

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` and fill in your real keys:
```bash
cp .env.example .env
```

Keys for the director pipeline and video generation:
```
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
ELEVENLABS_VOICE_STABILITY=0.35
ELEVENLABS_VOICE_SIMILARITY=0.85
ELEVENLABS_VOICE_STYLE=0.65
ELEVENLABS_SPEAKER_BOOST=True
RUNWAYML_API_SECRET=your_runwayml_api_key_here
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_VEO_OUTPUT_GCS_URI=gs://your-bucket/veo-output
GOOGLE_APPLICATION_CREDENTIALS_JSON= entire JSON content
```

## Google Cloud / Vertex / Veo Setup

1. Create (or select) a Google Cloud project and enable billing.
2. Enable Vertex AI and Cloud Storage APIs for the project.
3. Create a Cloud Storage bucket for Veo outputs (example bucket: `my-veo-output`).
4. Create a service account and grant it:
   - permission to run Vertex AI jobs/models (commonly `roles/aiplatform.user`)
   - read/write objects to your bucket (commonly `roles/storage.objectAdmin` on the bucket)
5. Create a JSON key for the service account and copy the full JSON contents.
6. Set these environment variables (locally in `.env`, or in Render “Environment”):

```
GOOGLE_CLOUD_PROJECT=<your project id>
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_VEO_OUTPUT_GCS_URI=gs://<your-bucket>/<optional-prefix>
GOOGLE_APPLICATION_CREDENTIALS_JSON=<paste the entire service account JSON>
```

Security note: treat `GOOGLE_APPLICATION_CREDENTIALS_JSON` like a password. Do not commit it.

4. Load environment variables.

Windows PowerShell:
```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
  $k, $v = $_ -split '=', 2
  $env:$k = $v
}
```

macOS/Linux:
```bash
set -a
source .env
set +a
```

## Run Locally

### Web App
```bash
python app.py
```

The app binds to `http://127.0.0.1:8000` by default. You can override with `PORT`.

### Director Pipeline (CLI)
```bash
python director_pipeline.py --input-dir "input_images"
```

Outputs are written to `generated_videos/` with timestamped run folders.

### Stitch Clips and Audio (PowerShell)
```powershell
.\make_final_video.ps1 -RunDir "generated_videos\director_YYYYMMDD_HHMMSS"
```

## Deploy on Render

This repo includes a `Dockerfile` that Render can use directly.

1. Create a new Render Web Service.
2. Connect the GitHub repo and choose **Docker**.
3. Set environment variables in the Render dashboard (same keys as `.env`).
4. Deploy.

Render will set `PORT` automatically. The Docker image starts with:
```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 2 --threads 2
```

## Notes

- Uploaded web images are stored in `web_uploads/`.
- Generated audio is stored in `audio files/`.
- `descriptions.txt` is append-only and keeps a log of each run.
- Never commit real API keys or `.env`.

## Notes (Free-Tier Limits)

- It’s possible to exceed free-tier limits. On Render, you may encounter errors like:There are possible to run exceeds the plan limits, Render may show: `Instance failed ... Ran out of memory (used over 512MB) while running your code.` In that case, it require an upgrade the Render instance size/plan.
- The ElevenLabs free tier can flag requests from shared cloud infrastructure (including Render) as “unusual activity.”
- If that happens, either use `--skip-audio`, switch to a paid plan.
