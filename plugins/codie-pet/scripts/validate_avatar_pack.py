#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageSequence
except ImportError as exc:
    raise SystemExit("Pillow is required. Install it with `python3 -m pip install Pillow`.") from exc


STATES = ("idle", "peek", "loading", "coding", "error", "done")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a generated CodiePet pack.")
    parser.add_argument("--workspace", default=".", help="Workspace root. Default: current directory.")
    return parser.parse_args()


def error(message: str) -> None:
    print(message, file=sys.stderr)


def validate_image_file(path: Path, label: str, expected_format: str) -> list[str]:
    try:
        with Image.open(path) as image:
            if image.format != expected_format:
                return [f"Invalid {label}: expected {expected_format}, found {image.format or 'unknown'}"]
            image.verify()
    except Exception as exc:
        return [f"Invalid {label}: {exc}"]
    return []


def image_size_label(size: tuple[int, int]) -> str:
    return f"{size[0]}x{size[1]}"


def inspect_image_file(
    path: Path, label: str, expected_format: str
) -> tuple[list[str], tuple[int, int] | None]:
    failures = validate_image_file(path, label, expected_format)
    if failures:
        return failures, None
    with Image.open(path) as image:
        return [], image.size


def validate_gif(path: Path, state: str) -> tuple[list[str], tuple[int, int] | None]:
    try:
        with Image.open(path) as image:
            if image.format != "GIF":
                return [
                    f"Invalid GIF: {path.name} (expected GIF, found {image.format or 'unknown'})"
                ], None
            size = image.size
            frame_count = getattr(image, "n_frames", 1)
            for frame in ImageSequence.Iterator(image):
                frame.copy()
    except Exception as exc:
        return [f"Invalid GIF: {path.name} ({exc})"], None

    if frame_count != 4:
        return [f"Expected 4 GIF frames for {state}, found {frame_count}"], size
    return [], size


def validate_state_config(config: dict) -> list[str]:
    failures: list[str] = []
    states_config = config.get("states", {})
    if not isinstance(states_config, dict):
        failures.append("avatar.config.json states must be an object")
        return failures

    if set(states_config) != set(STATES):
        failures.append("avatar.config.json states do not match required states")

    for state in STATES:
        state_config = states_config.get(state)
        if not isinstance(state_config, dict):
            failures.append(f"{state} config must be an object")
            continue
        if state_config.get("gif") != f"./gifs/{state}.gif":
            failures.append(f"{state} gif must be ./gifs/{state}.gif")
        if not isinstance(state_config.get("label"), str) or not state_config["label"].strip():
            failures.append(f"{state} label must be a non-empty string")
        if not isinstance(state_config.get("useWhen"), str) or not state_config["useWhen"].strip():
            failures.append(f"{state} useWhen must be a non-empty string")
        duration = state_config.get("frameDurationMs")
        if not isinstance(duration, int) or duration <= 0:
            failures.append(f"{state} frameDurationMs must be a positive integer")

    return failures


def validate(workspace: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    root = workspace / "codie-pet"
    for directory in ("frames", "gifs", "previews"):
        if not (root / directory).is_dir():
            failures.append(f"Missing directory: {directory}")

    if not (root / "source" / "character-preview.png").is_file():
        warnings.append(
            "Missing source/character-preview.png. Regeneration will need a new preview."
        )
    else:
        failures.extend(
            validate_image_file(
                root / "source" / "character-preview.png",
                "source/character-preview.png",
                "PNG",
            )
        )
    if not (root / "source" / "original.png").is_file():
        warnings.append("Missing source/original.png. Regeneration will need the original photo.")
    else:
        failures.extend(
            validate_image_file(root / "source" / "original.png", "source/original.png", "PNG")
        )

    canvas_size: tuple[int, int] | None = None
    for state in STATES:
        frame_dir = root / "frames" / state
        frames = sorted(frame_dir.glob("frame-*.png")) if frame_dir.is_dir() else []
        if len(frames) != 4:
            failures.append(f"Expected 4 frames for {state}, found {len(frames)}")
        for frame in frames:
            frame_failures, frame_size = inspect_image_file(
                frame, f"PNG frame for {state}: {frame.name}", "PNG"
            )
            failures.extend(frame_failures)
            if frame_size is None:
                continue
            if canvas_size is None:
                canvas_size = frame_size
            elif frame_size != canvas_size:
                failures.append(
                    f"PNG frame for {state}: {frame.name} size {image_size_label(frame_size)} "
                    f"does not match frame canvas {image_size_label(canvas_size)}"
                )

        gif = root / "gifs" / f"{state}.gif"
        if not gif.is_file():
            failures.append(f"Missing GIF: {state}.gif")
        else:
            gif_failures, gif_size = validate_gif(gif, state)
            failures.extend(gif_failures)
            if canvas_size is not None and gif_size is not None and gif_size != canvas_size:
                failures.append(
                    f"GIF {state}.gif size {image_size_label(gif_size)} "
                    f"does not match frame canvas {image_size_label(canvas_size)}"
                )

    config_path = root / "avatar.config.json"
    if not config_path.is_file():
        failures.append("Missing avatar.config.json")
    else:
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Invalid avatar.config.json: {exc}")
        else:
            if config.get("version") != 1:
                failures.append("avatar.config.json version must be 1")
            failures.extend(validate_state_config(config))

    if not (root / "previews" / "preview.html").is_file():
        failures.append("Missing preview.html")
    if not (root / "previews" / "contact-sheet.png").is_file():
        failures.append("Missing contact-sheet.png")

    return failures, warnings


def main() -> None:
    args = parse_args()
    failures, warnings = validate(Path(args.workspace).resolve())
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if failures:
        for failure in failures:
            error(failure)
        raise SystemExit(2)
    print("CodiePet pack validation passed")


if __name__ == "__main__":
    main()
