# Contextual Retrieval for vault-spider

## Context

Section chunks are embedded with only a thin synthesized header (`# {title}` + `Section: {heading}`, `chunker.py:144`). A chunk torn out of a note loses the note-level context that makes it findable ("the ratio drops to 0.6 after week three" — of what?). Anthropic-style Contextual Retrieval fixes this by prepending a short LLM-generated, chunk-specific context to each chunk before indexing. Earlier ideas (reusing top-of-note callouts) were rejected: replicated static text distorts BM25 (IDF dilution, length normalization) and depends on a human convention. Generated context is chunk-unique, so it feeds **both** the embedding and BM25 channels safely.

The one-line architectural shift: composed entry text stops being a pure function of the note on disk and becomes note + a persisted generated artifact. Everything below follows from that.

**Scope**: contextual retrieval only. No hierarchical/auto-merging retrieval, no multi-resolution, no granularity-default changes (follow-up decisions, gated on eval results).

## Settled design decisions

1. **Opt-in**: `index.contextual: false` default in `settings.py` DEFAULTS (user decision). Ordinary sync makes zero chat calls until enabled.
2. **Backfill via `sync --contextualize`** (user decision): widens the "needs update" set to include multi-section notes lacking context. Resumable by re-running.
3. **One LLM call per note**, not per section: note text in, JSON array of N contexts out (client has no prompt caching, `openrouter.py:224`). Parse with existing `parse_llm_json` (`synthesis/answer.py`).
4. **Sections only**: `::doc` entries never get context (self-referential). `document_text()` untouched.
5. **Skip single-section notes** (default): section ≈ note, title already prepended; ~74% of a realistic vault. Threshold configurable.
6. **Two caches in series**: `section_hash` (sha256 of bare section text) → context; existing `entry_hash` (sha256 of composed text) → embedding. Cache on `section_hash` alone; accept mild staleness; `--refresh-context` escape hatch.
7. **Empty context composes byte-identical text to today** (omit the line, never emit blank). Shipping re-embeds nothing; partial coverage is a valid state, not a corrupt one.
8. **Degraded, not fatal**: generation failure → index section without context, warning in sync output, later sync retries. Generation happens in the existing "fallible provider work before delete" phase (`store.py:340-344`).
9. **Model provenance**: `context_model` in collection metadata. Mismatch → **warning** in sync result (not the hard error used for `embedding_model` — stale context degrades, mixed embedding spaces corrupt).
10. **`chunker.py` stays deterministic and LLM-free** — boundaries, line ranges, `chunk_id`s unchanged, so golden eval labels stay valid and A/B runs on identical labels.
11. Context text goes into the single stored document string (embeddings + BM25 both see it). Splitting embed-text from tokenize-text is a measured follow-up only if BM25 precision degrades.

## Implementation

### 1. New module: `vault_spider/index/contextualizer.py`

- `section_hash(text: str) -> str` — sha256 of bare section text.
- `generate_contexts(provider, note, sections, *, model=None) -> tuple[dict[str, str], list[str]]` — returns `{section_hash: context}` + warnings. One `provider.chat()` call; system prompt asks for a JSON array of exactly N strings, each 1–2 sentences situating that section within the note, ≤ `CONTEXT_CONFIG["max_chars"]`; strictly descriptive, treats note as untrusted content (mirror the posture of `planner.py:52`). Length-mismatched/unparseable reply → `({}, [warning])`. Enforce the char cap by truncation post-parse.
- Prompt sends note title + full body (cap ~16k chars) and the numbered section list (heading + first ~200 chars each) so the model aligns array positions to sections.

### 2. Tuning constants: `vault_spider/config.py`

`CONTEXT_CONFIG = {"max_chars": 300, "min_sections": 2, "note_char_limit": 16000}`.

### 3. Settings: `vault_spider/settings.py` + `config.yaml.example`

- Add `"contextual": False` to `DEFAULTS["index"]` (validator rejects unknown keys, so this is required).
- Accessor `contextual_enabled() -> bool`.
- Document in `config.yaml.example` under `index:` (opt-in, cost implications, backfill command).
- `.env.example`: `OPENROUTER_CONTEXT_MODEL` (optional; defaults to chat model). Wire in `OpenRouterClient.from_env` as `context_model` attribute, resolved `context_model or chat_model` at call time.

### 4. Composition: `vault_spider/corpus/chunker.py` (minimal touch)

`section_text(note, section, context: str = "")` — when context is non-empty, emit `Context: {context}` on its own line after the `Section:` line. Empty context → byte-identical current output (invariant 7). No other changes to this file.

### 5. Store: `vault_spider/index/store.py`

