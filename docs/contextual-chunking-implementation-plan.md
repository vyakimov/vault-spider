# Contextual Chunking and Multi-Resolution Retrieval

## Final Implementation Amendment: One Canonical Note-Summary Store

The generation/storage design below is superseded by the implemented note-level design.
`index.contextual` remains opt-in. Both `manual` and `openrouter` use the same canonical records
under `index.context_path` (default `context-data/summaries`). Manual mode imports summaries from
Codex/Claude Code jobs and makes no context API calls. OpenRouter mode automatically generates
missing/stale summaries with one call per note and writes those records to the same directory.
There is no per-chunk generation or separate context cache.

Sync copies each ready note summary into derived document/chunk text before embedding; Chroma is
disposable and never authoritative. Missing/stale summaries do not block raw-note indexing.
See `docs/note-context-summaries.md` for the authoritative workflow and storage contract. The
remainder of this file records the original staged plan and is retained as design history.

## Summary

Replace the current H1–H3/character-window splitter with deterministic Markdown-aware chunks,
add trustworthy deterministic prefixes and optional LLM-generated context, and change `mixed`
retrieval to combine document and chunk signals while returning only line-addressable source
chunks.

The implementation will preserve the existing JSON envelope and schema version, remain opt-in
for LLM generation, support resumable explicit backfill, and isolate context-generation failures
per note. Generated prose will help embedding and reranking but will never become cited evidence
or satisfy exact-match constraints.

Delivery should be organized as staged commits, but completed as one coordinated effort:

1. Structural chunking and index migration.
2. Context generation, caching, and safe sync integration.
3. Source/dense/lexical representation separation.
4. Genuine mixed retrieval.
5. Evaluation, documentation, and rollout verification.

## Public Interfaces and Defaults

### Configuration

Add two strictly validated `index` settings:

```yaml
index:
  chroma_path: chroma_db
  contextual: false
  contextual_bm25: false
```

- `contextual` enables context generation for new or changed eligible notes.
- Existing unchanged entries are upgraded only by `sync --contextualize`.
- `contextual_bm25` controls whether generated context participates in BM25. It defaults to
  `false`; dense retrieval and reranking still use context.
- Reject `contextual_bm25: true` when `contextual` is false.
- Add optional `OPENROUTER_CONTEXT_MODEL`; default it to `OPENROUTER_CHAT_MODEL`.
- Context-off indexes remain network-compatible with today: no chat calls are made.

Chunk-size and prompt limits are algorithm constants, not installation settings:

- Target: 450 estimated tokens.
- Soft minimum: 300.
- Soft maximum: 600.
- Hard maximum: 900.
- Generated context: one or two sentences, maximum 400 normalized characters.
- A note is LLM-eligible only when it produces at least two chunks.
- One context call may cover at most 16 chunks and 12,000 estimated input tokens.

### CLI and MCP

Extend `sync` with:

- `--contextualize`: upgrade unchanged eligible notes whose context is missing, stale, or built
  with a different model/prompt version.
- `--refresh-context`: imply `--contextualize`, bypass cached contexts, and regenerate all
  eligible contexts.
- Both flags work with `--dry-run` without making provider calls.
- Reject either flag when `index.contextual` is false.

Thread these flags through the MCP `sync_index` tool while preserving `dry_run: true` as its
default.

Keep schema version 2 and all existing result fields. Add a nested `context` result:

```json
{
  "eligible_notes": 0,
  "eligible_sections": 0,
  "ready_sections": 0,
  "generated": 0,
  "cache_hits": 0,
  "failed_notes": [],
  "coverage": 1.0
}
```

Dry-run additionally returns `would_rechunk`, `would_contextualize`, and
`would_refresh_context` path lists. Per-note context failures produce `ok: true`, populate
`failed_notes`, and add warnings.

Extend `stats` with chunk schema version, context prompt version/model, eligible/ready/stale
section counts, and coverage.

### Retrieval contract

Keep existing candidate fields and types. Add only optional additive fields:

