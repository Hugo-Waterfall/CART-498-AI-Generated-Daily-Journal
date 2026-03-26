# CART-498-AI-Generated-Daily-Journal

Small Python utilities for:

- analyzing all images in `input_images`
- generating a short journal-style narrative from those image descriptions
- converting that narrative to speech with ElevenLabs
- turning local image sequences into Runway video transitions

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

3. Add your API keys without hardcoding them into the scripts:

```bash
cp .env.example .env
```

Then edit `.env` and add your real keys:

```bash
OPENAI_API_KEY=your_real_openai_key_here
ELEVENLABS_API_KEY=your_real_elevenlabs_key_here
RUNWAYML_API_SECRET=your_real_runway_key_here
```

Load them into your shell:

```bash
set -a
source .env
set +a
```

`.env` is ignored by Git, so it will not be committed unless you remove that rule.

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

## Notes

- `analyze_image.py` uses `gpt-4.1-mini` for image descriptions and `gpt-5.4` for the final narrative by default.
- Generated narration audio is saved to `audio files/`.
- `descriptions.txt` keeps an append-only log of each run, including the generated narrative and saved audio path.
- `imagetovideo.py` uses Runway `gen4_turbo` by default.
- If `imagetovideo.py` is run without `--prompt`, it uses the latest `Narrative:` block from `descriptions.txt`.
- Never commit your real API keys, `.env`, or any file containing secrets.
