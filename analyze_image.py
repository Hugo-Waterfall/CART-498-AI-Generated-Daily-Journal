#!/usr/bin/env python3

import argparse
import base64
import mimetypes
import os
from pathlib import Path


DEFAULT_PROMPT = "Describe this image in clear, detailed text."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze one image with OpenAI and return a text interpretation."
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--image-url",
        help="A public image URL to analyze.",
    )
    source_group.add_argument(
        "--image-path",
        help="A local image file to analyze.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help=f"Instruction for the model. Default: {DEFAULT_PROMPT!r}",
    )
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="OpenAI model to use. Default: gpt-4.1-mini",
    )
    return parser.parse_args()


def load_local_env() -> None:
    env_path = Path(".env")
    if not env_path.is_file():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def require_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "Missing OPENAI_API_KEY. Export it in your shell or load it from a local .env file before running this script."
        )


def build_data_url(image_path: str) -> str:
    path = Path(image_path).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"Image file not found: {path}")

    mime_type, _ = mimetypes.guess_type(path.name)
    if mime_type is None or not mime_type.startswith("image/"):
        raise SystemExit(
            f"Unsupported or unknown image type for {path.name}. Use a PNG, JPEG, WEBP, or GIF file."
        )

    encoded_image = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_image}"


def resolve_image_source(args: argparse.Namespace) -> str:
    if args.image_url:
        return args.image_url
    return build_data_url(args.image_path)


def main() -> None:
    args = parse_args()
    load_local_env()
    require_api_key()

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: openai. Install it with `pip install -r requirements.txt`."
        ) from exc

    client = OpenAI()
    image_source = resolve_image_source(args)

    response = client.responses.create(
        model=args.model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": args.prompt},
                    {"type": "input_image", "image_url": image_source},
                ],
            }
        ],
    )

    print(response.output_text)


if __name__ == "__main__":
    main()
