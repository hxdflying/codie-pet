---
name: codie-pet
description: Create, install, regenerate, validate, or remove a Q-style CodiePet GIF pack for a workspace. Use when the user asks to turn one single-person photo into Codex chat state GIFs, install avatar GIF behavior, or remove avatar behavior.
---

# CodiePet

Use this skill to guide a user through creating a local Q-style avatar pack for Codex replies.

## Scope

v0.1 supports one clear single-person human photo. It does not support multi-person photos, pets, objects, scenery, logos, or direct Codex desktop UI modification.

The plugin stores generated assets locally in the current workspace. The plugin scripts do not add an extra upload step, but Codex image generation may still use a cloud-hosted model.

## Required workflow

1. Ask for a clear single-person photo if none is attached.
2. Check that the input appears to match the v0.1 scope.
3. Save the source photo as `codie-pet/source/original.png` so later regeneration can re-use it.
4. Generate one Q-style character preview using `references/prompts.md`.
5. Stop and ask the user to confirm the preview.
6. After the user approves the preview, save it as `codie-pet/source/character-preview.png`. Use this saved file as the identity reference for every state strip prompt.
7. Generate six state strips: `idle`, `peek`, `loading`, `coding`, `error`, `done`.
8. Save state strips under `codie-pet/strips/`.
9. Run `python3 plugins/codie-pet/scripts/build_avatar_pack.py --workspace .`.
10. Run `python3 plugins/codie-pet/scripts/validate_avatar_pack.py --workspace .`.
11. Ask the user to review `codie-pet/previews/preview.html` or `codie-pet/previews/contact-sheet.png`.
12. If the user approves installation, run `python3 plugins/codie-pet/scripts/install_avatar_rules.py --workspace .`.

## Confirmation choices

When showing the character preview, ask the user to choose:

1. Use this character.
2. Regenerate with the same style.
3. Regenerate with corrections.

Do not generate state strips before the user chooses to use the character. Do not save `codie-pet/source/character-preview.png` until the user has chosen option 1.

## Script locations

All plugin scripts are under `plugins/codie-pet/scripts/`.

## Recovery

When a step in the required workflow fails, do not restart the full workflow. Narrow the regeneration to the smallest affected unit.

- **No image attached.** Ask the user to attach one clear single-person photo. Do not invent one.
- **Source image rejected by v0.1 scope checks** (multi-person, pet, object, scenery, back view, heavily blocked face). Explain the v0.1 limits from `references/quality-checks.md` and ask for a replacement photo. Do not proceed.
- **Character preview rejected by the user.** Offer "Regenerate with same style" or "Regenerate with corrections". Apply the corrections directly to the prompt in `references/prompts.md` and regenerate. Never save `codie-pet/source/character-preview.png` until the user picks option 1.
- **A single state strip has a defect** (wrong identity, missing frame, body cropped, label or grid line bleeding in). Regenerate only that one state. Replace just `codie-pet/strips/<state>.png` and re-run `build_avatar_pack.py`.
- **`build_avatar_pack.py` reports `Missing required strip`.** Generate the named state and save it under `codie-pet/strips/`. Re-run.
- **`build_avatar_pack.py` warns `width is not divisible by 4, trimming to ...`.** This is informational; the builder already trimmed 1-3 stray pixels. Inspect the contact sheet to confirm framing is intact. Regenerate that state only if the trim cropped the character.
- **`build_avatar_pack.py` reports `image is too small` or `Cannot open strip`.** The strip file is corrupted or below 4 px wide. Regenerate that state only.
- **`build_avatar_pack.py` reports `Pillow is required`.** Stop. Ask the user to run `python3 -m pip install Pillow` and retry. Do not attempt to install dependencies silently.
- **`validate_avatar_pack.py` warns about `source/character-preview.png`.** Save the approved preview to that path, then re-run validation. Do not skip the warning.
- **`validate_avatar_pack.py` reports a `Missing GIF` or wrong frame count.** Re-run `build_avatar_pack.py` after fixing the offending strip; do not edit files under `frames/` or `gifs/` by hand.
- **`install_avatar_rules.py` cannot write `AGENTS.md`** (permission error). Stop. Tell the user the workspace `AGENTS.md` is not writable and ask them to check file permissions. Do not retry with elevated privileges.
- **User cancels installation.** Leave the generated assets in place. Do not run the installer. Do not delete `codie-pet/`.

In all cases, stop after a failure rather than chaining new generation attempts. Tell the user exactly which step failed and what the next manual action is.

## References

- Workflow details: `references/workflow.md`
- Prompt templates: `references/prompts.md`
- Quality checks: `references/quality-checks.md`
