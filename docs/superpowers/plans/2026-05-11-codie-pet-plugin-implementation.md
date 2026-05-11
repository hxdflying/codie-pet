# CodiePet Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the v0.1 local CodiePet plugin that guides single-person photo avatar generation, processes six four-frame state strips into GIFs, and installs workspace-local `AGENTS.md` response rules.

**Architecture:** The plugin is a local Codex bundle under `plugins/codie-pet/`. The skill owns user workflow and image-generation prompting, while Python scripts own deterministic local processing: slicing strips, generating GIFs, validating output, and managing the `AGENTS.md` block. Tests exercise the scripts with synthetic images so the core file-processing behavior is reliable without model calls.

**Tech Stack:** Codex plugin manifest, Codex skill markdown, Python 3.11-compatible scripts, Pillow for image processing, pytest for tests, JSON config files, local workspace files.

---

## File Map

- `plugins/codie-pet/.codex-plugin/plugin.json`: Codex plugin manifest and UI metadata.
- `plugins/codie-pet/skills/codie-pet/SKILL.md`: Workflow instructions Codex loads when users ask to create, install, regenerate, disable, or remove an avatar.
- `plugins/codie-pet/skills/codie-pet/references/workflow.md`: Detailed v0.1 workflow and state machine.
- `plugins/codie-pet/skills/codie-pet/references/prompts.md`: Character preview prompt and per-state strip prompt templates.
- `plugins/codie-pet/skills/codie-pet/references/quality-checks.md`: Acceptance checks for input photos, previews, strips, and final GIF packs.
- `plugins/codie-pet/scripts/build_avatar_pack.py`: Builds frames, GIFs, `avatar.config.json`, contact sheet, and preview HTML from six state strips.
- `plugins/codie-pet/scripts/validate_avatar_pack.py`: Checks generated pack completeness and prints a pass/fail report.
- `plugins/codie-pet/scripts/install_avatar_rules.py`: Inserts or replaces the managed `codie-pet` block in workspace `AGENTS.md`.
- `plugins/codie-pet/scripts/uninstall_avatar_rules.py`: Removes the managed `codie-pet` block from workspace `AGENTS.md`.
- `plugins/codie-pet/assets/icon-small.svg`: Small composer icon.
- `plugins/codie-pet/assets/icon.png`: Plugin logo asset. Use a tiny generated PNG in v0.1.
- `.agents/plugins/marketplace.json`: Repo-local marketplace entry for local testing and sharing.
- `README.md`: Installation, desktop app usage, privacy, limitations, and development instructions.
- `requirements-dev.txt`: Test and script dependencies.
- `tests/test_build_avatar_pack.py`: Unit tests for strip slicing, GIF/config/preview output, and missing strip errors.
- `tests/test_avatar_rules.py`: Unit tests for installing, replacing, preserving, and uninstalling `AGENTS.md` rules.
- `tests/test_validate_avatar_pack.py`: Unit tests for validation pass and failure reports.

---

### Task 1: Repository Setup and Dependencies

**Files:**
- Create: `requirements-dev.txt`
- Create: `.gitignore`

- [ ] **Step 1: Create dependency file**

Create `requirements-dev.txt`:

