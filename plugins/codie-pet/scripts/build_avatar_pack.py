#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit("Pillow is required. Install it with `python3 -m pip install Pillow`.") from exc


STATES = ("idle", "peek", "loading", "coding", "error", "done")
STATE_META = {
    "idle": ("Idle", "General chat, thinking, lightweight answers"),
    "peek": ("Peek", "Reading files, inspecting context, checking previews"),
    "loading": ("Loading", "Running commands, waiting, long tasks"),
    "coding": ("Coding", "Writing code, editing files, generating assets"),
    "error": ("Error", "Failed commands, failed tests, blocked work"),
    "done": ("Done", "Successful final results"),
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
    parser.add_argument("--frame-duration", type=int, default=180, help="GIF frame duration in milliseconds.")
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
        image = Image.open(strip_path).convert("RGBA")
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

    frame_width = image.width // 4
    out_dir.mkdir(parents=True, exist_ok=True)
    frame_paths: list[Path] = []
    for index in range(4):
        left = index * frame_width
        frame = image.crop((left, 0, left + frame_width, image.height))
        frame_path = out_dir / f"frame-{index + 1:02d}.png"
        frame.save(frame_path)
        frame_paths.append(frame_path)
    return frame_paths


def build_gif(frame_paths: list[Path], gif_path: Path, duration: int) -> None:
    images = [Image.open(path).convert("RGBA") for path in frame_paths]
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
        disposal=2,
    )


def write_config(paths: Paths) -> None:
    states = {}
    for state in STATES:
        label, use_when = STATE_META[state]
        states[state] = {
            "label": label,
            "gif": f"./gifs/{state}.gif",
            "useWhen": use_when,
        }
    config = {
        "version": 1,
        "style": "q-chibi",
        "frameCount": 4,
        "states": states,
    }
    (paths.root / "avatar.config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def render_contact_sheet(paths: Paths) -> None:
    gif_cells = []
    for state in STATES:
        frame = Image.open(paths.frames / state / "frame-01.png").convert("RGBA")
        gif_cells.append((state, frame))

    cell_w = max(image.width for _, image in gif_cells)
    cell_h = max(image.height for _, image in gif_cells)
    label_h = 22
    gap = 12
    columns = 3
    rows = 2
    width = columns * cell_w + (columns + 1) * gap
    height = rows * (cell_h + label_h) + (rows + 1) * gap
    sheet = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(sheet)

    for index, (state, image) in enumerate(gif_cells):
        row = index // columns
        col = index % columns
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + label_h + gap)
        draw.text((x, y), state, fill="black")
        sheet.alpha_composite(image, (x + (cell_w - image.width) // 2, y + label_h))

    paths.previews.mkdir(parents=True, exist_ok=True)
    sheet.save(paths.previews / "contact-sheet.png")


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
    require_strips(paths)
    for directory in (paths.frames, paths.gifs, paths.previews):
        directory.mkdir(parents=True, exist_ok=True)

    for state in STATES:
        frame_paths = slice_strip(paths.strips / f"{state}.png", paths.frames / state)
        build_gif(frame_paths, paths.gifs / f"{state}.gif", args.frame_duration)

    write_config(paths)
    render_contact_sheet(paths)
    write_preview_html(paths)
    print(f"Built CodiePet pack at {paths.root}")


if __name__ == "__main__":
    main()
