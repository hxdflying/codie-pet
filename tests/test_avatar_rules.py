from __future__ import annotations

import subprocess
import sys
from pathlib import Path


INSTALL = Path("plugins/codie-pet/scripts/install_avatar_rules.py")
UNINSTALL = Path("plugins/codie-pet/scripts/uninstall_avatar_rules.py")


def run_script(script: Path, workspace: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--workspace", str(workspace)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_install_creates_agents_file_with_managed_block(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    result = run_script(INSTALL, workspace)

    assert result.returncode == 0, result.stderr
    content = (workspace / "AGENTS.md").read_text()
    assert "<!-- codie-pet:start -->" in content
    assert "<!-- codie-pet:end -->" in content
    assert "./codie-pet/gifs/" in content


def test_install_preserves_unrelated_content_and_replaces_existing_block(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    agents = workspace / "AGENTS.md"
    agents.write_text(
        "# Project Rules\n\nKeep this.\n\n"
        "<!-- codie-pet:start -->\nold block\n<!-- codie-pet:end -->\n\n"
        "Keep this too.\n"
    )

    result = run_script(INSTALL, workspace)

    assert result.returncode == 0, result.stderr
    content = agents.read_text()
    assert "Keep this." in content
    assert "Keep this too." in content
    assert "old block" not in content
    assert content.count("<!-- codie-pet:start -->") == 1
    assert content.count("<!-- codie-pet:end -->") == 1


def test_uninstall_removes_only_managed_block(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    install = run_script(INSTALL, workspace)
    assert install.returncode == 0, install.stderr
    agents = workspace / "AGENTS.md"
    agents.write_text("# Project Rules\n\nKeep this.\n\n" + agents.read_text() + "\nKeep this too.\n")

    result = run_script(UNINSTALL, workspace)

    assert result.returncode == 0, result.stderr
    content = agents.read_text()
    assert "<!-- codie-pet:start -->" not in content
    assert "<!-- codie-pet:end -->" not in content
    assert "Keep this." in content
    assert "Keep this too." in content