```text
Pillow>=10.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Create ignore file**

Create `.gitignore`:

```gitignore
__pycache__/
.pytest_cache/
*.pyc
.venv/
codie-pet/
```

- [ ] **Step 3: Verify dependency file is readable**

Run:

```bash
python3 -m pip install -r requirements-dev.txt
```

Expected: dependencies are already satisfied or install successfully. If the environment blocks downloads, rerun with approval according to sandbox instructions.

- [ ] **Step 4: Commit**

Run only after the workspace is a valid git repository:

```bash
git add requirements-dev.txt .gitignore
git commit -m "chore: add development dependencies"
```

Expected: commit succeeds. If `git rev-parse --show-toplevel` fails, initialize or repair the repository before using commit steps.

---

### Task 2: Plugin Manifest and Marketplace Entry

**Files:**
- Create: `plugins/codie-pet/.codex-plugin/plugin.json`
- Create: `plugins/codie-pet/assets/icon-small.svg`
- Create: `plugins/codie-pet/assets/icon.png`
- Create: `.agents/plugins/marketplace.json`

- [ ] **Step 1: Create plugin directories**

Run:

```bash
mkdir -p plugins/codie-pet/.codex-plugin plugins/codie-pet/assets .agents/plugins
```

Expected: directories exist.

- [ ] **Step 2: Create plugin manifest**

Create `plugins/codie-pet/.codex-plugin/plugin.json`:

```json
{
  "name": "codie-pet",
  "version": "0.1.0",
  "description": "Create a Q-style animated avatar pack for Codex workspace replies.",
  "author": {
    "name": "Xudong Han",
    "email": "support@example.com",
    "url": "https://github.com/"
  },
  "homepage": "https://github.com/",
  "repository": "https://github.com/",
  "license": "MIT",
  "keywords": [
    "avatar",
    "gif",
    "codex",
    "workspace",
    "personalization"
  ],
  "skills": "./skills/",
  "interface": {
    "displayName": "CodiePet",
    "shortDescription": "Turn one person photo into Codex state GIFs",
    "longDescription": "Guides Codex through creating a Q-style animated avatar pack from one single-person photo, then installs workspace rules so Codex can use local state GIFs in replies.",
    "developerName": "Xudong Han",
    "category": "Productivity",
    "capabilities": [
      "Interactive",
      "Write"
    ],
    "websiteURL": "https://github.com/",
    "privacyPolicyURL": "https://github.com/",
    "termsOfServiceURL": "https://github.com/",
    "defaultPrompt": [
      "Create my CodiePet from this photo",
      "Install CodiePet in this workspace",
      "Remove CodiePet from this workspace"
    ],
    "brandColor": "#10A37F",
    "composerIcon": "./assets/icon-small.svg",
    "logo": "./assets/icon.png",
    "screenshots": []
  }
}
```

- [ ] **Step 3: Create small SVG icon**

Create `plugins/codie-pet/assets/icon-small.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="CodiePet">
  <rect width="64" height="64" rx="14" fill="#10A37F"/>
  <circle cx="32" cy="25" r="13" fill="#FFFFFF"/>
  <path d="M16 53c2-11 10-18 16-18s14 7 16 18" fill="#FFFFFF"/>
  <circle cx="27" cy="24" r="2.2" fill="#10A37F"/>
  <circle cx="37" cy="24" r="2.2" fill="#10A37F"/>
  <path d="M27 31c3 3 7 3 10 0" fill="none" stroke="#10A37F" stroke-width="3" stroke-linecap="round"/>
</svg>
```

- [ ] **Step 4: Create PNG logo**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw

out = Path("plugins/codie-pet/assets/icon.png")
out.parent.mkdir(parents=True, exist_ok=True)
img = Image.new("RGBA", (256, 256), "#10A37F")
draw = ImageDraw.Draw(img)
draw.rounded_rectangle((0, 0, 255, 255), radius=48, fill="#10A37F")
draw.ellipse((78, 42, 178, 142), fill="white")
draw.pieslice((52, 116, 204, 300), 180, 360, fill="white")
draw.ellipse((102, 88, 118, 104), fill="#10A37F")
draw.ellipse((138, 88, 154, 104), fill="#10A37F")
draw.arc((102, 102, 154, 138), 20, 160, fill="#10A37F", width=10)
img.save(out)
PY
```

Expected: `plugins/codie-pet/assets/icon.png` exists and is a valid PNG.

- [ ] **Step 5: Create repo-local marketplace**

Create `.agents/plugins/marketplace.json`:

```json
{
  "name": "codie-pet-local",
  "interface": {
    "displayName": "CodiePet Local"
  },
  "plugins": [
    {
      "name": "codie-pet",
      "source": {
        "source": "local",
        "path": "./plugins/codie-pet"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

- [ ] **Step 6: Validate JSON files**

Run:

```bash
python3 -m json.tool plugins/codie-pet/.codex-plugin/plugin.json >/tmp/codie-pet-plugin-json.out
python3 -m json.tool .agents/plugins/marketplace.json >/tmp/codie-pet-marketplace-json.out
```

Expected: both commands exit 0.

- [ ] **Step 7: Commit**

```bash
git add plugins/codie-pet/.codex-plugin/plugin.json plugins/codie-pet/assets .agents/plugins/marketplace.json
git commit -m "feat: add CodiePet plugin manifest"
```

Expected: commit succeeds in a valid git repository.

---

### Task 3: Skill and Reference Documentation

**Files:**
- Create: `plugins/codie-pet/skills/codie-pet/SKILL.md`
- Create: `plugins/codie-pet/skills/codie-pet/references/workflow.md`
- Create: `plugins/codie-pet/skills/codie-pet/references/prompts.md`
- Create: `plugins/codie-pet/skills/codie-pet/references/quality-checks.md`

- [ ] **Step 1: Create skill directories**

Run:

```bash
mkdir -p plugins/codie-pet/skills/codie-pet/references
```

Expected: directories exist.

- [ ] **Step 2: Create main skill file**

Create `plugins/codie-pet/skills/codie-pet/SKILL.md`:

```markdown
---
name: codie-pet
description: Create, install, regenerate, validate, or remove a Q-style CodiePet GIF pack for a workspace. Use when the user asks to turn one single-person photo into Codex chat state GIFs, install avatar GIF behavior, or remove avatar behavior.
---

