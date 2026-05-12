from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugins" / "codie-pet"


def load_plugin_manifest() -> dict:
    manifest = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    return json.loads(manifest.read_text(encoding="utf-8"))


def test_manifest_screenshots_exist_and_are_png_files() -> None:
    manifest = load_plugin_manifest()
    screenshots = manifest["interface"]["screenshots"]

    assert screenshots == ["./assets/screenshot-preview.png"]
    for screenshot in screenshots:
        path = PLUGIN_ROOT / screenshot
        assert path.is_file()
        with Image.open(path) as image:
            assert image.format == "PNG"
            assert image.width >= 800
            assert image.height >= 450


def test_manifest_policy_urls_point_to_tracked_docs() -> None:
    manifest = load_plugin_manifest()
    interface = manifest["interface"]

    assert interface["privacyPolicyURL"].endswith("/blob/main/docs/privacy.md")
    assert interface["termsOfServiceURL"].endswith("/blob/main/docs/terms.md")
    assert (REPO_ROOT / "docs" / "privacy.md").is_file()
    assert (REPO_ROOT / "docs" / "terms.md").is_file()


def test_marketplace_uses_publishable_name() -> None:
    marketplace = json.loads(
        (REPO_ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )

    assert marketplace["name"] == "codie-pet"
    assert marketplace["interface"]["displayName"] == "CodiePet"


def test_prompt_contract_uses_white_background_for_gif_outputs() -> None:
    prompts = (PLUGIN_ROOT / "skills" / "codie-pet" / "references" / "prompts.md").read_text(
        encoding="utf-8"
    )
    quality = (
        PLUGIN_ROOT / "skills" / "codie-pet" / "references" / "quality-checks.md"
    ).read_text(encoding="utf-8")

    assert "White background" in prompts
    assert "white background" in quality
    assert "transparent background" not in prompts.lower()
    assert "transparent background" not in quality.lower()


def test_runtime_scripts_do_not_depend_on_pillow() -> None:
    requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    script_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PLUGIN_ROOT / "scripts").glob("*.py")
    )

    assert "pillow" not in requirements
    assert "from PIL" not in script_sources
    assert "import PIL" not in script_sources


def test_docs_include_github_marketplace_install_path() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "codex plugin marketplace add hxdflying/codie-pet" in readme
    assert "codex plugin marketplace add hxdflying/codie-pet@v0.1.0" in readme


def test_skill_uses_installed_plugin_root_for_scripts() -> None:
    skill = (PLUGIN_ROOT / "skills" / "codie-pet" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "installed plugin root" in skill
    assert "plugins/codie-pet/scripts" not in skill

    workflow = (
        PLUGIN_ROOT / "skills" / "codie-pet" / "references" / "workflow.md"
    ).read_text(encoding="utf-8")
    assert "installed plugin root" in workflow
    assert "plugins/codie-pet/scripts" not in workflow
