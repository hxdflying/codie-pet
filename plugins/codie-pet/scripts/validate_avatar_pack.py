#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


STATES = ("idle", "peek", "loading", "coding", "error", "done")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a generated CodiePet pack.")
    parser.add_argument("--workspace", default=".", help="Workspace root. Default: current directory.")
    return parser.parse_args()


def error(message: str) -> None:
    print(message, file=sys.stderr)


def validate(workspace: Path) -> list[str]:
    failures: list[str] = []
    root = workspace / "codie-pet"
    for directory in ("frames", "gifs", "previews"):
        if not (root / directory).is_dir():
            failures.append(f"Missing directory: {directory}")

    for state in STATES:
        gif = root / "gifs" / f"{state}.gif"
        if not gif.is_file():
            failures.append(f"Missing GIF: {state}.gif")
        frame_dir = root / "frames" / state
        frames = sorted(frame_dir.glob("frame-*.png")) if frame_dir.is_dir() else []
        if len(frames) != 4:
            failures.append(f"Expected 4 frames for {state}, found {len(frames)}")

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
            if set(config.get("states", {})) != set(STATES):
                failures.append("avatar.config.json states do not match required states")

    if not (root / "previews" / "preview.html").is_file():
        failures.append("Missing preview.html")
    if not (root / "previews" / "contact-sheet.png").is_file():
        failures.append("Missing contact-sheet.png")

    return failures


def main() -> None:
    args = parse_args()
    failures = validate(Path(args.workspace).resolve())
    if failures:
        for failure in failures:
            error(failure)
        raise SystemExit(2)
    print("CodiePet pack validation passed")


if __name__ == "__main__":
    main()
