# CodiePet Workflow

## Workspace output

Generated files live under `codie-pet/` in the user's current workspace:

```text
codie-pet/
  source/
    original.png            # the photo the user attached
    character-preview.png   # the Q-style preview the user approved
  strips/
  frames/
  gifs/
  previews/
  avatar.config.json
```

`source/character-preview.png` is the identity reference for every state strip prompt. The skill must save it only after the user explicitly approves the preview.

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
