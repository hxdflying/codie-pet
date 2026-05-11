from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


STATES = ("idle", "peek", "loading", "coding", "error", "done")
SCRIPT = Path("plugins/codie-pet/scripts/build_avatar_pack.py")


def make_strip(path: Path, frame_size: tuple[int, int] = (32, 32), frames: int = 4) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = frame_size[0] * frames
    height = frame_size[1]
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    colors = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6"]
    for index in range(frames):
        left = index * frame_size[0]
        draw.rectangle((left + 4, 4, left + frame_size[0] - 4, frame_size[1] - 4), fill=colors[index % len(colors)])
    image.save(path)


def make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    for state in STATES:
        make_strip(workspace / "codie-pet" / "strips" / f"{state}.png")
    return workspace


def run_builder(workspace: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--workspace", str(workspace)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_builds_gifs_frames_config_and_previews(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)

    result = run_builder(workspace)

    assert result.returncode == 0, result.stderr
    root = workspace / "codie-pet"
    for state in STATES:
        assert (root / "gifs" / f"{state}.gif").is_file()
        frames = sorted((root / "frames" / state).glob("frame-*.png"))
        assert len(frames) == 4
    config = json.loads((root / "avatar.config.json").read_text())
    assert config["version"] == 1
    assert config["style"] == "q-chibi"
    assert config["frameCount"] == 4
    assert set(config["states"]) == set(STATES)
    assert (root / "previews" / "contact-sheet.png").is_file()
    assert (root / "previews" / "preview.html").is_file()


def test_missing_required_strip_fails_with_clear_message(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    (workspace / "codie-pet" / "strips" / "done.png").unlink()

    result = run_builder(workspace)

    assert result.returncode == 2
    assert "Missing required strip: done.png" in result.stderr


def test_non_divisible_strip_width_is_trimmed_with_warning(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    bad = Image.new("RGBA", (130, 32), (255, 255, 255, 0))
    bad.save(workspace / "codie-pet" / "strips" / "idle.png")

    result = run_builder(workspace)

    assert result.returncode == 0, result.stderr
    assert "trimming to 128" in result.stderr
    frames = sorted((workspace / "codie-pet" / "frames" / "idle").glob("frame-*.png"))
    assert len(frames) == 4
    assert Image.open(frames[0]).width == 32


def test_strip_smaller_than_four_pixels_fails(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    bad = Image.new("RGBA", (3, 32), (255, 255, 255, 0))
    bad.save(workspace / "codie-pet" / "strips" / "idle.png")

    result = run_builder(workspace)

    assert result.returncode == 2
    assert "image is too small" in result.stderr
