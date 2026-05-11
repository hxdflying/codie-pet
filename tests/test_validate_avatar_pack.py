from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from test_build_avatar_pack import make_workspace, run_builder


VALIDATOR = Path("plugins/codie-pet/scripts/validate_avatar_pack.py")


def run_validator(workspace: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--workspace", str(workspace)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_validator_passes_for_built_pack(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    built = run_builder(workspace)
    assert built.returncode == 0, built.stderr

    result = run_validator(workspace)

    assert result.returncode == 0, result.stderr
    assert "CodiePet pack validation passed" in result.stdout


def test_validator_reports_missing_gif(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    built = run_builder(workspace)
    assert built.returncode == 0, built.stderr
    (workspace / "codie-pet" / "gifs" / "done.gif").unlink()

    result = run_validator(workspace)

    assert result.returncode == 2
    assert "Missing GIF: done.gif" in result.stderr