- `_entries_for_note(note, contexts: dict[str, str])` — for each section compute `section_hash`, look up context, pass to `section_text`; add `section_hash` and `context` to section metadata (context may be `""`).
- In `sync()`:
  - Harvest step (`store.py:270-284`): alongside `reusable` embeddings, build `reusable_contexts[section_hash] = context` from old section metadata before delete.
  - For each note needing entries and eligible (contextual enabled, `len(sections) >= min_sections`): resolve contexts from `reusable_contexts`; if any section misses and generation is enabled, call `generate_contexts` once for the note; merge; failures append to `warnings`.
  - `--contextualize` path: new `contextualize: bool = False` param; when set, notes that are otherwise `unchanged` but have ≥ min_sections sections and any section entry with empty/missing `context` metadata are promoted into the update set (their doc-entry embeddings are reused via the existing `entry_hash` harvest; only recomposed sections re-embed).
  - `refresh_context: bool = False` param: skip `reusable_contexts`, regenerate for all eligible notes in the update set, and force all eligible notes into the update set.
  - Sync result dict gains `contexts_generated` / `context_warnings` counts.
- Collection metadata: add `context_model` in `_collection_metadata()`; on load, mismatch with current model → warning surfaced in next sync result (no hard error, invariant 9).
- Respect the existing safety invariant: all chat + embed calls complete before `collection.delete`.

### 6. CLI: `vault_spider/cli.py`

`cmd_sync` + parser (`cli.py:1000-1010`): add `--contextualize` and `--refresh-context` flags, pass through to `store.sync`. `--refresh-context` implies `--contextualize`. Both refused with `--dry-run`? No — dry-run should predict them (report `would_contextualize` note count) without calling the LLM. Update the sync help strings and the command manifest (`cli.py:77`).

### 7. Display seams

- `vault_spider/web/format.py:18-22` — add `Context` to the `SYNTHETIC_PREFIX_RE` alternation (`(?:Path|Tags|Date|Section|Context):`), or previews open with generated context instead of the note's words.
- `evidence.py` excerpt: no change (context sits inside the 700-char head; acceptable, cap is 300).

### 8. Tests

- `tests/conftest.py` `FakeProvider`: record `chat_calls` (list of prompts); settable `context_response`.
- New `tests/test_contextualizer.py`: prompt includes all sections; happy-path parse; wrong-length array → empty + warning; junk JSON → empty + warning; truncation to max_chars; single-section note skipped.
- `tests/test_store_sync.py` additions:
  - contextual disabled (default) → zero chat calls, metadata `context == ""`, composed text byte-identical to current fixtures.
  - enabled: contexts stored in section metadata; `section_hash` present.
  - note edited, one section changed → context reused for unchanged sections (no second chat call for them), regenerated only for changed one — assert via `chat_calls`.
  - generation failure (chat raises) → sync succeeds, sections indexed with empty context, warning present; next sync with working chat fills them via `--contextualize`.
  - `--contextualize` on an already-synced vault: unchanged multi-section notes get contexts, doc embeddings reused (assert `embed_calls` excludes doc texts), single-section notes untouched.
  - `--refresh-context` regenerates despite cache.
- `tests/test_chunker.py`: `section_text` with/without context; empty-context identity.
- `tests/test_web_format.py`: `Context:` line stripped from previews.

### 9. Docs

`AGENTS.md` architecture list (corpus/index sections): note the contextualizer module, the two-hash cache, the opt-in setting, the backfill flag.

## Verification

1. `uv run pytest` — full suite green (network-free via FakeProvider).
2. Upgrade no-op proof: existing test `test_second_sync_is_noop` must still pass unmodified with contextual disabled; add the same assertion with contextual *enabled* against a vault synced *before* enabling (no re-embeds until backfill).
3. Manual eval A/B (user-run, needs real `OPENROUTER_API_KEY`; labels valid across the change per invariant 10):
   ```
   ./bin/vault-spider sync --root eval-realistic/corpus --reset
   ./bin/vault-spider eval ... --granularity mixed   # baseline; record mean_ndcg_at_k, mean_group_recall_at_k, mrr
   # enable index.contextual in config.yaml
   ./bin/vault-spider sync --root eval-realistic/corpus --contextualize
   ./bin/vault-spider eval ... --granularity mixed   # variant, same labels
   ```
   Repeat for `eval/public_vault`. Decision gates: `mean_group_recall_at_k` drop → inspect generated contexts; BM25-driven precision drop on short sections → follow-up to split embed-text from tokenize-text (~20 lines in `store.py` `_tokenize` path).

## Non-goals (explicit)

- No hierarchical / auto-merging / multi-resolution retrieval.
- No granularity default changes (web UI stays `document`) — follow-up gated on eval.
- No doc-entry windowing or length caps; no `embed_texts` length guard (separate small fix).
- No enrich-planner rework (`_add_focused_section_excerpts` stays).

Branch: `claude/chunking-implementation-etk94b`; commit and push there when done.
