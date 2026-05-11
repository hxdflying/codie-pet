---
name: codex-avatar
description: Create, install, regenerate, validate, or remove a Q-style Codex avatar GIF pack for a workspace. Use when the user asks to turn one single-person photo into Codex chat state GIFs, install avatar GIF behavior, or remove avatar behavior.
---

# Codex Avatar

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
6. Save state strips under `codex-avatar/strips/`.
7. Run `python3 plugins/codex-avatar/scripts/build_avatar_pack.py --workspace .`.
8. Run `python3 plugins/codex-avatar/scripts/validate_avatar_pack.py --workspace .`.
9. Ask the user to review `codex-avatar/previews/preview.html` or `codex-avatar/previews/contact-sheet.png`.
10. If the user approves installation, run `python3 plugins/codex-avatar/scripts/install_avatar_rules.py --workspace .`.

## Confirmation choices

When showing the character preview, ask the user to choose:

1. Use this character.
2. Regenerate with the same style.
3. Regenerate with corrections.

Do not generate state strips before the user chooses to use the character.

## Script locations

All plugin scripts are under `plugins/codex-avatar/scripts/`.

## References

- Workflow details: `references/workflow.md`
- Prompt templates: `references/prompts.md`
- Quality checks: `references/quality-checks.md`
