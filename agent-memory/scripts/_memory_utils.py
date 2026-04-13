#!/usr/bin/env python3
"""Shared helpers for memory vault scripts."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED_ROOT_PATHS = (
    "AGENTS.md",
    "memory.config.json",
    "index.md",
    "log.md",
    "raw",
    "inbox",
    "scratch",
    "wiki",
)

REQUIRED_FRONTMATTER_KEYS = ("title", "type", "status", "updated")


def load_config(vault_path: Path) -> dict:
    config_path = vault_path / "memory.config.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def iter_wiki_pages(vault_path: Path) -> list[Path]:
    wiki_root = vault_path / "wiki"
    if not wiki_root.exists():
        return []
    return sorted(path for path in wiki_root.rglob("*.md") if path.is_file())


def page_slug(wiki_root: Path, page_path: Path) -> str:
    return page_path.relative_to(wiki_root).with_suffix("").as_posix()


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    block = text[4:end]
    body = text[end + 5 :]
    data: dict[str, object] = {}
    current_key: str | None = None

    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, [])
            assert isinstance(data[current_key], list)
            data[current_key].append(line[4:].strip())
            continue
        if ": " in line:
            key, value = line.split(": ", 1)
        elif line.endswith(":"):
            key, value = line[:-1], ""
        else:
            continue
        key = key.strip()
        value = value.strip()
        current_key = key
        if not value:
            data[key] = []
        else:
            data[key] = value

    return data, body


def collect_wiki_links(text: str) -> set[str]:
    links: set[str] = set()
    start = 0
    while True:
        left = text.find("[[", start)
        if left == -1:
            break
        right = text.find("]]", left + 2)
        if right == -1:
            break
        target = text[left + 2 : right].strip()
        if target:
            links.add(target)
        start = right + 2
    return links
