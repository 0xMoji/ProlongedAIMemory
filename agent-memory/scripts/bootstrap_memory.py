#!/usr/bin/env python3
"""Create a starter memory vault from the bundled template."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import shutil
import subprocess
import sys
import textwrap
from datetime import date
from pathlib import Path


TEXT_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", help="Directory where the vault should be created")
    parser.add_argument("--agent-name", default="Codex", help="Primary agent name")
    parser.add_argument("--vault-name", help="Vault display name; defaults to directory name")
    parser.add_argument("--force", action="store_true", help="Allow bootstrap into an existing empty directory")
    parser.add_argument(
        "--enable-palace",
        action="store_true",
        help="Install MemPalace and initialize a local recall layer in palace/",
    )
    return parser.parse_args()


def replace_tokens(path: Path, replacements: dict[str, str]) -> None:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return
    text = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(key, value)
    path.write_text(text, encoding="utf-8")


def ensure_mempalace_installed() -> None:
    if importlib.util.find_spec("mempalace") is not None:
        return

    print("Installing mempalace...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mempalace"], check=True)
    importlib.invalidate_caches()

    if importlib.util.find_spec("mempalace") is None:
        raise SystemExit("mempalace installation completed but the package is still unavailable")


def initialize_palace(palace_dir: Path) -> None:
    ensure_mempalace_installed()

    from mempalace.palace import get_collection

    palace_dir.mkdir(parents=True, exist_ok=True)
    collection = get_collection(str(palace_dir))
    try:
        collection.count()
    except Exception:
        pass


def write_palace_readme(vault_dir: Path) -> None:
    palace_dir = vault_dir / "palace"
    palace_readme = textwrap.dedent(
        f"""\
        # Palace — MemPalace Integration

        This directory holds the local MemPalace collection used as the recall layer
        for `{vault_dir.name}`.

        ## Mine your data

        ```bash
        # Conversation exports
        mempalace --palace {palace_dir} mine {vault_dir / "raw"} --mode convos --wing <project-name>

        # Code and documentation
        mempalace --palace {palace_dir} mine {vault_dir / "raw"} --mode projects --wing <project-name>

        # Inspect indexed content
        mempalace --palace {palace_dir} status
        ```

        ## Search

        ```bash
        mempalace --palace {palace_dir} search "why did we switch to GraphQL"
        mempalace --palace {palace_dir} search "auth migration" --wing <project-name>
        ```

        ## MCP server

        ```bash
        claude mcp add mempalace -- python -m mempalace.mcp_server --palace {palace_dir}
        ```
        """
    )
    (palace_dir / "README.md").write_text(palace_readme, encoding="utf-8")


def update_config_for_palace(vault_dir: Path) -> None:
    config_path = vault_dir / "memory.config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    palace = config.setdefault("palace", {})
    palace["enabled"] = True
    palace.setdefault("path", "palace/")
    palace.setdefault("backend", "mempalace")
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


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

    if args.enable_palace:
        palace_dir = destination / "palace"
        initialize_palace(palace_dir)
        write_palace_readme(destination)
        update_config_for_palace(destination)
        print(f"Initialized MemPalace recall layer in {palace_dir}")

    print(f"Created memory vault: {destination}")
    print("Next steps:")
    print(f"  python {script_dir / 'rebuild_index.py'} {destination}")
    print(f"  python {script_dir / 'lint_memory.py'} {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
