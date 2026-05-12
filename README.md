# CodiePet

CodiePet is a local Codex plugin that helps turn one clear single-person photo into a Q-style animated avatar pack for Codex workspace replies.

## What v0.1 does

- Guides Codex through creating a Q-style character preview.
- Requires the user to approve the preview before generating state GIFs.
- Builds six local state GIFs: `idle`, `peek`, `loading`, `coding`, `error`, `done`.
- Installs workspace-local `AGENTS.md` rules so Codex can use the GIFs naturally in replies.

## What v0.1 does not do

- The plugin scripts do not add an extra upload step. Codex image generation may still use a cloud-hosted model.
- It does not modify the Codex desktop app UI.
- It does not create a floating desktop pet overlay.
- It does not support multi-person photos, pets, objects, scenery, or custom visual styles.

## Install from GitHub

```bash
codex plugin marketplace add hxdflying/codie-pet
```

For a pinned release:

```bash
codex plugin marketplace add hxdflying/codie-pet@v0.1.0
```

Then restart Codex desktop app. If CodiePet is not enabled automatically, open the plugin marketplace or plugin settings in the desktop app and install or enable **CodiePet**.

CodiePet has no third-party runtime Python package dependency.

## Install for local testing

From this repository:

```bash
codex plugin marketplace add .
```

Then restart Codex desktop app. If CodiePet is not enabled automatically, open the plugin marketplace or plugin settings in the desktop app and install or enable **CodiePet** from the **CodiePet** marketplace.

Marketplace metadata assumptions are documented in `docs/marketplace.md`.

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
  source/
    original.png
    character-preview.png
  strips/
  frames/
  gifs/
  previews/
  avatar.config.json
```

The installer updates only the managed CodiePet block in `AGENTS.md`.

## Remove CodiePet behavior

Ask Codex:

```text
Remove CodiePet from this workspace.
```

Or run:

```bash
python3 /path/to/installed/codie-pet/scripts/uninstall_avatar_rules.py --workspace .
```

## Privacy

CodiePet stores the source photo, the approved character preview, the state strips, and all generated GIFs locally inside the current workspace under `codie-pet/`. The plugin scripts do not add an additional cloud upload step.

Image generation is performed by Codex's own image-generation capability. That step may send your photo to a cloud-hosted model owned by the Codex provider, subject to that provider's data-handling policy. CodiePet has no control over that path.

Only use photos you have the right to use.

See `docs/privacy.md` and `docs/terms.md` for the plugin metadata policy links.

## Development

Install test dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run tests:

```bash
python3 -m pytest tests -q
```
