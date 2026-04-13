#!/usr/bin/env python3
"""Create a starter memory vault from the bundled template."""

from __future__ import annotations

import argparse
import shutil
from datetime import date
from pathlib import Path


TEXT_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", help="Directory where the vault should be created")
    parser.add_argument("--agent-name", default="Codex", help="Primary agent name")
    parser.add_argument("--vault-name", help="Vault display name; defaults to directory name")
    parser.add_argument("--force", action="store_true", help="Allow bootstrap into an existing empty directory")
    return parser.parse_args()


def replace_tokens(path: Path, replacements: dict[str, str]) -> None:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return
    text = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(key, value)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()

    script_dir = Path(__file__).resolve().parent
    template_dir = script_dir.parent / "assets" / "memory-template"
    destination = Path(args.destination).expanduser().resolve()
    vault_name = args.vault_name or destination.name

    if destination.exists():
        if any(destination.iterdir()):
            raise SystemExit(f"Destination is not empty: {destination}")
        if not args.force:
            raise SystemExit(
                "Destination already exists. Use a new directory or pass --force if it is empty."
            )
    else:
        destination.mkdir(parents=True)

    for source in sorted(template_dir.rglob("*")):
        relative = source.relative_to(template_dir)
        target = destination / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        shutil.copy2(source, target)

    replacements = {
        "{{VAULT_NAME}}": vault_name,
        "{{AGENT_NAME}}": args.agent_name,
        "{{TODAY}}": date.today().isoformat(),
    }

    for path in destination.rglob("*"):
        if path.is_file():
            replace_tokens(path, replacements)

    print(f"Created memory vault: {destination}")
    print("Next steps:")
    print(f"  python {script_dir / 'rebuild_index.py'} {destination}")
    print(f"  python {script_dir / 'lint_memory.py'} {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
