# CodiePet

Turn one clear single-person photo into a Q-style animated avatar pack for Codex workspace replies.

<p align="center">
  <img src="image/coding.gif" alt="CodiePet coding state" width="220">
  <img src="image/done.gif" alt="CodiePet done state" width="220">
</p>

<p align="center">
  <strong>A tiny local companion for long Codex tasks.</strong><br>
  CodiePet generates six workspace-local GIF states, then installs rules so Codex can use them naturally while it works.
</p>

## What It Does

- Creates a Q-style character preview from one clear single-person photo.
- Waits for your approval before generating the full state pack.
- Builds six local animated GIFs: `idle`, `peek`, `loading`, `coding`, `error`, and `done`.
- Installs a managed `AGENTS.md` block so Codex knows when to use each state.
- Keeps generated assets inside the current workspace under `codie-pet/`.

## State Pack

| Idle | Peek | Loading |
| --- | --- | --- |
| <img src="image/idle.gif" alt="Idle CodiePet GIF" width="180"> | <img src="image/peek.gif" alt="Peek CodiePet GIF" width="180"> | <img src="image/loading.gif" alt="Loading CodiePet GIF" width="180"> |
| General chat, thinking, lightweight answers. | Reading files, inspecting context, checking previews. | Running commands, waiting, long tasks. |

| Coding | Error | Done |
| --- | --- | --- |
| <img src="image/coding.gif" alt="Coding CodiePet GIF" width="180"> | <img src="image/error.gif" alt="Error CodiePet GIF" width="180"> | <img src="image/done.gif" alt="Done CodiePet GIF" width="180"> |
| Writing code, editing files, generating assets. | Failed commands, failed tests, blocked work. | Successful final results. |

Each state is generated as a four-frame GIF. The current v0.1 pack contains 6 states and 24 total animation frames.

## Install

### From Codex App

Ask Codex App to install this plugin from GitHub:

```text
Install https://github.com/hxdflying/codie-pet.git
```

Then restart Codex App if the plugin list does not refresh automatically. Enable **CodiePet** from plugin settings if needed.

### From Codex CLI

```bash
codex plugin marketplace add hxdflying/codie-pet
```

For local testing from this repository:

```bash
codex plugin marketplace add .
```

CodiePet has no third-party runtime Python package dependency.

## Use

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

The plugin scripts do not add an additional upload step. Image generation is performed by Codex's own image-generation capability, which may use a cloud-hosted model controlled by the Codex provider. Only use photos you have the right to use.

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
