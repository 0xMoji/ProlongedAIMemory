---
name: agent-memory
description: Persistent memory management for agents. Use when the user wants an agent to keep long-term memory, maintain a self-updating wiki, retrieve past facts, ingest new notes or transcripts, or run a structured memory vault with separate raw evidence and curated knowledge pages.
---

# Agent Memory

Use this skill to run a local memory vault that combines:

- a raw evidence layer
- an optional retrieval backend such as MemPalace
- a curated markdown wiki that the agent maintains over time

Read [references/schema.md](references/schema.md) first when you need the directory layout or page format.
Read [references/workflows.md](references/workflows.md) when you are about to ingest, answer from memory, or lint the vault.

## What This Skill Owns

This skill treats memory as three layers:

1. `raw/` is the immutable source of truth.
2. `wiki/` is the maintained knowledge layer.
3. `index.md` and `log.md` are the navigation and audit layer.

Optional:

- `palace/` can hold a retrieval substrate such as MemPalace metadata, vector stores, or adapters.

## Default Behavior

When the user asks you to set up memory:

1. Run `scripts/bootstrap_memory.py` to create a vault from the bundled template.
2. Review the generated `AGENTS.md`, `memory.config.json`, and starter wiki pages.
3. Run `scripts/rebuild_index.py` so the root `index.md` reflects the current pages.
4. Run `scripts/lint_memory.py` and fix any reported issues.

When the user asks you to retrieve memory or answer from prior context:

1. Start with `index.md` and relevant `wiki/` pages.
2. If the wiki is missing evidence or looks stale, inspect `raw/` and any `palace/` backend.
3. Answer from the curated layer when possible, but verify against raw evidence before stating facts that may have changed.
4. If the answer creates durable knowledge, update or create a wiki page and append a log entry.

When the user asks you to save new memory:

1. Put raw captures in `raw/` or append quick notes to `inbox/capture.md`.
2. Promote durable insights into `wiki/` pages instead of leaving them only in inbox or scratch files.
3. Append a short entry to `log.md`.
4. Rebuild the index and run lint if multiple pages changed.

## Hard Rules

- Never rewrite or summarize over the original files inside `raw/`.
- Do not store final answers only in `scratch/`; either keep them ephemeral or promote them into `wiki/`.
- Keep `wiki/` pages opinionated but evidence-backed. Prefer concise summaries with explicit source references.
- Prefer updating existing pages over creating near-duplicate pages.
- `log.md` is append-only.
- If `palace/` exists, treat it as a retrieval accelerator, not as the only source of truth.

## File Operations

Important scripts:

- `python scripts/bootstrap_memory.py /path/to/vault --agent-name Codex`
- `python scripts/rebuild_index.py /path/to/vault`
- `python scripts/lint_memory.py /path/to/vault`

If you create new wiki pages manually, follow the frontmatter and section rules from [references/schema.md](references/schema.md).

## Retrieval Order

Use this order unless the user asks otherwise:

1. `index.md`
2. matching `wiki/` pages
3. `inbox/capture.md` and `scratch/`
4. `raw/`
5. optional `palace/`

## Maintenance Standard

A healthy vault should always satisfy these conditions:

- every durable topic lives in `wiki/`
- every wiki page has frontmatter and at least one outgoing link or source
- `index.md` can be regenerated without manual edits
- `log.md` tells the story of what changed and why

When in doubt, optimize for a vault that a future agent can navigate without the original chat history.
