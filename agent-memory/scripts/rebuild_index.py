#!/usr/bin/env python3
"""Regenerate the root index.md from pages in wiki/."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from _memory_utils import iter_wiki_pages, page_slug, parse_frontmatter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault", nargs="?", default=".", help="Path to the memory vault")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vault = Path(args.vault).expanduser().resolve()
    wiki_root = vault / "wiki"
    pages = []

    for page_path in iter_wiki_pages(vault):
        text = page_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        title = str(frontmatter.get("title") or page_path.stem.replace("-", " ").title())
        page_type = str(frontmatter.get("type") or "unknown")
        status = str(frontmatter.get("status") or "unknown")
        updated = str(frontmatter.get("updated") or "unknown")
        summary = ""
        for line in body.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                summary = stripped
                break
        if len(summary) > 140:
            summary = summary[:137] + "..."
        pages.append(
            {
                "title": title,
                "slug": page_slug(wiki_root, page_path),
                "type": page_type,
                "status": status,
                "updated": updated,
                "summary": summary,
            }
        )

    grouped: dict[str, list[dict]] = defaultdict(list)
    stale_pages = []
    for page in sorted(pages, key=lambda item: (item["type"], item["title"].lower())):
        grouped[page["type"]].append(page)
        if page["status"] == "stale":
            stale_pages.append(page)

    lines = [
        "# Memory Index",
        "",
        f"_Generated: {datetime.now().isoformat(timespec='minutes')}_",
        "",
        "This index is generated from `wiki/` pages. Edit the pages, not this file.",
        "",
        "## Summary",
        "",
        f"- Total pages: {len(pages)}",
        f"- Page types: {len(grouped)}",
        f"- Stale pages: {len(stale_pages)}",
        "",
    ]

    if stale_pages:
        lines.extend(["## Stale Pages", ""])
        for page in stale_pages:
            lines.append(
                f"- [[{page['slug']}]] | {page['title']} | updated {page['updated']}"
            )
        lines.append("")

    for page_type in sorted(grouped):
        title = page_type.replace("-", " ").title()
        lines.extend([f"## {title}", ""])
        for page in grouped[page_type]:
            detail = f"- [[{page['slug']}]] | {page['status']} | updated {page['updated']}"
            if page["summary"]:
                detail += f" | {page['summary']}"
            lines.append(detail)
        lines.append("")

    (vault / "index.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Rebuilt {vault / 'index.md'} from {len(pages)} wiki pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
