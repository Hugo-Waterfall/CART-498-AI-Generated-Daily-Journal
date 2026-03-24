# CART-498-AI-Generated-Daily-Journal

Small Python utility for analyzing all images in `input_images`, generating a short narrative from the resulting descriptions, and appending both the descriptions and the narrative to `descriptions.txt`.

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

Analyze every supported image in `input_images`, generate a narrative from the eight descriptions, and append the results to `descriptions.txt`:

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

Override the image-analysis model or the narrative model:

```bash
python3 analyze_image.py \
  --image-model "gpt-4.1-mini" \
  --narrative-model "gpt-5.4"
```

## Notes

- The default image-description model is `gpt-4.1-mini`.
- The default narrative model is `gpt-5.4`.
- The script skips hidden files like `.DS_Store`.
- The script appends each run to `descriptions.txt`, so previous descriptions and narratives are preserved.
- Never commit your real API key, `.env`, or any file containing secrets.


Terminal command (replace the url with any image url you want)
python3 analyze_image.py --image-url "https://static.wikia.nocookie.net/obamium/images/c/cd/Screenshot_20.jpg/revision/latest?cb=20210915024847"