- `heading_path`: full H1–H6 ancestry.
- `parent_section_id`: stable H1–H3 parent identifier.
- `scores.parent`: the mixed-mode document-derived contribution.

Preserve `heading` as the current H1–H3 label so evaluation datasets and downstream citation
matching remain valid. Preserve `chunk_id` in the existing `note_id::sNNN` format.

Change documented `mixed` semantics:

- Search document and section pools.
- Use document rankings as parent signals.
- Return only section chunks with exact source line ranges.
- Apply the three-chunks-per-note diversity cap before reranking.

`document` and `section` modes retain their current single-pool behavior.

## Implementation Changes

### 1. Markdown-aware deterministic chunking

Refactor `vault_spider/corpus/chunker.py` around Markdown block spans obtained from
`markdown-it-py` token `map` ranges.

- Parse headings, paragraphs, lists, fenced code, blockquotes/callouts, and tables without
  changing note text.
- Maintain an H1–H6 heading stack and assign every block a complete heading path.
- Define an H1–H3 parent section for each chunk; heading-less content belongs to a preamble
  parent.
- Never combine content across H1–H3 parents or across different full heading paths. Short
  structurally complete chunks may remain below 300 tokens.
- Combine adjacent blocks within one heading path toward 450 tokens without exceeding 600 when
  possible.
- Use a deterministic token estimator that counts Latin/alphanumeric runs, individual CJK
  characters, and punctuation; do not add a model-specific tokenizer dependency.
- Preserve fenced code, tables, callouts, paragraphs, and top-level list items as atomic blocks
  below the 900-token hard limit.
- Split oversized lists between top-level items, tables between rows, code by lines, and prose
  by sentences.
- Only sentence-split prose receives up to 50 estimated tokens of overlap. Ordinary chunks,
  lists, tables, and code do not overlap.
- Any remaining oversized single line uses a deterministic character fallback so no embedding
  input exceeds the hard ceiling.
- Retrieval-only wrappers such as “continued code/table” markers must remain outside source
  evidence and line ranges.
- Preserve complete line coverage and exact 1-based inclusive ranges.

Add `CHUNK_SCHEMA_VERSION = 2`. Store it on every entry and in collection metadata. During
normal sync, any note whose entries lack the current version is automatically promoted to the
update set; dry-run reports it in `would_rechunk`. This avoids requiring a destructive reset.

### 2. Retrieval-text composition and source isolation

Compose section documents as:

```text
# <title>
Path: <vault-relative path>
Type: <type>                 # when non-empty
Tags: <tags>                 # when non-empty
Heading path: <H1 > H2 > H4>
Context: <generated context> # when ready

<exact source chunk>
```

Store `source_offset` metadata pointing to the first source character. Do not recover source
content with a regex.

Maintain three logical views:

- `dense_text`: the stored Chroma document, including generated context.
- `lexical_text`: deterministic headers plus source, including generated context only when
  `contextual_bm25` is true.
- `source_text`: `dense_text[source_offset:]`.

Rehydrate all three views in `IndexStore`. Build BM25 from `lexical_text`; use `dense_text` for
embeddings and reranking; use `source_text` for evidence, previews, synthesis, quoted-phrase
boosts, and `must_include`.

Document entries keep their current indexing composition but also receive a source offset so
document excerpts stop exposing synthetic headers.

### 3. Context generation and persistent cache

Add an index-layer contextualizer and a SQLite cache under the Chroma directory.

The contextualizer must:

- Keep chunking completely deterministic and LLM-free.
- Treat note content as untrusted prompt data and explicitly ignore instructions found inside
  it.
- Ask for descriptive retrieval context only, without adding facts or interpretation.
- Use JSON-object mode and require:

```json
{
  "contexts": [
    {"chunk_ref": "<exact supplied ref>", "context": "<one or two sentences>"}
  ]
}
```

- Validate that every requested reference appears exactly once, no unknown references appear,
  and every context is a non-empty string.
- Normalize whitespace to one line and truncate to 400 characters.
- Reject the entire batch on malformed, missing, duplicated, or misaligned output.
- Use one call per note when it fits; otherwise make deterministic batches of at most 16
  chunks.
