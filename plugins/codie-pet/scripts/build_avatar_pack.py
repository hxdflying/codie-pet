#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from avatar_image import (
    RgbaImage,
    new_rgba,
    pad_to_canvas,
    paste_rgba,
    read_png,
    write_gif,
    write_png,
)


STATES = ("idle", "peek", "loading", "coding", "error", "done")
STATE_META = {
    "idle": ("Idle", "General chat, thinking, lightweight answers", 280),
    "peek": ("Peek", "Reading files, inspecting context, checking previews", 220),
    "loading": ("Loading", "Running commands, waiting, long tasks", 130),
    "coding": ("Coding", "Writing code, editing files, generating assets", 180),
    "error": ("Error", "Failed commands, failed tests, blocked work", 260),
    "done": ("Done", "Successful final results", 240),
}


@dataclass(frozen=True)
class Paths:
    workspace: Path
    root: Path
    strips: Path
    frames: Path
    gifs: Path
    previews: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build CodiePet GIF pack from six four-frame strips.")
    parser.add_argument("--workspace", default=".", help="Workspace root. Default: current directory.")
    parser.add_argument(
        "--frame-duration",
        type=int,
        default=None,
        help="Override the per-state defaults; applies one duration (ms) to every GIF.",
    )
    return parser.parse_args()


def resolve_paths(workspace: str) -> Paths:
    root_workspace = Path(workspace).resolve()
    root = root_workspace / "codie-pet"
    return Paths(
        workspace=root_workspace,
        root=root,
        strips=root / "strips",
        frames=root / "frames",
        gifs=root / "gifs",
        previews=root / "previews",
    )


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def require_strips(paths: Paths) -> None:
    for state in STATES:
        strip = paths.strips / f"{state}.png"
        if not strip.is_file():
            fail(f"Missing required strip: {state}.png")


def slice_strip(strip_path: Path, out_dir: Path) -> list[Path]:
    try:
        image = read_png(strip_path)
    except Exception as exc:
        fail(f"Cannot open strip {strip_path.name}: {exc}")

    if image.height < 1 or image.width < 4:
        fail(f"Invalid strip {strip_path.name}: image is too small")

    if image.width % 4 != 0:
        trimmed_width = image.width - (image.width % 4)
        print(
            f"warning: strip {strip_path.name} width {image.width} is not divisible by 4, "
            f"trimming to {trimmed_width}",
            file=sys.stderr,
        )
        image = image.crop((0, 0, trimmed_width, image.height))

    out_dir.mkdir(parents=True, exist_ok=True)
    for stale_frame in out_dir.glob("frame-*.png"):
        if stale_frame.is_file() or stale_frame.is_symlink():
            stale_frame.unlink()

    frame_width = image.width // 4
    frame_paths: list[Path] = []
    for index in range(4):
        left = index * frame_width
        frame = image.crop((left, 0, left + frame_width, image.height))
        frame_path = out_dir / f"frame-{index + 1:02d}.png"
        write_png(frame_path, frame)
        frame_paths.append(frame_path)
    return frame_paths


def build_gif(frame_paths: list[Path], gif_path: Path, duration: int) -> None:
    write_gif(gif_path, [read_png(path) for path in frame_paths], duration)


def normalize_frames(frame_paths: list[Path], canvas_size: tuple[int, int]) -> None:
    for path in frame_paths:
        rgba = read_png(path)
        if rgba.width > canvas_size[0] or rgba.height > canvas_size[1]:
            fail(f"Frame {path} is larger than the target canvas")
        write_png(path, pad_to_canvas(rgba, canvas_size))


def target_canvas_size(all_frame_paths: dict[str, list[Path]]) -> tuple[int, int]:
    sizes = []
    for frame_paths in all_frame_paths.values():
        for frame_path in frame_paths:
            image = read_png(frame_path)
            sizes.append((image.width, image.height))
    return max(width for width, _ in sizes), max(height for _, height in sizes)


def write_config(paths: Paths, durations: dict[str, int]) -> None:
    states = {}
    for state in STATES:
        label, use_when, _ = STATE_META[state]
        states[state] = {
            "label": label,
            "gif": f"./gifs/{state}.gif",
            "useWhen": use_when,
            "frameDurationMs": durations[state],
        }
    config = {
        "version": 1,
        "style": "q-chibi",
        "frameCount": 4,
        "states": states,
    }
    (paths.root / "avatar.config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def render_contact_sheet(paths: Paths) -> None:
    gif_cells: list[tuple[str, RgbaImage]] = []
    for state in STATES:
        frame = read_png(paths.frames / state / "frame-01.png")
        gif_cells.append((state, frame))

    cell_w = max(image.width for _, image in gif_cells)
    cell_h = max(image.height for _, image in gif_cells)
    gap = 12
    columns = 3
    rows = 2
    width = columns * cell_w + (columns + 1) * gap
    height = rows * cell_h + (rows + 1) * gap
    sheet = bytearray(new_rgba(width, height, (255, 255, 255, 255)).pixels)

    for index, (state, image) in enumerate(gif_cells):
        row = index // columns
        col = index % columns
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + gap)
        paste_rgba(sheet, width, image, x + (cell_w - image.width) // 2, y)

    paths.previews.mkdir(parents=True, exist_ok=True)
    write_png(paths.previews / "contact-sheet.png", RgbaImage(width, height, bytes(sheet)))


def write_preview_html(paths: Paths) -> None:
    cards = "\n".join(
        f'      <section><h2>{state}</h2><img src="../gifs/{state}.gif" alt="{state} avatar GIF"></section>'
        for state in STATES
    )
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CodiePet Preview</title>
    <style>
      body {{ font-family: system-ui, sans-serif; margin: 24px; background: #f7f7f7; color: #111; }}
      main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; }}
      section {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 16px; text-align: center; }}
      h1 {{ font-size: 22px; }}
      h2 {{ font-size: 14px; margin: 0 0 12px; }}
      img {{ max-width: 100%; image-rendering: auto; }}
    </style>
  </head>
  <body>
    <h1>CodiePet Preview</h1>
    <main>
{cards}
    </main>
  </body>
</html>
"""
    paths.previews.mkdir(parents=True, exist_ok=True)
    (paths.previews / "preview.html").write_text(html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    paths = resolve_paths(args.workspace)
    if args.frame_duration is not None and args.frame_duration <= 0:
        fail("frame duration must be a positive integer")
    require_strips(paths)
    for directory in (paths.frames, paths.gifs, paths.previews):
        directory.mkdir(parents=True, exist_ok=True)

    durations = {
        state: args.frame_duration if args.frame_duration is not None else STATE_META[state][2]
        for state in STATES
    }

    all_frame_paths = {
        state: slice_strip(paths.strips / f"{state}.png", paths.frames / state)
        for state in STATES
    }
    canvas_size = target_canvas_size(all_frame_paths)

    for state, frame_paths in all_frame_paths.items():
        normalize_frames(frame_paths, canvas_size)
        build_gif(frame_paths, paths.gifs / f"{state}.gif", durations[state])

    write_config(paths, durations)
    render_contact_sheet(paths)
    write_preview_html(paths)
    print(f"Built CodiePet pack at {paths.root}")


if __name__ == "__main__":
    main()
