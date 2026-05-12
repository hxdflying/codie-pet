from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


def _first_lzw_min_code_size_offset(data: bytes) -> int:
    offset = 13
    packed = data[10]
    if packed & 0x80:
        offset += 3 * (2 ** ((packed & 0x07) + 1))
    while offset < len(data):
        marker = data[offset]
        offset += 1
        if marker == 0x21:
            offset += 1
            while True:
                block_length = data[offset]
                offset += 1
                if block_length == 0:
                    break
                offset += block_length
        elif marker == 0x2C:
            return offset + 9
        elif marker == 0x3B:
            break
        else:
            raise ValueError(f"unexpected GIF marker 0x{marker:02x}")
    raise ValueError("GIF has no image descriptor")


def test_validator_passes_for_built_pack(built_workspace: Path, run_script) -> None:
    result = run_script("validate", built_workspace)

    assert result.returncode == 0, result.stderr
    assert "CodiePet pack validation passed" in result.stdout


def test_validator_passes_for_complex_built_gifs(
    strip_workspace: Path, run_script, states
) -> None:
    root = strip_workspace / "codie-pet"
    for state in states:
        image = Image.new("RGBA", (64 * 4, 64), (255, 255, 255, 255))
        pixels = image.load()
        for frame_index in range(4):
            for y in range(64):
                for x in range(64):
                    pixels[frame_index * 64 + x, y] = (
                        (x + y + frame_index * 37) % 256,
                        (x * 3 + frame_index * 29) % 256,
                        (y * 5 + frame_index * 13) % 256,
                        255,
                    )
        image.save(root / "strips" / f"{state}.png")

    build = run_script("build", strip_workspace)
    assert build.returncode == 0, build.stderr

    result = run_script("validate", strip_workspace)

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


def test_validator_reports_undecodable_gif_lzw_data(
    built_workspace: Path, run_script
) -> None:
    gif = built_workspace / "codie-pet" / "gifs" / "idle.gif"
    data = bytearray(gif.read_bytes())
    data[_first_lzw_min_code_size_offset(data)] = 12
    gif.write_bytes(data)

    result = run_script("validate", built_workspace)

    assert result.returncode == 2
    assert "Invalid GIF: idle.gif" in result.stderr
    assert "LZW" in result.stderr


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