# CodiePet

Use this skill to guide a user through creating a local Q-style avatar pack for Codex replies.

## Scope

v0.1 supports one clear single-person human photo. It does not support multi-person photos, pets, objects, scenery, logos, or direct Codex desktop UI modification.

The plugin stores generated assets locally in the current workspace. It does not upload to a cloud service.

## Required workflow

1. Ask for a clear single-person photo if none is attached.
2. Check that the input appears to match the v0.1 scope.
3. Generate one Q-style character preview using `references/prompts.md`.
4. Stop and ask the user to confirm the preview.
5. Only after confirmation, generate six state strips: `idle`, `peek`, `loading`, `coding`, `error`, `done`.
6. Save state strips under `codie-pet/strips/`.
7. Run `python3 plugins/codie-pet/scripts/build_avatar_pack.py --workspace .`.
8. Run `python3 plugins/codie-pet/scripts/validate_avatar_pack.py --workspace .`.
9. Ask the user to review `codie-pet/previews/preview.html` or `codie-pet/previews/contact-sheet.png`.
10. If the user approves installation, run `python3 plugins/codie-pet/scripts/install_avatar_rules.py --workspace .`.

## Confirmation choices

When showing the character preview, ask the user to choose:

1. Use this character.
2. Regenerate with the same style.
3. Regenerate with corrections.

Do not generate state strips before the user chooses to use the character.

## Script locations

All plugin scripts are under `plugins/codie-pet/scripts/`.

## References

- Workflow details: `references/workflow.md`
- Prompt templates: `references/prompts.md`
- Quality checks: `references/quality-checks.md`
```

- [ ] **Step 3: Create workflow reference**

Create `plugins/codie-pet/skills/codie-pet/references/workflow.md`:

````markdown
# CodiePet Workflow

## Workspace output

Generated files live under `codie-pet/` in the user's current workspace:

```text
codie-pet/
  source/
  strips/
  frames/
  gifs/
  previews/
  avatar.config.json
```

## States

- `idle`: general chat, thinking, lightweight answers.
- `peek`: reading files, inspecting context, checking previews.
- `loading`: running commands, waiting, long tasks.
- `coding`: writing code, editing files, generating assets.
- `error`: failed command, failed test, blocked state.
- `done`: successful final result.

## Local commands

Build the pack:

```bash
python3 plugins/codie-pet/scripts/build_avatar_pack.py --workspace .
```

Validate the pack:

```bash
python3 plugins/codie-pet/scripts/validate_avatar_pack.py --workspace .
```

Install workspace rules:

```bash
python3 plugins/codie-pet/scripts/install_avatar_rules.py --workspace .
```

Remove workspace rules:

```bash
python3 plugins/codie-pet/scripts/uninstall_avatar_rules.py --workspace .
```
````

- [ ] **Step 4: Create prompt reference**

Create `plugins/codie-pet/skills/codie-pet/references/prompts.md`:

```markdown
# CodiePet Prompt Templates

## Character preview prompt

Use the uploaded single-person photo as the identity reference. Create one cute Q-style anime desktop-pet character.

Hard requirements:

- One character only.
- Preserve recognizable features from the photo: hair shape, hair color, face impression, clothing style, dominant clothing colors, glasses, hat, earrings, and prominent accessories.
- Q-style anime desktop pet, 2 to 2.5 head-body ratio.
- Large head, small body, clear facial expression.
- Clean dark outline and flat cel-shaded colors.
- Full body visible.
- White or transparent background.
- No labels, no frame numbers, no border, no scenery.
- Do not render a realistic portrait.

Generate a single full-body character preview image.

## State strip prompt template

Use the approved character preview as the identity reference. Generate one horizontal four-frame animation strip for state: `<STATE>`.

Hard requirements:

- Exactly four frames.
- One horizontal row.
- Same character in every frame.
- Same outfit, hairstyle, color palette, proportions, and accessories.
- Enough spacing between frames for slicing.
- White or transparent background.
- No labels, no frame numbers, no grid lines, no borders.
- No extra characters.
- Do not crop hair, head, hands, feet, body, or props.

Animation beat for `<STATE>`:

- `idle`: standing, blinking, slight smile or nod.
- `peek`: peeking from a window edge or screen edge.
- `loading`: holding or hugging a progress bar while waiting.
- `coding`: typing on a tiny keyboard or laptop.
- `error`: holding an ERROR sign or shrugging with a blocked expression.
- `done`: celebrating with confetti or a 100% sign.
```

- [ ] **Step 5: Create quality check reference**

Create `plugins/codie-pet/skills/codie-pet/references/quality-checks.md`:

```markdown
# CodiePet Quality Checks

## Source image checks

