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
