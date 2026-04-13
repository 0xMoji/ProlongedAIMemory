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

- If the same topic has appeared in multiple separate queries, promote it.
- If the fact is grounded in `raw/` evidence, promote it with explicit `sources`.
- If a future agent starting cold would benefit from it, promote it.
- If it updates or contradicts an existing wiki page, promote it and revise the existing page.
- If it only matters for the current task and likely will not recur, leave it in `scratch/`.
- If in doubt, promote it.

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
python scripts/lint_memory.py /path/to/vault --check-contradictions
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

MemPalace is a local memory system that stores conversation history and project
material in a local ChromaDB-backed index. It runs on your machine without
requiring hosted memory APIs.

If `memory.config.json` shows `"palace": {"enabled": true}`, the integration is active.

### Setup

```bash
python scripts/bootstrap_memory.py /path/to/vault --agent-name Codex --enable-palace
```

This creates a local collection inside `/path/to/vault/palace/`.

### Mine your data

Run this whenever you have new raw material to index:

```bash
# Conversation exports (Claude, ChatGPT, Slack)
mempalace --palace /path/to/vault/palace mine /path/to/vault/raw --mode convos --wing <project-name>

# Code and documentation
mempalace --palace /path/to/vault/palace mine /path/to/vault/raw --mode projects --wing <project-name>

# Inspect the local index
mempalace --palace /path/to/vault/palace status
```

### Retrieve from the palace

Use MemPalace search when `index.md` and `wiki/` do not surface the answer:

```bash
# Semantic search across the local palace
mempalace --palace /path/to/vault/palace search "why did we decide to use Postgres"

# Scoped to a single project wing
mempalace --palace /path/to/vault/palace search "auth migration" --wing <project-name>
```

### Agent retrieval discipline

When palace integration is enabled, follow this order:

1. Check `index.md` and matching `wiki/` pages first.
2. If the wiki is missing, stale, or underspecified, run `mempalace search` against the local palace.
3. Synthesize the answer from wiki summaries plus verbatim palace evidence.
4. If new durable knowledge is discovered, update `wiki/` and append to `log.md`.

Rule of thumb:

- `palace/` is the recall layer.
- `wiki/` is the synthesis layer.

Do not answer directly from raw palace output when a curated wiki page already exists.

### MCP server

If you are using an MCP-capable environment:

```bash
claude mcp add mempalace -- python -m mempalace.mcp_server --palace /path/to/vault/palace
```

This gives the agent direct access to tools such as `mempalace_status`,
`mempalace_search`, and the MemPalace knowledge graph queries.
