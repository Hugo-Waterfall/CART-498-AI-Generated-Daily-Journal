#!/usr/bin/env python3

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, abort, render_template, request, send_file, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from analyze_image import SUPPORTED_SUFFIXES, run_analysis_pipeline


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_ROOT = BASE_DIR / "web_uploads"
DEFAULT_OUTPUT_FILE = BASE_DIR / "descriptions.txt"
DEFAULT_AUDIO_DIR = BASE_DIR / "audio files"
MAX_UPLOAD_SIZE_BYTES = 32 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_BYTES


def is_supported_image(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_SUFFIXES


def ensure_project_child(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(BASE_DIR)
    except ValueError as exc:
        raise FileNotFoundError("Requested file is outside the project directory.") from exc
    return resolved


def ensure_audio_child(path: Path) -> Path:
    resolved = ensure_project_child(path)
    try:
        resolved.relative_to(DEFAULT_AUDIO_DIR.resolve())
    except ValueError as exc:
        raise FileNotFoundError("Requested file is outside the audio directory.") from exc
    return resolved


def save_uploaded_images(files) -> list[Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = UPLOAD_ROOT / f"run_{timestamp}_{uuid4().hex[:8]}"
    run_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    for index, file_storage in enumerate(files, start=1):
        original_name = file_storage.filename or f"image_{index}.jpg"
        if not is_supported_image(original_name):
            raise ValueError(
                f"Unsupported file type for {original_name}. Please upload PNG, JPG, JPEG, WEBP, or GIF images."
            )

        sanitized_name = secure_filename(original_name) or f"image_{index}{Path(original_name).suffix.lower()}"
        final_name = f"{index:02d}_{sanitized_name}"
        destination = run_dir / final_name
        file_storage.save(destination)
        saved_paths.append(destination)

    if not saved_paths:
        raise ValueError("Please upload at least one image.")

    return saved_paths


@app.route("/", methods=["GET", "POST"])
def index():
    context = {
        "error": None,
        "result": None,
    }

    if request.method == "POST":
        uploaded_files = [file for file in request.files.getlist("images") if file and file.filename]

        if not uploaded_files:
            context["error"] = "Choose one or more images to generate a narrative."
            return render_template("index.html", **context), 400

        try:
            saved_paths = save_uploaded_images(uploaded_files)
            result = run_analysis_pipeline(
                image_paths=saved_paths,
                output_file=str(DEFAULT_OUTPUT_FILE),
                audio_dir=str(DEFAULT_AUDIO_DIR),
            )
            audio_relative = result["audio_path"].resolve().relative_to(DEFAULT_AUDIO_DIR.resolve()).as_posix()
            context["result"] = {
                "image_count": len(saved_paths),
                "image_names": [path.name for path in saved_paths],
                "run_text": result["run_text"].strip(),
                "audio_url": url_for("serve_audio_file", relative_path=audio_relative),
                "audio_path": result["audio_path"].resolve().relative_to(BASE_DIR).as_posix(),
                "descriptions_path": result["output_path"].resolve().relative_to(BASE_DIR).as_posix(),
            }
        except ValueError as exc:
            context["error"] = str(exc)
            return render_template("index.html", **context), 400
        except SystemExit as exc:
            context["error"] = str(exc)
            return render_template("index.html", **context), 500
        except Exception as exc:
            context["error"] = str(exc)
            return render_template("index.html", **context), 500

    return render_template("index.html", **context)


@app.route("/audio/<path:relative_path>")
def serve_audio_file(relative_path: str):
    target_path = ensure_audio_child(DEFAULT_AUDIO_DIR / relative_path)
    if not target_path.is_file():
        abort(404)
    return send_file(target_path)


@app.errorhandler(RequestEntityTooLarge)
def handle_upload_too_large(_error):
    return (
        render_template(
            "index.html",
            error="Upload too large. Keep the total request under 32 MB.",
            result=None,
        ),
        413,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(debug=True, host="127.0.0.1", port=port)
