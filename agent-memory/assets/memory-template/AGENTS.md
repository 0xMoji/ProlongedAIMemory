# Agent Memory Rules

This vault belongs to `{{AGENT_NAME}}` and is named `{{VAULT_NAME}}`.

## Mission

Use this vault to preserve long-term memory in a form that future agents can navigate.

## Rules

- `raw/` is immutable source material. Never rewrite it.
- `wiki/` stores curated knowledge pages with frontmatter.
- `index.md` is generated from `wiki/` pages.
- `log.md` is append-only.
- `inbox/` is for uncategorized captures that still need promotion.
- `scratch/` is temporary and may be deleted or reorganized freely.
- `palace/` is optional retrieval infrastructure, not the only truth source.

## Working Order

1. Read `index.md` before answering from memory.
2. Use `wiki/` first, then verify against `raw/` if facts may have changed.
3. When a new durable fact appears, update `wiki/` and append to `log.md`.
4. Rebuild `index.md` after meaningful wiki changes.
5. Run lint before handing the vault off to another agent.
