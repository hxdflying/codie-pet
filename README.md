# CodiePet

English | [简体中文](docs/zh-CN/README.md)

<p align="center">
  <img alt="states: 6" src="https://img.shields.io/badge/states-6-10A37F">
  <img alt="frames: 24" src="https://img.shields.io/badge/frames-24-0EA5E9">
  <img alt="languages: en | zh-CN" src="https://img.shields.io/badge/languages-en%20%7C%20zh--CN-64748B">
  <img alt="runtime: no dependencies" src="https://img.shields.io/badge/runtime-no%20deps-F59E0B">
  <img alt="license: MIT" src="https://img.shields.io/badge/license-MIT-111827">
</p>

<p align="center">
  <img src="image/logo.png" alt="CodiePet cover" width="450">
</p>

CodiePet is a local Codex plugin that turns one clear single-person photo into a Q-style animated avatar pack for Codex workspace replies.

Each generated pack is small, local, and workspace-scoped:

```text
codie-pet/
  source/      original photo and approved character preview
  strips/      generated four-frame state strips
  frames/      sliced PNG frames
  gifs/        final Codex state GIFs
  previews/    preview.html and contact-sheet.png
```

## Quick Install

1. Install from Codex App by asking:

   ```text
   Install https://github.com/hxdflying/codie-pet.git
   ```

   Then restart Codex App if the plugin list does not refresh automatically. Enable **CodiePet** from plugin settings if needed.

2. Optional CLI install:

   ```bash
   codex plugin marketplace add hxdflying/codie-pet
   ```

3. Optional local development install:

   ```bash
   codex plugin marketplace add .
   ```

CodiePet has no third-party runtime Python package dependency.

## State Pack

| Action | Preview | Used When |
| --- | --- | --- |
| `idle` | <img src="image/idle.gif" alt="Idle CodiePet GIF" width="96"> | General chat, thinking, lightweight answers. |
| `peek` | <img src="image/peek.gif" alt="Peek CodiePet GIF" width="96"> | Reading files, inspecting context, checking previews. |
| `loading` | <img src="image/loading.gif" alt="Loading CodiePet GIF" width="96"> | Running commands, waiting, long tasks. |
| `coding` | <img src="image/coding.gif" alt="Coding CodiePet GIF" width="96"> | Writing code, editing files, generating assets. |
| `error` | <img src="image/error.gif" alt="Error CodiePet GIF" width="96"> | Failed commands, failed tests, blocked work. |
| `done` | <img src="image/done.gif" alt="Done CodiePet GIF" width="96"> | Successful final results. |

Each state is a four-frame GIF. The v0.1 pack contains 6 states and 24 total animation frames.

## Make Your CodiePet

Open a workspace in Codex App and ask:

```text
Create my CodiePet from this photo.
```

Attach one clear single-person photo. CodiePet will:

1. Save the source photo locally.
2. Generate one Q-style character preview.
3. Ask you to approve the preview.
4. Generate the six GIF states after approval.
5. Validate the pack and offer to install workspace rules.

## Generated Files

Generated assets are written inside the current workspace:

```text
codie-pet/
  source/
    original.png
    character-preview.png
  strips/
    idle.png
    peek.png
    loading.png
    coding.png
    error.png
    done.png
  frames/
  gifs/
    idle.gif
    peek.gif
    loading.gif
    coding.gif
    error.gif
    done.gif
  previews/
    contact-sheet.png
    preview.html
  avatar.config.json
```

The installer updates only the managed CodiePet block in `AGENTS.md`.

## Scope

CodiePet v0.1 is intentionally narrow:

- It supports one clear single-person human photo.
- It does not support multi-person photos, pets, objects, scenery, logos, or custom visual styles.
- It does not modify the Codex desktop app UI.
- It does not create a floating desktop pet overlay.

## Remove

Ask Codex:

```text
Remove CodiePet from this workspace.
```

Or run the installed uninstall script:

```bash
python3 /path/to/installed/codie-pet/scripts/uninstall_avatar_rules.py --workspace .
```

## Privacy

CodiePet stores the source photo, approved character preview, state strips, frames, and GIFs locally inside the current workspace under `codie-pet/`.

The plugin scripts do not add an additional upload step. Image generation is performed by Codex's own image-generation capability, which may use a cloud-hosted GPT Image model or another model selected by the Codex provider. CodiePet does not choose or force a specific image model. Only use photos you have the right to use.

See [privacy](docs/privacy.md) and [terms](docs/terms.md) for plugin metadata policy links.

## Development

Install test dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run tests:

```bash
python3 -m pytest tests -q
```

Validate marketplace metadata:

```bash
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool plugins/codie-pet/.codex-plugin/plugin.json
```

## License

Code is licensed under [MIT](LICENSE).
