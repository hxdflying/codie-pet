from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


def test_validator_passes_for_built_pack(built_workspace: Path, run_script) -> None:
    result = run_script("validate", built_workspace)

    assert result.returncode == 0, result.stderr
    assert "CodiePet pack validation passed" in result.stdout


def test_validator_reports_missing_gif(built_workspace: Path, run_script) -> None:
    (built_workspace / "codie-pet" / "gifs" / "done.gif").unlink()

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "Missing GIF: done.gif" in result.stderr


def test_validator_warns_when_character_preview_missing(
    built_workspace: Path, run_script
) -> None:
    result = run_script("validate", built_workspace)

    assert result.returncode == 0, result.stderr
    assert "source/character-preview.png" in result.stderr


def test_validator_warns_when_original_source_photo_missing(
    built_workspace: Path, run_script
) -> None:
    source_dir = built_workspace / "codie-pet" / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (8, 8), "white").save(source_dir / "character-preview.png")

    result = run_script("validate", built_workspace)

    assert result.returncode == 0, result.stderr
    assert "source/original.png" in result.stderr


def test_validator_silent_when_character_preview_present(
    built_workspace: Path, run_script
) -> None:
    source_dir = built_workspace / "codie-pet" / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (8, 8), "white").save(source_dir / "character-preview.png")
    Image.new("RGBA", (8, 8), "white").save(source_dir / "original.png")

    result = run_script("validate", built_workspace)

    assert result.returncode == 0, result.stderr
    assert "character-preview.png" not in result.stderr


def test_validator_reports_corrupt_frame_png(
    built_workspace: Path, run_script
) -> None:
    frame = built_workspace / "codie-pet" / "frames" / "idle" / "frame-01.png"
    frame.write_bytes(b"not a png")

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "Invalid PNG frame for idle: frame-01.png" in result.stderr


def test_validator_reports_corrupt_gif(
    built_workspace: Path, run_script
) -> None:
    gif = built_workspace / "codie-pet" / "gifs" / "idle.gif"
    gif.write_bytes(b"not a gif")

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "Invalid GIF: idle.gif" in result.stderr


def test_validator_reports_gif_with_wrong_frame_count(
    built_workspace: Path, run_script
) -> None:
    gif = built_workspace / "codie-pet" / "gifs" / "idle.gif"
    first_frame = built_workspace / "codie-pet" / "frames" / "idle" / "frame-01.png"
    Image.open(first_frame).save(gif, save_all=True)

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "Expected 4 GIF frames for idle" in result.stderr


def test_validator_reports_gif_size_mismatch(
    built_workspace: Path, run_script
) -> None:
    gif = built_workspace / "codie-pet" / "gifs" / "idle.gif"
    frames = [
        Image.new("RGB", (24, 24), color)
        for color in ("#ef4444", "#f59e0b", "#10b981", "#3b82f6")
    ]
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=100, loop=0)

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "GIF idle.gif size" in result.stderr
    assert "does not match frame canvas" in result.stderr


def test_validator_reports_corrupt_config_json(
    built_workspace: Path, run_script
) -> None:
    config = built_workspace / "codie-pet" / "avatar.config.json"
    config.write_text("{not valid json", encoding="utf-8")

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "Invalid avatar.config.json" in result.stderr


def test_validator_reports_wrong_config_version(
    built_workspace: Path, run_script
) -> None:
    config = built_workspace / "codie-pet" / "avatar.config.json"
    data = json.loads(config.read_text())
    data["version"] = 99
    config.write_text(json.dumps(data), encoding="utf-8")

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "version must be 1" in result.stderr


def test_validator_reports_mismatched_states(
    built_workspace: Path, run_script
) -> None:
    config = built_workspace / "codie-pet" / "avatar.config.json"
    data = json.loads(config.read_text())
    data["states"].pop("done")
    config.write_text(json.dumps(data), encoding="utf-8")

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "states do not match" in result.stderr


def test_validator_reports_invalid_state_config(
    built_workspace: Path, run_script
) -> None:
    config = built_workspace / "codie-pet" / "avatar.config.json"
    data = json.loads(config.read_text())
    data["states"]["idle"]["frameDurationMs"] = 0
    data["states"]["idle"].pop("gif")
    config.write_text(json.dumps(data), encoding="utf-8")

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "idle gif must be ./gifs/idle.gif" in result.stderr
    assert "idle frameDurationMs must be a positive integer" in result.stderr
