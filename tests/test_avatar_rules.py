from __future__ import annotations

from pathlib import Path


def test_install_creates_agents_file_with_managed_block(
    tmp_path: Path, run_script
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    result = run_script("install", workspace)

    assert result.returncode == 0, result.stderr
    content = (workspace / "AGENTS.md").read_text()
    assert "<!-- codie-pet:start -->" in content
    assert "<!-- codie-pet:end -->" in content
    assert "./codie-pet/gifs/" in content


def test_install_preserves_unrelated_content_and_replaces_existing_block(
    tmp_path: Path, run_script
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    agents = workspace / "AGENTS.md"
    agents.write_text(
        "# Project Rules\n\nKeep this.\n\n"
        "<!-- codie-pet:start -->\nold block\n<!-- codie-pet:end -->\n\n"
        "Keep this too.\n"
    )

    result = run_script("install", workspace)

    assert result.returncode == 0, result.stderr
    content = agents.read_text()
    assert "Keep this." in content
    assert "Keep this too." in content
    assert "old block" not in content
    assert content.count("<!-- codie-pet:start -->") == 1
    assert content.count("<!-- codie-pet:end -->") == 1


def test_uninstall_removes_only_managed_block(
    tmp_path: Path, run_script
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    install = run_script("install", workspace)
    assert install.returncode == 0, install.stderr
    agents = workspace / "AGENTS.md"
    agents.write_text(
        "# Project Rules\n\nKeep this.\n\n" + agents.read_text() + "\nKeep this too.\n"
    )

    result = run_script("uninstall", workspace)

    assert result.returncode == 0, result.stderr
    content = agents.read_text()
    assert "<!-- codie-pet:start -->" not in content
    assert "<!-- codie-pet:end -->" not in content
    assert "Keep this." in content
    assert "Keep this too." in content
