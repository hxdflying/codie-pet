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
