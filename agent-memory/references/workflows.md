# Workflows

## Bootstrap

Use this when creating a new vault:

```bash
python scripts/bootstrap_memory.py /path/to/vault --agent-name Codex
python scripts/rebuild_index.py /path/to/vault
python scripts/lint_memory.py /path/to/vault
```

## Ingest

Use ingest when new information arrives.

1. Save or copy the raw material into `raw/`.
2. If the material is not yet curated, record a short capture in `inbox/capture.md`.
3. Update an existing wiki page or create a new one under `wiki/`.
4. Append a log entry to `log.md`.
5. Rebuild the index and lint if the change touched durable memory.

Promotion heuristic:

- Promote when the information is likely to matter again.
- Leave it in `scratch/` when it only matters for the current task.

## Query

Use this order:

1. Open `index.md` to find candidate pages.
2. Search `wiki/` for relevant titles, aliases, tags, or link targets.
3. Inspect linked raw evidence if the fact may have changed or if you need stronger grounding.
4. If `palace/` exists, use it as a secondary retrieval layer for recall, then validate against wiki or raw evidence.
5. If the answer uncovered missing durable knowledge, update the vault before you finish.

## Lint

Run lint after structural edits or before handing the vault to another agent:

```bash
python scripts/lint_memory.py /path/to/vault
```

Lint checks:

- required files and folders
- missing frontmatter
- missing required keys
- broken source references
- orphan pages
- stale pages older than the threshold

## Maintenance

Periodic maintenance should:

1. clear promoted items from `inbox/`
2. archive truly obsolete pages by setting `status: archived`
3. mark pages `stale` when they may be outdated but still useful
4. rebuild `index.md`
5. run lint

## Optional MemPalace Integration

If the vault also uses MemPalace, treat it like this:

- `raw/` remains the immutable evidence layer.
- `palace/` stores retrieval indexes, exported manifests, or backend notes.
- `wiki/` remains the human-readable, agent-maintained layer.

Recommended discipline:

- retrieve with MemPalace when recall matters
- answer from the wiki when synthesis matters
- update the wiki when new durable knowledge is discovered
