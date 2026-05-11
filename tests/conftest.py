from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "plugins" / "codie-pet" / "scripts"
SCRIPTS = {
    "build": SCRIPTS_DIR / "build_avatar_pack.py",
    "validate": SCRIPTS_DIR / "validate_avatar_pack.py",
    "install": SCRIPTS_DIR / "install_avatar_rules.py",
    "uninstall": SCRIPTS_DIR / "uninstall_avatar_rules.py",
}

STATES = ("idle", "peek", "loading", "coding", "error", "done")


def _make_strip(path: Path, frame_size: tuple[int, int] = (32, 32), frames: int = 4) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = frame_size[0] * frames
    height = frame_size[1]
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    colors = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6"]
    for index in range(frames):
        left = index * frame_size[0]
        draw.rectangle(
            (left + 4, 4, left + frame_size[0] - 4, frame_size[1] - 4),
            fill=colors[index % len(colors)],
        )
    image.save(path)


@pytest.fixture
def make_strip():
    return _make_strip


@pytest.fixture
def states() -> tuple[str, ...]:
    return STATES


@pytest.fixture
def strip_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    for state in STATES:
        _make_strip(workspace / "codie-pet" / "strips" / f"{state}.png")
    return workspace


@pytest.fixture
def run_script():
    def _run(name: str, workspace: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS[name]), "--workspace", str(workspace), *extra_args],
            text=True,
            capture_output=True,
            check=False,
        )

    return _run


@pytest.fixture
def built_workspace(strip_workspace: Path, run_script) -> Path:
    result = run_script("build", strip_workspace)
    assert result.returncode == 0, result.stderr
    return strip_workspace