Accept the source image only when it appears to contain one clear human subject. Ask for a replacement if the image contains multiple prominent people, a pet, an object, scenery, a heavily blocked face, a very small person, a back view, or an extreme side view.

## Character preview checks

The preview passes when it is one full-body Q-style character, keeps the source person's recognizable traits, has a white or transparent background, and has no labels or scenery.

## State strip checks

A state strip passes when it is one horizontal row, contains exactly four frames, keeps the same character identity across frames, includes no labels or grid lines, and has no cropped body parts or props.

## Final pack checks

The final pack passes when all six GIFs exist, each state has four PNG frames, `avatar.config.json` exists, and at least one preview file exists under `codie-pet/previews/`.
```

- [ ] **Step 6: Verify skill files contain required trigger terms**

Run:

```bash
rg -n "single-person|character preview|idle|peek|loading|coding|error|done|AGENTS.md" plugins/codie-pet/skills/codie-pet
```

Expected: matches appear across `SKILL.md` and reference files.

- [ ] **Step 7: Commit**

```bash
git add plugins/codie-pet/skills/codie-pet
git commit -m "feat: add CodiePet skill workflow"
```

Expected: commit succeeds in a valid git repository.

---

### Task 4: Failing Tests for Avatar Pack Builder

**Files:**
- Create: `tests/test_build_avatar_pack.py`

- [ ] **Step 1: Create tests directory**

Run:

```bash
mkdir -p tests
```

Expected: `tests/` exists.

- [ ] **Step 2: Write failing tests**

Create `tests/test_build_avatar_pack.py`:

```python
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


STATES = ("idle", "peek", "loading", "coding", "error", "done")
SCRIPT = Path("plugins/codie-pet/scripts/build_avatar_pack.py")


def make_strip(path: Path, frame_size: tuple[int, int] = (32, 32), frames: int = 4) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = frame_size[0] * frames
    height = frame_size[1]
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    colors = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6"]
    for index in range(frames):
        left = index * frame_size[0]
        draw.rectangle((left + 4, 4, left + frame_size[0] - 4, frame_size[1] - 4), fill=colors[index % len(colors)])
    image.save(path)


def make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    for state in STATES:
        make_strip(workspace / "codie-pet" / "strips" / f"{state}.png")
    return workspace


