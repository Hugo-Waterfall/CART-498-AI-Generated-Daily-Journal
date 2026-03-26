#!/usr/bin/env python3

import argparse
import base64
import mimetypes
import os
from datetime import datetime
from pathlib import Path


DEFAULT_INPUT_DIR = Path("input_images")
DEFAULT_OUTPUT_FILE = Path("descriptions.txt")
DEFAULT_IMAGE_MODEL = "gpt-4.1-mini"
DEFAULT_NARRATIVE_MODEL = "gpt-5.4"

DEFAULT_PROMPT = (
    "Describe this image in two parts:"
    "1. Objective Description - Clearly and precisely describe only what is directly visible in the image (people, objects, setting, actions) without interpretation."
    "2. Inferred Context (Uncertain) - Suggest possible emotions, intentions, or situations based on the image. These should be speculative and expressed with uncertainty (e.g., “perhaps,” “it seems,” “likely”)."
    "Avoid making definitive claims about things that cannot be directly observed."
)

DEFAULT_NARRATIVE_PROMPT = (
    "Write a short, 2-3 sentence first-person journal entry based on the following image descriptions. The entry should describe a single day, moving from morning to evening, using the first description as the beginning and the last as the end."
    "Create a smooth and engaging narrative by filling in gaps between moments, inferring emotions, intentions, and events where necessary. These inferences should feel natural and believable, but not definitively certain."
    "The tone should resemble a social-media-style reflection: engaging, reflective, slightly idealized, slightly polished and narratively cohesive."
    "The narrative should read as if it confidently tells a story, even though it is built from incomplete and potentially misleading information."
    "Do not mention that the information is based on images."
)
SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze all images in a folder and append descriptions to a text file."
    )
    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT_DIR),
        help=f"Folder containing images to analyze. Default: {DEFAULT_INPUT_DIR}",
    )
    parser.add_argument(
        "--output-file",
        default=str(DEFAULT_OUTPUT_FILE),
        help=f"Text file to append descriptions to. Default: {DEFAULT_OUTPUT_FILE}",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help=f"Instruction for the model. Default: {DEFAULT_PROMPT!r}",
    )
    parser.add_argument(
        "--image-model",
        default=DEFAULT_IMAGE_MODEL,
        help=f"OpenAI model to use for image descriptions. Default: {DEFAULT_IMAGE_MODEL}",
    )
    parser.add_argument(
        "--narrative-model",
        default=DEFAULT_NARRATIVE_MODEL,
        help=f"OpenAI model to use for the narrative. Default: {DEFAULT_NARRATIVE_MODEL}",
    )
    parser.add_argument(
        "--narrative-prompt",
        default=DEFAULT_NARRATIVE_PROMPT,
        help="Instruction for generating the final narrative.",
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


def collect_image_paths(input_dir: str) -> list[Path]:
    directory = Path(input_dir).expanduser().resolve()
    if not directory.is_dir():
        raise SystemExit(f"Input folder not found: {directory}")

    image_paths = sorted(
        path
        for path in directory.iterdir()
        if path.is_file()
        and not path.name.startswith(".")
        and path.suffix.lower() in SUPPORTED_SUFFIXES
    )

    if not image_paths:
        raise SystemExit(f"No supported image files found in {directory}")

    return image_paths


def build_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path.name)
    if mime_type is None or not mime_type.startswith("image/"):
        raise SystemExit(
            f"Unsupported or unknown image type for {image_path.name}. Use a PNG, JPEG, WEBP, or GIF file."
        )

    encoded_image = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_image}"


def analyze_image(client, image_path: Path, prompt: str, model: str) -> str:
    image_source = build_data_url(image_path)
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_source},
                ],
            }
        ],
    )
    return response.output_text.strip()


def build_narrative_prompt(base_prompt: str, descriptions: list[str]) -> str:
    numbered_descriptions = [
        f"Description {index}: {description}"
        for index, description in enumerate(descriptions, start=1)
    ]
    return f"{base_prompt}\n\nHere are the descriptions:\n" + "\n".join(numbered_descriptions)


def generate_narrative(
    client, descriptions: list[str], narrative_prompt: str, narrative_model: str
) -> str:
    response = client.responses.create(
        model=narrative_model,
        input=build_narrative_prompt(narrative_prompt, descriptions),
    )
    return response.output_text.strip()


def append_descriptions(
    output_file: str, descriptions: list[tuple[Path, str]], narrative: str
) -> Path:
    output_path = Path(output_file).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"Run: {timestamp}", ""]

    for image_path, description in descriptions:
        lines.append(f"Image: {image_path.name}")
        lines.append(description or "[No description returned]")
        lines.append("")

    lines.append("Narrative:")
    lines.append(narrative or "[No narrative returned]")
    lines.append("")

    with output_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return output_path


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

    image_paths = collect_image_paths(args.input_dir)
    client = OpenAI()
    descriptions = []

    for image_path in image_paths:
        description = analyze_image(client, image_path, args.prompt, args.image_model)
        descriptions.append((image_path, description))
        print(f"Analyzed {image_path.name}")

    narrative = generate_narrative(
        client,
        [description for _, description in descriptions],
        args.narrative_prompt,
        args.narrative_model,
    )
    print("Generated narrative")

    output_path = append_descriptions(args.output_file, descriptions, narrative)
    print(
        f"Appended descriptions and narrative for {len(descriptions)} images to {output_path}"
    )


if __name__ == "__main__":
    main()
