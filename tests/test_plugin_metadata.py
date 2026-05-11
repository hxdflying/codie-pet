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