- Supply the full title, heading outline, and body when they fit within 12,000 estimated tokens.
- For oversized notes, supply the title, complete heading outline, preamble, and the H1–H3
  parent sections relevant to that batch, trimming only distant unrelated parents.

Construct each cache key from:

- Prompt version.
- Context model.
- Note ID.
- Hash of the exact rendered document representation sent in that request.
- Full heading path.
- Chunk source hash.
- Occurrence number among identical chunks.

Do not use raw `note.content_hash`, because it includes irrelevant frontmatter timestamps. Do
not use a bare section hash.

Use SQLite with WAL mode, a busy timeout, and an LRU limit of 50,000 entries. Persist each
successful batch before embedding begins so an embedding failure or later context-batch failure
does not waste completed generation.

Store these section metadata fields using Chroma-compatible scalar values:

- `chunk_schema_version`
- `heading_path`
- `parent_section_id`
- `source_offset`
- `section_hash`
- `context_status`: `disabled`, `not_needed`, or `ready`
- `context`
- `context_model`
- `context_prompt_version`
- `context_input_hash`

### 4. Sync planning, migration, and failure behavior

Refactor sync around per-note update plans rather than immediately appending flat entries.

For each note:

1. Split and compose deterministic entries.
2. Determine whether it is new, changed, moved, structurally stale, context-stale, or unchanged.
3. Reuse valid cached contexts unless refresh was requested.
4. Generate all missing contexts before embedding.
5. Mark the note ready for replacement only when all required contexts validate.

Failure behavior:

- Existing note context failure: retain every old entry for that note.
- New note context failure: omit that note from this sync.
- Continue contextualizing and indexing unrelated notes.
- Never newly write an eligible note with empty generated context while contextual mode is
  enabled.
- Preserve the existing global embedding-failure behavior: finish all provider work before
  deletes, and abort without changing the collection when embedding resolution fails.
- Cache contexts even when the later embedding stage fails.
- Deletions of notes removed from disk remain independent of context generation.

Context migration:

- Enabling contextual mode does not automatically spend money on unchanged notes.
- New and changed eligible notes contextualize during ordinary sync.
- `--contextualize` upgrades missing or stale unchanged notes.
- Model or prompt-version changes make entries stale and are repaired by `--contextualize`.
- `--refresh-context` bypasses cache and rebuilds every eligible context.
- A second completed sync must perform zero chat and embedding calls.

Rollback behavior:

- Once a collection contains contextual embeddings, changing `index.contextual` to false
  requires `sync --reset`; reject ordinary construction with `config_mismatch` rather than
  silently mixing rollback semantics.
- Use a separate Chroma path for contextual versus non-contextual A/B evaluation.
- Fix the existing reset construction seam by passing `allow_model_mismatch=args.reset` into
  `IndexStore`.

After successful sync, update collection metadata with current chunk/context schema targets and
contextual state without treating prompt/model changes like embedding-space corruption.

### 5. Genuine mixed retrieval

Refactor search scoring so document and section pools can be ranked independently with one
query embedding.

For `mixed`:

1. Apply metadata and exact-source filters to both pools.
2. Produce four ranked section lists:
   - Direct section dense rank.
   - Direct section BM25 rank.
   - Document-dense rank expanded to child chunks.
   - Document-BM25 rank expanded to child chunks.
3. Route only the top 20 document candidates, with at most three children per document and at
   most 2,000 routed child embeddings.
4. For dense parent expansion, bulk-fetch child embeddings once and rank them by normalized dot
   product with the query.
5. For lexical parent expansion, rank children by their existing source-safe BM25 scores.
6. Fuse the four lists with weighted multi-list RRF:
   - 80% total direct-section weight.
   - 20% total parent-document weight.
   - Split each total using the configured semantic weight.
   - Use the existing `rrf_k`.
7. Retain at most three sections per note before constructing the reranker pool.
8. Increase `rerank_top_k` from 30 to 60 for thorough mode; fast mode continues to skip
   reranking.
9. Rerank using contextual dense text, then apply recency exactly as today.
10. Return source-only excerpts and section line ranges.

