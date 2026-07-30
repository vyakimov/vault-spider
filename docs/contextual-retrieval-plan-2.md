# Contextual Retrieval Chunking for vault-spider (plan 2)

> Independently drafted alternative to [contextual-retrieval-plan.md](contextual-retrieval-plan.md). The two plans agree on the core (opt-in, sections only, context in the single stored document string for both embeddings and BM25) but differ on batching (per-section vs per-note LLM calls), failure policy (abort vs degrade), and cache keying (note content hash vs section hash). Kept side by side for comparison.

## Context

vault-spider indexes an Obsidian vault into ChromaDB + in-memory BM25 hybrid search. Today each section chunk is embedded with only a thin synthesized header (`# {title}\n\nSection: {heading}\n\n{body}` — `vault_spider/corpus/chunker.py:144`). Chunks lose the surrounding note's context, which hurts retrieval for sections that only make sense inside their note (pronouns, implicit subjects, follow-up sections).

**Goal**: adopt Anthropic-style *contextual retrieval*: at index time, each section chunk gets a short LLM-generated snippet situating it within the whole note. The snippet is prepended to the chunk text for **both** embedding (contextual embeddings) and the stored document BM25 tokenizes (contextual BM25). Opt-in via config (defaults off) because it adds one LLM call per section.

## Design decisions

- **Sections only** — the `::doc` entry already *is* the whole note; contextualizing it doubles cost for no benefit.
- **Context lives in the composed text** as a single synthetic header line `Context: ...` (one line is load-bearing — the display strip regexes are line-based), plus a `context` metadata field for inspection.
- **Cache key includes `note.content_hash`** — any note edit regenerates all its sections' contexts (correct "situate in the *current* document" semantics). Unchanged notes never re-call the LLM.
- **Failure policy: abort the sync** (same semantics as an embedding failure — old index stays intact, `store.py:340-347` invariant). Contexts already generated survive in a write-through cache so retries are cheap. No silent fallback to context-free chunks.
- **Collection version marker** mirrors the `embedding_model` mismatch guard: toggling the feature, changing model, or bumping the prompt version forces `sync --reset`.

## Implementation steps

### 1. Config (`vault_spider/settings.py`, `config.yaml.example`)

Flat keys inside the existing `index` section (the strict unknown-key check at settings.py:95 only validates top-level section keys and shallow-merges, so a nested block would bypass validation):

```python
"index": {
    "chroma_path": "chroma_db",
    "contextual_enabled": False,
    "contextual_model": None,        # None -> provider.chat_model
    "contextual_max_tokens": 120,
},
```

Accessors `contextual_enabled()`, `contextual_model()`, `contextual_max_tokens()` in the style of `chroma_path()`. Document in `config.yaml.example` (cost note; toggling requires `sync --reset`).

### 2. JSON-mode opt-out (`vault_spider/llm/openrouter.py`)

`chat(...)` gains `json_response: bool = True`; when False, omit `response_format` from the payload (openrouter.py:240). Existing callers unchanged.

### 3. New module `vault_spider/index/contextualizer.py`

- `CONTEXT_PROMPT_VERSION = 1`, `MAX_CONTEXT_CHARS = 600`, `MAX_DOCUMENT_CHARS = 24000` (truncate huge note bodies).
- `ContextualConfig` frozen dataclass (`enabled`, `model`, `max_tokens`) with `from_settings()`.
- `Contextualizer(provider, config, cache)` with `context_for(note, raw_section_text) -> str`: cache-first; on miss calls `provider.chat(..., temperature=0.0, json_response=False, model=config.model)` with Anthropic's contextual-retrieval prompt (whole note in `<document>`, chunk in `<chunk>`, "give a short succinct context to situate this chunk... for search retrieval, answer with the context only"). Post-process: collapse whitespace to one line, strip quotes, truncate. Empty result is allowed (entry indexed without a Context line); provider errors propagate.
- Cache key: `sha256` over `(prompt_version, model, note.content_hash, sha256(section_text))`.

### 4. New module `vault_spider/index/context_cache.py`

Clone the `QueryEmbeddingCache` pattern (`vault_spider/retrieval/query_cache.py`): JSON file at `<chroma_path>/context_cache.json`, atomic `os.replace`, ts pruning, `max_entries=50_000`. Payload `{"prompt_version": 1, "entries": {key: {"context", "ts"}}}`. `put` is write-through so an aborted sync keeps everything generated so far.

### 5. Text composition (`vault_spider/corpus/chunker.py`)

```python
def section_text(note, section, context: str = "") -> str:
    # header gains "Context: {context}\n" when non-empty; byte-identical
    # to today's output when context == ""
```

