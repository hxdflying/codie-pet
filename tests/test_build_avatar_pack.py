from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageSequence


def test_builds_gifs_frames_config_and_previews(
    strip_workspace: Path, run_script, states
) -> None:
    result = run_script("build", strip_workspace)

    assert result.returncode == 0, result.stderr
    root = strip_workspace / "codie-pet"
    for state in states:
        assert (root / "gifs" / f"{state}.gif").is_file()
        frames = sorted((root / "frames" / state).glob("frame-*.png"))
        assert len(frames) == 4
    config = json.loads((root / "avatar.config.json").read_text())
    assert config["version"] == 1
    assert config["style"] == "q-chibi"
    assert config["frameCount"] == 4
    assert set(config["states"]) == set(states)
    assert (root / "previews" / "contact-sheet.png").is_file()
    assert (root / "previews" / "preview.html").is_file()


def test_build_writes_gifs_that_decode_for_complex_frames(
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

    result = run_script("build", strip_workspace)

    assert result.returncode == 0, result.stderr
    for state in states:
        with Image.open(root / "gifs" / f"{state}.gif") as gif:
            decoded_sizes = []
            for frame in ImageSequence.Iterator(gif):
                frame.load()
                decoded_sizes.append(frame.size)
        assert decoded_sizes == [(64, 64)] * 4


def test_missing_required_strip_fails_with_clear_message(
    strip_workspace: Path, run_script
) -> None:
    (strip_workspace / "codie-pet" / "strips" / "done.png").unlink()

    result = run_script("build", strip_workspace)

    assert result.returncode == 2
    assert "Missing required strip: done.png" in result.stderr


def test_non_divisible_strip_width_is_trimmed_with_warning(
    strip_workspace: Path, run_script
) -> None:
    bad = Image.new("RGBA", (130, 32), (255, 255, 255, 0))
    bad.save(strip_workspace / "codie-pet" / "strips" / "idle.png")

    result = run_script("build", strip_workspace)

    assert result.returncode == 0, result.stderr
    assert "trimming to 128" in result.stderr
    frames = sorted((strip_workspace / "codie-pet" / "frames" / "idle").glob("frame-*.png"))
    assert len(frames) == 4
    assert Image.open(frames[0]).width == 32


def test_build_removes_stale_frames_before_writing_new_output(
    strip_workspace: Path, run_script
) -> None:
    stale = strip_workspace / "codie-pet" / "frames" / "idle" / "frame-99.png"
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"stale")

    result = run_script("build", strip_workspace)

    assert result.returncode == 0, result.stderr
    assert not stale.exists()
    frames = sorted((strip_workspace / "codie-pet" / "frames" / "idle").glob("frame-*.png"))
    assert [frame.name for frame in frames] == [
        "frame-01.png",
        "frame-02.png",
        "frame-03.png",
        "frame-04.png",
    ]


def test_build_pads_all_frames_and_gifs_to_one_canvas(
    strip_workspace: Path, run_script, make_strip, states
) -> None:
    make_strip(
        strip_workspace / "codie-pet" / "strips" / "loading.png",
        frame_size=(40, 48),
    )

    result = run_script("build", strip_workspace)

    assert result.returncode == 0, result.stderr
    root = strip_workspace / "codie-pet"
    for state in states:
        for frame in (root / "frames" / state).glob("frame-*.png"):
            assert Image.open(frame).size == (40, 48)
        assert Image.open(root / "gifs" / f"{state}.gif").size == (40, 48)


def test_strip_smaller_than_four_pixels_fails(
    strip_workspace: Path, run_script
) -> None:
    bad = Image.new("RGBA", (3, 32), (255, 255, 255, 0))
    bad.save(strip_workspace / "codie-pet" / "strips" / "idle.png")

    result = run_script("build", strip_workspace)

    assert result.returncode == 2
    assert "image is too small" in result.stderr


def test_unopenable_strip_fails_with_clear_message(
    strip_workspace: Path, run_script
) -> None:
    bad = strip_workspace / "codie-pet" / "strips" / "idle.png"
    bad.write_bytes(b"this is not a valid PNG")

    result = run_script("build", strip_workspace)

    assert result.returncode == 2
    assert "Cannot open strip idle.png" in result.stderr


def test_states_record_per_state_frame_duration(
    strip_workspace: Path, run_script
) -> None:
    result = run_script("build", strip_workspace)
    assert result.returncode == 0, result.stderr
    config = json.loads(
        (strip_workspace / "codie-pet" / "avatar.config.json").read_text()
    )
    durations = {s: config["states"][s]["frameDurationMs"] for s in config["states"]}
    for state, value in durations.items():
        assert isinstance(value, int) and value > 0, state
    # Loading should be the fastest beat in the default mapping.
    assert durations["loading"] < durations["idle"]
    assert durations["loading"] < durations["done"]


def test_frame_duration_override_applies_to_all_states(
    strip_workspace: Path, run_script
) -> None:
    result = run_script("build", strip_workspace, "--frame-duration", "100")
    assert result.returncode == 0, result.stderr
    config = json.loads(
        (strip_workspace / "codie-pet" / "avatar.config.json").read_text()
    )
    for state in config["states"]:
        assert config["states"][state]["frameDurationMs"] == 100


def test_frame_duration_override_must_be_positive(
    strip_workspace: Path, run_script
) -> None:
    result = run_script("build", strip_workspace, "--frame-duration", "0")

    assert result.returncode == 2
    assert "frame duration must be a positive integer" in result.stderr
