# Memory Schema

## Directory Layout

Every vault follows this layout:

```text
vault/
├── AGENTS.md
├── memory.config.json
├── index.md
├── log.md
├── raw/
├── inbox/
├── scratch/
├── palace/        # optional
└── wiki/
```

Directory roles:

- `raw/`: immutable source material such as transcripts, exports, notes, PDFs, or copied snippets.
- `inbox/`: quick capture area for unprocessed facts, loose notes, and promotion candidates.
- `scratch/`: temporary working notes for the current task or session.
- `palace/`: optional retrieval backend artifacts such as vector indexes, room manifests, or MemPalace data.
- `wiki/`: durable pages curated by the agent.

## Root Files

- `AGENTS.md`: operational rules for any agent working inside the vault.
- `memory.config.json`: vault metadata, schema version, optional namespaces, and MemPalace backend configuration.
- `index.md`: generated directory of the curated knowledge layer.
- `log.md`: append-only operational log.

## Config Structure

`memory.config.json` stores the top-level vault configuration.

Important sections:

- `vault`: display name for the vault
- `agent`: default primary agent
- `namespaces.enabled`: enables multi-project organization
- `namespaces.wings`: project names that should mirror `wiki/<wing>/`
- `palace.enabled`: whether the local MemPalace recall layer is active
- `palace.path`: relative path to the local palace directory

## Wiki Page Requirements

Every durable page under `wiki/` must begin with frontmatter:

```yaml
---
title: Example Page
type: overview
status: active
updated: 2026-04-12
tags:
  - planning
  - memory
sources:
  - raw/interviews/user-01.md
aliases:
  - Example Alias
---
```

Required keys:

- `title`
- `type`
- `status`
- `updated`

Optional keys:

- `tags`
- `sources`
- `aliases`
- `summary`

Allowed `type` values:

- `overview`
- `entity`
- `topic`
- `decision`
- `timeline`
- `session`
- `reference`

Allowed `status` values:

- `active`
- `draft`
- `stale`
- `archived`

## Wiki Page Body

Use short sections. The recommended pattern is:

```markdown
# Title

## Summary

One short paragraph with the current state.

## Facts

- Durable fact

## Evidence

- `raw/...`

## Links

- [[related-page]]
```

Not every page needs every section, but every page should include at least one of:

- a `sources` frontmatter entry
- an `Evidence` section
- an outgoing link in `Links`

## Link Policy

Preferred durable links:

- `[[page-slug]]` for links between wiki pages
- relative markdown links for files outside `wiki/`, such as `../raw/interview.md`

Page slug rule:

- slug = file path under `wiki/` without `.md`
- `wiki/people/founders.md` becomes `people/founders`

## Source Policy

- `raw/` paths in frontmatter are relative to the vault root.
- Do not put generated summaries back into `raw/`.
- If a fact is inferred, say so in the page body and keep the underlying evidence explicit.

## Log Policy

Append entries to `log.md` in this format:

```markdown
- 2026-04-12 20:15 | query | Verified onboarding decision from `wiki/decisions.md` and `raw/meeting-2026-04-11.md`
```

Fields:

- timestamp
- operation type such as `ingest`, `query`, `promote`, `lint`
- one sentence describing what changed or what was verified
