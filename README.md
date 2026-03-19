# CART-498-AI-Generated-Daily-Journal

Small Python utility for analyzing a single image with the OpenAI Responses API and turning it into text.

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

3. Add your API key without hardcoding it into the script:

```bash
cp .env.example .env
```

Then edit `.env` and add your real key:

```bash
OPENAI_API_KEY=your_real_key_here
```

Load it into your shell:

```bash
set -a
source .env
set +a
```

`.env` is ignored by Git, so it will not be committed to GitHub unless you remove that rule.

## Run

Analyze a public image URL:

```bash
python3 analyze_image.py --image-url "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg"
```

Analyze a local image file:

```bash
python3 analyze_image.py --image-path "/path/to/image.jpg"
```

Use a custom prompt:

```bash
python3 analyze_image.py \
  --image-path "/path/to/image.jpg" \
  --prompt "Describe this image like a journal entry prompt, including mood, setting, and notable details."
```

## Notes

- The default model is `gpt-4.1-mini`, but you can override it with `--model`.
- The script accepts exactly one image at a time.
- Never commit your real API key, `.env`, or any file containing secrets.


Terminal command (replace the url with any image url you want)
python3 analyze_image.py --image-url "https://static.wikia.nocookie.net/obamium/images/c/cd/Screenshot_20.jpg/revision/latest?cb=20210915024847"