def run_builder(workspace: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--workspace", str(workspace)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_builds_gifs_frames_config_and_previews(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)

    result = run_builder(workspace)

    assert result.returncode == 0, result.stderr
    root = workspace / "codie-pet"
    for state in STATES:
        assert (root / "gifs" / f"{state}.gif").is_file()
        frames = sorted((root / "frames" / state).glob("frame-*.png"))
        assert len(frames) == 4
    config = json.loads((root / "avatar.config.json").read_text())
    assert config["version"] == 1
    assert config["style"] == "q-chibi"
    assert config["frameCount"] == 4
    assert set(config["states"]) == set(STATES)
    assert (root / "previews" / "contact-sheet.png").is_file()
    assert (root / "previews" / "preview.html").is_file()


def test_missing_required_strip_fails_with_clear_message(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    (workspace / "codie-pet" / "strips" / "done.png").unlink()

    result = run_builder(workspace)

    assert result.returncode == 2
    assert "Missing required strip: done.png" in result.stderr


def test_non_divisible_strip_width_fails(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    bad = Image.new("RGBA", (130, 32), (255, 255, 255, 0))
    bad.save(workspace / "codie-pet" / "strips" / "idle.png")

    result = run_builder(workspace)

    assert result.returncode == 2
    assert "width must be divisible by 4" in result.stderr
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
python3 -m pytest tests/test_build_avatar_pack.py -q
```

Expected: tests fail because `plugins/codie-pet/scripts/build_avatar_pack.py` does not exist.

- [ ] **Step 4: Commit failing tests**

```bash
git add tests/test_build_avatar_pack.py
git commit -m "test: cover avatar pack builder behavior"
```

Expected: commit succeeds in a valid git repository.

---

### Task 5: Implement Avatar Pack Builder

**Files:**
- Create: `plugins/codie-pet/scripts/build_avatar_pack.py`

- [ ] **Step 1: Create scripts directory**

Run:

```bash
mkdir -p plugins/codie-pet/scripts
```

Expected: scripts directory exists.

- [ ] **Step 2: Implement builder script**

Create `plugins/codie-pet/scripts/build_avatar_pack.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit("Pillow is required. Install it with `python3 -m pip install Pillow`.") from exc


STATES = ("idle", "peek", "loading", "coding", "error", "done")
STATE_META = {
    "idle": ("Idle", "General chat, thinking, lightweight answers"),
    "peek": ("Peek", "Reading files, inspecting context, checking previews"),
    "loading": ("Loading", "Running commands, waiting, long tasks"),
    "coding": ("Coding", "Writing code, editing files, generating assets"),
    "error": ("Error", "Failed commands, failed tests, blocked work"),
    "done": ("Done", "Successful final results"),
}


@dataclass(frozen=True)
class Paths:
    workspace: Path
    root: Path
    strips: Path
    frames: Path
    gifs: Path
    previews: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build CodiePet GIF pack from six four-frame strips.")
    parser.add_argument("--workspace", default=".", help="Workspace root. Default: current directory.")
    parser.add_argument("--frame-duration", type=int, default=180, help="GIF frame duration in milliseconds.")
    return parser.parse_args()


def resolve_paths(workspace: str) -> Paths:
    root_workspace = Path(workspace).resolve()
    root = root_workspace / "codie-pet"
    return Paths(
        workspace=root_workspace,
        root=root,
        strips=root / "strips",
        frames=root / "frames",
        gifs=root / "gifs",
        previews=root / "previews",
    )


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def require_strips(paths: Paths) -> None:
    for state in STATES:
        strip = paths.strips / f"{state}.png"
        if not strip.is_file():
            fail(f"Missing required strip: {state}.png")


def slice_strip(strip_path: Path, out_dir: Path) -> list[Path]:
    try:
        image = Image.open(strip_path).convert("RGBA")
    except Exception as exc:
        fail(f"Cannot open strip {strip_path.name}: {exc}")

    if image.width % 4 != 0:
        fail(f"Invalid strip {strip_path.name}: width must be divisible by 4")
    if image.height < 1 or image.width < 4:
        fail(f"Invalid strip {strip_path.name}: image is too small")

    frame_width = image.width // 4
    out_dir.mkdir(parents=True, exist_ok=True)
    frame_paths: list[Path] = []
    for index in range(4):
        left = index * frame_width
        frame = image.crop((left, 0, left + frame_width, image.height))
        frame_path = out_dir / f"frame-{index + 1:02d}.png"
        frame.save(frame_path)
        frame_paths.append(frame_path)
    return frame_paths


def build_gif(frame_paths: list[Path], gif_path: Path, duration: int) -> None:
    images = [Image.open(path).convert("RGBA") for path in frame_paths]
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
        disposal=2,
    )


def write_config(paths: Paths) -> None:
    states = {}
    for state in STATES:
        label, use_when = STATE_META[state]
        states[state] = {
            "label": label,
            "gif": f"./gifs/{state}.gif",
            "useWhen": use_when,
        }
    config = {
        "version": 1,
        "style": "q-chibi",
        "frameCount": 4,
        "states": states,
    }
    (paths.root / "avatar.config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def render_contact_sheet(paths: Paths) -> None:
    gif_cells = []
    for state in STATES:
        frame = Image.open(paths.frames / state / "frame-01.png").convert("RGBA")
        gif_cells.append((state, frame))

    cell_w = max(image.width for _, image in gif_cells)
    cell_h = max(image.height for _, image in gif_cells)
    label_h = 22
    gap = 12
    columns = 3
    rows = 2
    width = columns * cell_w + (columns + 1) * gap
    height = rows * (cell_h + label_h) + (rows + 1) * gap
    sheet = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(sheet)

    for index, (state, image) in enumerate(gif_cells):
        row = index // columns
        col = index % columns
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + label_h + gap)
        draw.text((x, y), state, fill="black")
        sheet.alpha_composite(image, (x + (cell_w - image.width) // 2, y + label_h))

    paths.previews.mkdir(parents=True, exist_ok=True)
    sheet.save(paths.previews / "contact-sheet.png")


def write_preview_html(paths: Paths) -> None:
    cards = "\n".join(
        f'      <section><h2>{state}</h2><img src="../gifs/{state}.gif" alt="{state} avatar GIF"></section>'
        for state in STATES
    )
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CodiePet Preview</title>
    <style>
      body {{ font-family: system-ui, sans-serif; margin: 24px; background: #f7f7f7; color: #111; }}
      main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; }}
      section {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 16px; text-align: center; }}
      h1 {{ font-size: 22px; }}
      h2 {{ font-size: 14px; margin: 0 0 12px; }}
      img {{ max-width: 100%; image-rendering: auto; }}
    </style>
  </head>
  <body>
    <h1>CodiePet Preview</h1>
    <main>
{cards}
    </main>
  </body>
</html>
"""
    paths.previews.mkdir(parents=True, exist_ok=True)
    (paths.previews / "preview.html").write_text(html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    paths = resolve_paths(args.workspace)
    require_strips(paths)
    for directory in (paths.frames, paths.gifs, paths.previews):
        directory.mkdir(parents=True, exist_ok=True)

    for state in STATES:
        frame_paths = slice_strip(paths.strips / f"{state}.png", paths.frames / state)
        build_gif(frame_paths, paths.gifs / f"{state}.gif", args.frame_duration)

    write_config(paths)
    render_contact_sheet(paths)
    write_preview_html(paths)
    print(f"Built CodiePet pack at {paths.root}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run builder tests**

Run:

```bash
python3 -m pytest tests/test_build_avatar_pack.py -q
```

Expected: all tests in `test_build_avatar_pack.py` pass.

- [ ] **Step 4: Commit**

```bash
git add plugins/codie-pet/scripts/build_avatar_pack.py tests/test_build_avatar_pack.py
git commit -m "feat: build avatar gif packs from state strips"
```

Expected: commit succeeds in a valid git repository.

---

### Task 6: Failing Tests for AGENTS.md Rule Management

**Files:**
- Create: `tests/test_avatar_rules.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_avatar_rules.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m pytest tests/test_avatar_rules.py -q
```

Expected: tests fail because install and uninstall scripts do not exist.

- [ ] **Step 3: Commit failing tests**

```bash
git add tests/test_avatar_rules.py
git commit -m "test: cover avatar rule installation"
```

Expected: commit succeeds in a valid git repository.

---

### Task 7: Implement AGENTS.md Install and Uninstall Scripts

**Files:**
- Create: `plugins/codie-pet/scripts/install_avatar_rules.py`
- Create: `plugins/codie-pet/scripts/uninstall_avatar_rules.py`

- [ ] **Step 1: Implement install script**

Create `plugins/codie-pet/scripts/install_avatar_rules.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


START = "<!-- codie-pet:start -->"
END = "<!-- codie-pet:end -->"
BLOCK = f"""{START}
## CodiePet GIF Response Style

Use local avatar GIFs from `./codie-pet/gifs/` when replying in this workspace.

- Use `idle.gif` for general chat, thinking, and lightweight answers.
- Use `peek.gif` when reading files, inspecting context, or checking previews.
- Use `loading.gif` when running commands, waiting, processing, or doing long tasks.
- Use `coding.gif` when writing code, editing files, generating assets, or implementing changes.
- Use `error.gif` when a command fails, tests fail, or work is blocked.
- Use `done.gif` for successful final responses and clean completion.

Placement rules:
- Put the selected GIF near the beginning of short replies.
- During long-running work, include the current-state GIF in progress updates when useful.
- Do not explain the GIF system every time; use it naturally.

Selection rules:
- Choose the GIF from the current task stage.
- If several states apply, choose the most active current state.
- If the user asks to remove, reduce, or change avatar behavior, follow the user.
- User, system, and developer instructions take priority over these avatar rules.
{END}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install CodiePet workspace AGENTS.md rules.")
    parser.add_argument("--workspace", default=".", help="Workspace root. Default: current directory.")
    return parser.parse_args()


def replace_block(content: str) -> str:
    pattern = re.compile(rf"{re.escape(START)}.*?{re.escape(END)}\n?", re.DOTALL)
    if pattern.search(content):
        return pattern.sub(BLOCK + "\n", content).rstrip() + "\n"
    if content.strip():
        return content.rstrip() + "\n\n" + BLOCK
    return BLOCK


def main() -> None:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    agents = workspace / "AGENTS.md"
    content = agents.read_text(encoding="utf-8") if agents.exists() else ""
    agents.write_text(replace_block(content), encoding="utf-8")
    print(f"Installed CodiePet rules in {agents}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Implement uninstall script**

Create `plugins/codie-pet/scripts/uninstall_avatar_rules.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


START = "<!-- codie-pet:start -->"
END = "<!-- codie-pet:end -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove CodiePet workspace AGENTS.md rules.")
    parser.add_argument("--workspace", default=".", help="Workspace root. Default: current directory.")
    return parser.parse_args()


def remove_block(content: str) -> str:
    pattern = re.compile(rf"\n?{re.escape(START)}.*?{re.escape(END)}\n?", re.DOTALL)
    cleaned = pattern.sub("\n", content)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned + "\n" if cleaned else ""


def main() -> None:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    agents = workspace / "AGENTS.md"
    if not agents.exists():
        print(f"No AGENTS.md found at {agents}")
        return
    agents.write_text(remove_block(agents.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"Removed CodiePet rules from {agents}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run rule tests**

Run:

```bash
python3 -m pytest tests/test_avatar_rules.py -q
```

Expected: all tests in `test_avatar_rules.py` pass.

- [ ] **Step 4: Commit**

```bash
git add plugins/codie-pet/scripts/install_avatar_rules.py plugins/codie-pet/scripts/uninstall_avatar_rules.py tests/test_avatar_rules.py
git commit -m "feat: manage CodiePet workspace rules"
```

Expected: commit succeeds in a valid git repository.

---

### Task 8: Failing Tests for Avatar Pack Validator

**Files:**
- Create: `tests/test_validate_avatar_pack.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_validate_avatar_pack.py`:

```python
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
    assert "Avatar pack validation passed" in result.stdout


def test_validator_reports_missing_gif(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    built = run_builder(workspace)
    assert built.returncode == 0, built.stderr
    (workspace / "codie-pet" / "gifs" / "done.gif").unlink()

    result = run_validator(workspace)

    assert result.returncode == 2
    assert "Missing GIF: done.gif" in result.stderr
```

- [ ] **Step 2: Run tests to verify validator tests fail**

Run:

```bash
python3 -m pytest tests/test_validate_avatar_pack.py -q
```

Expected: tests fail because `validate_avatar_pack.py` does not exist.

- [ ] **Step 3: Commit failing tests**

```bash
git add tests/test_validate_avatar_pack.py
git commit -m "test: cover avatar pack validation"
```

Expected: commit succeeds in a valid git repository.

---

### Task 9: Implement Avatar Pack Validator

**Files:**
- Create: `plugins/codie-pet/scripts/validate_avatar_pack.py`

- [ ] **Step 1: Implement validator script**

Create `plugins/codie-pet/scripts/validate_avatar_pack.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


STATES = ("idle", "peek", "loading", "coding", "error", "done")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a generated CodiePet pack.")
    parser.add_argument("--workspace", default=".", help="Workspace root. Default: current directory.")
    return parser.parse_args()


def error(message: str) -> None:
    print(message, file=sys.stderr)


def validate(workspace: Path) -> list[str]:
    failures: list[str] = []
    root = workspace / "codie-pet"
    for directory in ("frames", "gifs", "previews"):
        if not (root / directory).is_dir():
            failures.append(f"Missing directory: {directory}")

    for state in STATES:
        gif = root / "gifs" / f"{state}.gif"
        if not gif.is_file():
            failures.append(f"Missing GIF: {state}.gif")
        frame_dir = root / "frames" / state
        frames = sorted(frame_dir.glob("frame-*.png")) if frame_dir.is_dir() else []
        if len(frames) != 4:
            failures.append(f"Expected 4 frames for {state}, found {len(frames)}")

    config_path = root / "avatar.config.json"
    if not config_path.is_file():
        failures.append("Missing avatar.config.json")
    else:
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Invalid avatar.config.json: {exc}")
        else:
            if config.get("version") != 1:
                failures.append("avatar.config.json version must be 1")
            if set(config.get("states", {})) != set(STATES):
                failures.append("avatar.config.json states do not match required states")

    if not (root / "previews" / "preview.html").is_file():
        failures.append("Missing preview.html")
    if not (root / "previews" / "contact-sheet.png").is_file():
        failures.append("Missing contact-sheet.png")

    return failures


def main() -> None:
    args = parse_args()
    failures = validate(Path(args.workspace).resolve())
    if failures:
        for failure in failures:
            error(failure)
        raise SystemExit(2)
    print("Avatar pack validation passed")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run validator tests**

Run:

```bash
python3 -m pytest tests/test_validate_avatar_pack.py -q
```

Expected: all tests in `test_validate_avatar_pack.py` pass.

- [ ] **Step 3: Run all script tests**

Run:

```bash
python3 -m pytest tests -q
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add plugins/codie-pet/scripts/validate_avatar_pack.py tests/test_validate_avatar_pack.py
git commit -m "feat: validate CodiePet packs"
```

Expected: commit succeeds in a valid git repository.

---

### Task 10: README and User-Facing Installation Docs

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README**

Create `README.md`:

````markdown
# CodiePet

CodiePet is a local Codex plugin that helps turn one clear single-person photo into a Q-style animated avatar pack for Codex workspace replies.

## What v0.1 does

- Guides Codex through creating a Q-style character preview.
- Requires the user to approve the preview before generating state GIFs.
- Builds six local state GIFs: `idle`, `peek`, `loading`, `coding`, `error`, `done`.
- Installs workspace-local `AGENTS.md` rules so Codex can use the GIFs naturally in replies.

## What v0.1 does not do

- It does not upload images to a cloud service.
- It does not modify the Codex desktop app UI.
- It does not create a floating desktop pet overlay.
- It does not support multi-person photos, pets, objects, scenery, or custom visual styles.

## Install for local testing

From this repository:

```bash
codex plugin marketplace add .
```

Then restart Codex desktop app.

## Use in Codex desktop app

Open a workspace and ask:

```text
Create my CodiePet from this photo.
```

Attach one clear single-person photo. The plugin workflow asks you to approve the Q-style character preview before generating GIFs.

## Generated workspace files

Generated assets are written under:

```text
codie-pet/
  strips/
  frames/
  gifs/
  previews/
  avatar.config.json
```

The installer updates only the managed CodiePet block in `AGENTS.md`.

## Remove avatar behavior

Ask Codex:

```text
Remove CodiePet from this workspace.
```

Or run:

```bash
python3 plugins/codie-pet/scripts/uninstall_avatar_rules.py --workspace .
```

## Privacy

v0.1 stores source and generated files locally in the current workspace. It does not add a cloud upload step. Only use photos you have the right to use.

## Development

Install test dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run tests:

```bash
python3 -m pytest tests -q
```
````

- [ ] **Step 2: Verify README mentions desktop usage and privacy**

Run:

```bash
rg -n "desktop app|Privacy|single-person|AGENTS.md|pytest" README.md
```

Expected: all required topics are found.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add CodiePet usage guide"
```

Expected: commit succeeds in a valid git repository.

---

### Task 11: End-to-End Local Fixture Verification

**Files:**
- No new files required.

- [ ] **Step 1: Create synthetic fixture workspace**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw

states = ("idle", "peek", "loading", "coding", "error", "done")
root = Path("/tmp/codie-pet-e2e/codie-pet/strips")
root.mkdir(parents=True, exist_ok=True)
for s_index, state in enumerate(states):
    image = Image.new("RGBA", (256, 64), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    for index in range(4):
        left = index * 64
        draw.ellipse((left + 14, 12, left + 50, 48), fill=(40 + s_index * 25, 120, 200, 255))
        draw.text((left + 4, 48), str(index + 1), fill="black")
    image.save(root / f"{state}.png")
PY
```

Expected: six strip files exist under `/tmp/codie-pet-e2e/codie-pet/strips/`.

- [ ] **Step 2: Build fixture pack**

Run:

```bash
python3 plugins/codie-pet/scripts/build_avatar_pack.py --workspace /tmp/codie-pet-e2e
```

Expected: prints `Built CodiePet pack at /tmp/codie-pet-e2e/codie-pet`.

- [ ] **Step 3: Validate fixture pack**

Run:

```bash
python3 plugins/codie-pet/scripts/validate_avatar_pack.py --workspace /tmp/codie-pet-e2e
```

Expected: prints `Avatar pack validation passed`.

- [ ] **Step 4: Install rules into fixture workspace**

Run:

```bash
python3 plugins/codie-pet/scripts/install_avatar_rules.py --workspace /tmp/codie-pet-e2e
```

Expected: prints `Installed CodiePet rules` and `/tmp/codie-pet-e2e/AGENTS.md` contains the managed block.

- [ ] **Step 5: Uninstall rules from fixture workspace**

Run:

```bash
python3 plugins/codie-pet/scripts/uninstall_avatar_rules.py --workspace /tmp/codie-pet-e2e
```

Expected: prints `Removed CodiePet rules` and the managed block is absent from `/tmp/codie-pet-e2e/AGENTS.md`.

- [ ] **Step 6: Run all tests again**

Run:

```bash
python3 -m pytest tests -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit final verification updates**

Run only if previous tasks changed files after their commits:

```bash
git status --short
git add .
git commit -m "chore: verify CodiePet plugin workflow"
```

Expected: commit succeeds when there are changes; skip commit if `git status --short` is empty.

---

### Task 12: Final Manual Review

**Files:**
- Modify if review finds a concrete mismatch: `README.md`, skill references, or scripts.

- [ ] **Step 1: Check spec coverage**

Run:

```bash
rg -n "idle|peek|loading|coding|error|done|character preview|single-person|AGENTS.md|cloud" plugins/codie-pet README.md tests
```

Expected: the implementation mentions the six states, character preview workflow, input scope, local workspace rules, and no-cloud boundary.

- [ ] **Step 2: Validate JSON**

Run:

```bash
python3 -m json.tool plugins/codie-pet/.codex-plugin/plugin.json >/tmp/codie-pet-plugin-json.out
python3 -m json.tool .agents/plugins/marketplace.json >/tmp/codie-pet-marketplace-json.out
```

Expected: both commands exit 0.

- [ ] **Step 3: Validate tests**

Run:

```bash
python3 -m pytest tests -q
```

Expected: all tests pass.

- [ ] **Step 4: Inspect final changed files**

Run:

```bash
find plugins/codie-pet tests docs -maxdepth 5 -type f | sort
```

Expected: the file list includes plugin manifest, skill files, scripts, tests, spec, and plan.

- [ ] **Step 5: Prepare user summary**

Summarize:

- Plugin files created.
- Script behavior implemented.
- Test commands run.
- Any missing environment capability, such as inability to run image generation locally.
- Desktop app usage path from README.
