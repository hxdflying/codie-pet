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
