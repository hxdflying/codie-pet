from __future__ import annotations

from pathlib import Path


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


def test_validator_silent_when_character_preview_present(
    built_workspace: Path, run_script
) -> None:
    source_dir = built_workspace / "codie-pet" / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "character-preview.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    result = run_script("validate", built_workspace)

    assert result.returncode == 0, result.stderr
    assert "character-preview.png" not in result.stderr
