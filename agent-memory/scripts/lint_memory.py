#!/usr/bin/env python3
"""Lint a memory vault for structural and content issues."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from _memory_utils import (
    REQUIRED_FRONTMATTER_KEYS,
    REQUIRED_ROOT_PATHS,
    collect_wiki_links,
    iter_wiki_pages,
    page_slug,
    parse_frontmatter,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault", nargs="?", default=".", help="Path to the memory vault")
    parser.add_argument(
        "--stale-days",
        type=int,
        default=45,
        help="Warn when a non-archived page is older than this many days",
    )
    parser.add_argument(
        "--check-contradictions",
        action="store_true",
        help="Run basic contradiction checks across wiki pages (frontmatter-level)",
    )
    return parser.parse_args()


def check_contradictions(pages_meta: list[dict]) -> list[str]:
    """Run lightweight contradiction checks based on frontmatter only."""
    issues: list[str] = []

    by_prefix: dict[str, list[dict]] = {}
    for page in pages_meta:
        page_type = page.get("type", "unknown")
        if page_type not in {"entity", "topic", "decision"}:
            continue
        prefix = page["title"].split(":")[0].split(" - ")[0].strip().lower()
        by_prefix.setdefault(prefix, []).append(page)

    for prefix, group in by_prefix.items():
        if len(group) < 2:
            continue
        statuses = {page["status"] for page in group}
        if "active" in statuses and "archived" in statuses:
            slugs = [page["slug"] for page in group]
            issues.append(
                f"[contradiction] '{prefix}' appears as both active and archived: {slugs}"
            )

    today = date.today()
    for page in pages_meta:
        if page["status"] != "active":
            continue
        updated = page.get("updated", "unknown")
        if updated == "unknown":
            continue
        try:
            updated_date = date.fromisoformat(updated)
        except ValueError:
            continue
        age_days = (today - updated_date).days
        if age_days > 90:
            issues.append(
                f"[contradiction] '{page['slug']}' is marked 'active' but has not been "
                f"updated in {age_days} days — consider marking it 'stale'"
            )

    return issues


def main() -> int:
    args = parse_args()
    vault = Path(args.vault).expanduser().resolve()
    wiki_root = vault / "wiki"

    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_ROOT_PATHS:
        if not (vault / rel).exists():
            errors.append(f"Missing required path: {rel}")

    known_slugs: set[str] = set()
    incoming_links: dict[str, int] = {}
    outbound_links: dict[str, set[str]] = {}
    pages_meta: list[dict] = []

    for page_path in iter_wiki_pages(vault):
        slug = page_slug(wiki_root, page_path)
        known_slugs.add(slug)
        text = page_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)

        if not frontmatter:
            errors.append(f"{slug}: missing frontmatter")
            continue

        for key in REQUIRED_FRONTMATTER_KEYS:
            if key not in frontmatter or frontmatter[key] in ("", []):
                errors.append(f"{slug}: missing required frontmatter key '{key}'")

        sources = frontmatter.get("sources", [])
        if isinstance(sources, str):
            sources = [sources]
        for source in sources:
            if not (vault / source).exists():
                errors.append(f"{slug}: source does not exist: {source}")

        updated = frontmatter.get("updated")
        status = str(frontmatter.get("status") or "")
        page_type = str(frontmatter.get("type") or "unknown")
        if isinstance(updated, str):
            try:
                updated_date = date.fromisoformat(updated)
            except ValueError:
                errors.append(f"{slug}: invalid updated date: {updated}")
            else:
                age = (date.today() - updated_date).days
                if status not in {"archived", "stale"} and age > args.stale_days:
                    warnings.append(f"{slug}: page is {age} days old; consider reviewing it")

        targets = collect_wiki_links(body)
        outbound_links[slug] = targets
        for target in targets:
            incoming_links[target] = incoming_links.get(target, 0) + 1

        pages_meta.append(
            {
                "slug": slug,
                "title": str(frontmatter.get("title") or slug),
                "type": page_type,
                "status": status or "unknown",
                "updated": str(updated or "unknown"),
            }
        )

    for slug, targets in sorted(outbound_links.items()):
        for target in sorted(targets):
            if target not in known_slugs:
                errors.append(f"{slug}: broken wiki link: [[{target}]]")

    for page_path in iter_wiki_pages(vault):
        slug = page_slug(wiki_root, page_path)
        if slug == "home":
            continue
        if incoming_links.get(slug, 0) == 0:
            warnings.append(f"{slug}: orphan page with no incoming wiki links")

    if args.check_contradictions:
        warnings.extend(check_contradictions(pages_meta))

    lines = [f"Memory lint report for {vault}", ""]
    if errors:
        lines.append("Errors:")
        lines.extend(f"- {item}" for item in errors)
        lines.append("")
    if warnings:
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in warnings)
        lines.append("")
    if not errors and not warnings:
        lines.append("No issues found.")

    print("\n".join(lines).rstrip())
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
