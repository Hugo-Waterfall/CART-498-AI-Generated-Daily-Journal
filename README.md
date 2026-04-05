# CART-498-AI-Generated-Daily-Journal

Small Python utilities for:

- analyzing all images in `input_images`
- generating a short journal-style narrative from those image descriptions
- converting that narrative to speech with ElevenLabs
- serving a simple one-page website for image uploads and output playback
- turning local image sequences into Runway video transitions
- directing a Veo-based pipeline from images to scenes, shots, clips, and a final edit

## Setup

1. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Optional audio dependency for narration:

```bash
pip install elevenlabs
```

3. Add your API keys without hardcoding them into the scripts:

```bash
cp .env.example .env
```

Then edit `.env` and add your real keys:

```bash
OPENAI_API_KEY=your_real_openai_key_here
ELEVENLABS_API_KEY=your_real_elevenlabs_key_here
RUNWAYML_API_SECRET=your_real_runway_key_here
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_VEO_OUTPUT_GCS_URI=gs://your-bucket/veo-output
```

Load them into your shell:

```bash
set -a
source .env
set +a
```

`.env` is ignored by Git, so it will not be committed unless you remove that rule.

## Website

Run the one-page upload site:

```bash
python3 app.py
```

Then open `http://127.0.0.1:8000`.

To serve the app with Gunicorn instead:

```bash
./.venv/bin/gunicorn app:app
```

What the website currently does:

- accepts one or more uploaded images
- analyzes each image with OpenAI
- generates one final journal-style narrative
- appends the run output to `descriptions.txt`
- generates ElevenLabs narration audio and exposes it in an HTML audio player

What it does not do yet:

- generate the final image-to-video social post inside the web UI

The current web output is intentionally the saved text block plus the ElevenLabs audio result, so the final video step can be plugged in later.

For the Veo pipeline, authenticate Google Cloud locally with Application Default Credentials before running:

```bash
gcloud auth application-default login
```

## Analyze Images

Analyze every supported image in `input_images`, generate a journal-style narrative, convert that narrative to speech, and append the text output to `descriptions.txt`:

```bash
python3 analyze_image.py
```

Use a custom prompt:

```bash
python3 analyze_image.py \
  --prompt "Describe this image like a journal entry prompt, including mood, setting, and notable details."
```

Use a different folder or output file:

```bash
python3 analyze_image.py \
  --input-dir "input_images" \
  --output-file "descriptions.txt"
```

Override the image-analysis model, narrative model, or ElevenLabs voice settings:

```bash
python3 analyze_image.py \
  --image-model "gpt-4.1-mini" \
  --narrative-model "gpt-5.4" \
  --tts-voice-id "JBFqnCBsd6RMkjVDRZzb" \
  --tts-model-id "eleven_multilingual_v2"
```

## Generate Video

Generate Runway clips from a folder of local images:

```bash
python3 imagetovideo.py --input-dir "input_images"
```

Generate one stitched final video from image pairs:

```bash
python3 imagetovideo.py \
  --input-dir "input_images" \
  --group-size 2 \
  --total-duration 7 \
  --stitch
```

## Director Pipeline For Veo

Build a shot plan from your images, generate Veo clips, stitch them, and optionally add narration:

```bash
python3 director_pipeline.py \
  --input-dir "input_images" \
  --veo-model "veo-3.1-fast-generate-001"
```

Plan everything without generating Veo clips yet:

```bash
python3 director_pipeline.py \
  --input-dir "input_images" \
  --skip-video
```

## Notes

- `analyze_image.py` uses `gpt-4.1-mini` for image descriptions and `gpt-5.4` for the final narrative by default.
- `app.py` reuses the same analysis pipeline as `analyze_image.py`, so the CLI and website produce the same saved output format.
- Generated narration audio is saved to `audio files/`.
- `descriptions.txt` keeps an append-only log of each run, including the generated narrative and saved audio path.
- Uploaded website images are stored temporarily in `web_uploads/`.
- `imagetovideo.py` uses Runway `gen4_turbo` by default.
- If `imagetovideo.py` is run without `--prompt`, it uses the latest `Narrative:` block from `descriptions.txt`.
- `director_pipeline.py` uses OpenAI to create image analyses and a shot plan, then calls Veo through Vertex AI using `google-genai`.
- Veo outputs are written to the Cloud Storage prefix configured by `GOOGLE_CLOUD_VEO_OUTPUT_GCS_URI`, then downloaded back into the local run folder.
- `elevenlabs` is optional for `director_pipeline.py` when you run with `--skip-audio`.
- Never commit your real API keys, `.env`, or any file containing secrets.
