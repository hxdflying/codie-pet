from __future__ import annotations

import json
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