Plus `CONTEXT_LINE_RE` and `strip_context_line(text)` helper (chunker owns the composed-text format). `document_text` unchanged.

### 6. `IndexStore` (`vault_spider/index/store.py`) + `cli.py`

- Constructor: `contextual: Optional[ContextualConfig] = None` (None → `from_settings()`); build `self.contextualizer` only when enabled. Existing call sites need no changes.
- `_collection_metadata()` gains `"contextual"` marker: `"off"` or `f"v{CONTEXT_PROMPT_VERSION}:{model}"`. `_load_or_create_collection()` raises on mismatch (missing key ⇒ `"off"`) with a `sync --reset` message, honoring `allow_model_mismatch`.
- **Companion fix**: `cli.py` never passes `allow_model_mismatch`, so `sync --reset` currently dead-ends at construction on any marker mismatch (latent bug for `embedding_model` today). Thread `allow_model_mismatch=args.reset` through `get_store`.
- Sync flow: contextualization must NOT run in `_entries_for_note` (it runs during the diff loop and under `dry_run`). New `_apply_contexts(notes_by_id, entries)` step between the dry-run return (store.py:295) and embedding resolution (store.py:309): for each `granularity == "section"` entry, fetch/generate context, recompose via `section_text(note, section, context)`, set `metadata["context"]`, recompute `entry_hash` over the final text. Carry the raw section text internally through `_entries_for_note` (drop before `collection.add`). Add `contexts_generated`/`contexts_cached` counts to the sync result.
- Ordering preserved: diff → dry-run return → **contexts (fallible)** → embeddings (fallible, entry-hash reuse works unchanged since it hashes final text) → delete → add.

### 7. Display/excerpt leak

- `vault_spider/web/format.py:19` — add `Context` to `SYNTHETIC_PREFIX_RE` alternation.
- `vault_spider/retrieval/evidence.py:66` — `excerpt = strip_context_line(document)[:EXCERPT_CHARS]`: the Context line is LLM prose, not note text; synthesis must not cite it as vault content.

### 8. Tests

- `tests/conftest.py` `FakeProvider`: `chat` gains `json_response=True` + `chat_calls` recording; when `json_response is False` return a deterministic snippet derived from md5(user_prompt).
- `tests/test_store_sync.py` (store built with explicit `ContextualConfig(enabled=True, ...)`):
  - sections get `Context:` line + `context` metadata; `::doc` entries don't
  - second sync ⇒ `chat_calls == []` and `embed_calls == []`; fresh store over same chroma_path ⇒ still no chat calls (cache persistence)
  - editing one note ⇒ chat calls only for its sections
  - chat failure ⇒ sync raises, collection intact; partial cache survives for retry
  - marker mismatch (off→on) ⇒ ValueError mentioning `sync --reset`; `allow_model_mismatch=True` passes
  - `dry_run=True` makes zero chat calls
- `tests/test_chunker.py` (`section_text(context=)`, `strip_context_line`), `tests/test_web_format.py`, `tests/test_evidence.py`, `tests/test_settings.py` (new defaults + unknown-key rejection), `tests/test_openrouter.py` (`json_response=False` omits `response_format`).
- All existing tests pass unchanged with the feature off.

### 9. Docs

- `AGENTS.md`: metadata list (add `context`), `index.contextual_*` keys, abort-on-failure + reset-on-toggle rules.
- Regenerate `docs/codebase-map.{json,html}` via `uv run tools/build_codebase_map.py` (two new modules; CI fails if stale).
- `evaluation/` untouched — context never alters splitting, headings, or line ranges, so `dataset.py:147` label validation is unaffected.

## Verification

1. `uv run pytest -q`, `uv run ruff check .`, `uv run pyright vault_spider` — all green, network-free.
2. Smoke: enable `contextual_enabled: true` in a scratch config, `sync --reset` a small vault twice — second run reports `contexts_generated: 0`; `retrieve` excerpts show no `Context:` line; raw Chroma documents do.
3. Optional eval A/B (`eval/` and `eval-realistic/` harnesses): compare retrieval metrics with the feature off vs on (fresh `sync --reset` each) — the go/no-go signal for recommending it as a default.

## Risks

- One edited line in a many-section note regenerates all that note's contexts (and likely re-embeds them). Price of correct semantics; bounded by opt-in + per-note incrementality.
- Initial sync of a large vault is one serial chat call per section; the write-through cache makes interruption safe. Parallelism is a follow-up.
- Chat models aren't bitwise deterministic even at temperature 0 — the cache, not the model, guarantees no-op re-syncs.