Promoted chunks absent from the original direct top-K receive their locally computed dense/BM25
signals. Candidate `scores.parent` exposes the parent contribution, and `why` distinguishes
direct matches from document-promoted matches.

Document-only retrieval continues to return document candidates. Mixed retrieval never returns
a whole-note candidate, preventing note-level embeddings from producing uncitable head-only
excerpts.

## Test and Acceptance Plan

### Deterministic chunking

Cover:

- H1–H6 ancestry and preservation of H1–H3 `heading` labels.
- Preamble and heading-less notes.
- Nested lists, task lists, oversized list items, tables, fenced code containing heading
  markers, blockquotes, Obsidian callouts, and ordinary prose.
- Target/min/max behavior and hard-limit fallback.
- Sentence-only overlap.
- Exact source recovery through `source_offset`.
- Complete source-line coverage and stable sequential chunk IDs.
- Chunk schema migration of an otherwise unchanged index.
- Evaluation label validation remaining unchanged.

### Context generation and cache

Cover:

- One-note structured batching and deterministic large-note batching.
- Exact keyed response validation.
- Duplicate chunk text in one note and across notes receiving distinct cache entries.
- Title/body edits invalidating context while timestamp-only frontmatter changes do not.
- Moves reusing LLM context while recomposing/re-embedding the path prefix.
- Prompt/model version invalidation.
- Cache persistence across store instances and embedding failures.
- Concurrent SQLite readers/writers and LRU pruning.
- Prompt-injection content remaining quoted as untrusted input.
- Single-chunk notes making zero chat calls.
- Context-disabled indexes making zero chat calls.

### Sync and contracts

Cover:

- Explicit backfill, refresh, and dry-run predictions.
- Per-note failure retaining an old note, skipping a new note, and indexing successful
  neighbors.
- No empty-context eligible entries.
- Context coverage and stats.
- Context rollback requiring reset.
- Reset bypassing embedding-model mismatch construction.
- CLI schema and MCP arguments staying synchronized.
- No-op second sync with zero provider work.
- Generated context never appearing in evidence, previews, synthesis prompts, exact phrase
  boosts, or `must_include` matches.

### Retrieval

Use deterministic rank fixtures to verify:

- Mixed mode consults both pools.
- Parent-document hits promote the correct child chunks.
- Weighted RRF values and `scores.parent`.
- Metadata and exact-source filters apply before parent expansion.
- Three-per-note diversity happens before the 60-item reranker pool.
- Promoted results always have valid section headings and line ranges.
- Document and section modes retain their prior single-pool ranking behavior.
- Reranker failure still falls back to fused ordering.
- Recency remains the final scoring step.

### Verification and evaluation

Run:

```bash
uv run ruff check .
uv run pytest -q
uv run pyright vault_spider
uv run python tools/build_codebase_map.py
git diff --check
```

Regenerate and commit both codebase-map artifacts after structural changes.

Perform real-model evaluation using separate Chroma paths:

1. New structure-aware chunks, context off.
2. Context on, contextual BM25 off.
3. Context on, contextual BM25 on.

Record retrieval nDCG@k, evidence-group recall, complete@k, MRR, synthesis citation coverage,
context coverage, generated/cache-hit counts, indexing cost, and query latency. Keep
`contextual` and `contextual_bm25` disabled by default regardless of the first evaluation
result; default changes require a separate decision.

## Rollout Defaults

- Ship with LLM contextualization off.
- The first normal sync automatically migrates old chunks to chunk schema version 2 but makes
  no chat calls.
- Validate the deterministic chunking baseline before enabling context.
- Enable `index.contextual: true`, preview cost with `sync --contextualize --dry-run`, then run
  the explicit backfill.
- Confirm 100% eligible-section coverage or inspect `failed_notes`; rerunning backfill resumes
  from the persistent cache.
- Keep contextual BM25 off for the recommended production configuration until the A/B result
  demonstrates a lexical benefit.
- Treat the two original contextual-retrieval documents as superseded by this consolidated
  design and update repository architecture documentation accordingly.
