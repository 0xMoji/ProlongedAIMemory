# ProlongedAIMemory

`ProlongedAIMemory` is a Codex skill for long-term agent memory.

It combines two complementary ideas:

- a retrieval substrate such as MemPalace for chunking, recall, and optional semantic search
- an LLM-maintained markdown wiki for durable, navigable knowledge

The repository currently ships one reusable skill:

- `agent-memory/`: initialize and maintain a local memory vault with separate raw evidence, curated wiki pages, generated index, and append-only log

## Repository Layout

```text
agent-memory/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── assets/memory-template/
```

## What The Skill Provides

- a memory schema with `raw/`, `wiki/`, `index.md`, `log.md`, `inbox/`, `scratch/`, and optional `palace/`
- a bootstrap script to create a new vault from a starter template
- an index rebuild script for generated navigation
- a lint script for frontmatter, broken sources, orphan pages, stale pages, and broken wiki links

## Quick Start

Create a new memory vault:

```bash
python agent-memory/scripts/bootstrap_memory.py /path/to/vault --agent-name Codex
python agent-memory/scripts/rebuild_index.py /path/to/vault
python agent-memory/scripts/lint_memory.py /path/to/vault
```

## Philosophy

- `raw/` is immutable evidence
- `wiki/` is curated, durable knowledge
- `index.md` and `log.md` make the memory legible to future agents
- retrieval backends are accelerators, not the final truth source
