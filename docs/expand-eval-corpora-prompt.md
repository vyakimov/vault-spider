# Task: substantially expand the vault-spider evaluation corpora

Repo: `/Users/vy/Documents/Development/vault-spider` (Python 3.12, `uv`).

Read `AGENTS.md` and `eval/README.md` before touching anything. `AGENTS.md` is the canonical
description of this codebase; `eval/README.md` describes the benchmark you are extending.

## Why this is needed

The eval runs at `--granularity mixed`, which searches the **section** pool. Retrieval builds its
candidate set from the top 150 semantic hits ∪ the top 150 BM25 hits (`top_k = 150` in
`vault_spider/config.py`), so the pool is at most ~300 distinct entries and usually fewer.

Current corpus sizes:

| corpus | notes | section entries | sections/note |
|---|---|---|---|
| `eval/public_vault` | 36 | 138 | 3.8 |
| `eval-realistic/corpus` | 57 | 114 | 2.0 |

**Both section pools are smaller than `top_k`.** Every section of every note is a candidate on
every query. That means the benchmark cannot measure retrieval *reach* at all — only reordering.
Any change whose value is "find evidence that scoring alone would not have reached" is untestable
here, and a recent graph-expansion experiment failed to measure for exactly this reason (see
`docs/graph-augmented-retrieval-report.md`, section d.2).

**Target: at least ~900 section entries per corpus**, i.e. roughly 3× the candidate pool, so a
query's evidence can plausibly fall outside it. At current section density that is ~240 notes for
`public_vault` and ~450 for `eval-realistic/corpus`.

Do **not** hit the section number by inflating headings per note. The realistic corpus is
deliberately heading-light (that is what its `headingless` slice tests). Add notes, not headings.

## Scope

Two phases. **Do phase 1 completely, validate, re-baseline, and report before starting phase 2.**

### Phase 1 — distractor notes only, no new queries

This is the high-value, low-risk bulk of the work, and there is precedent: the corpora were grown
this way on 2026-07-19 (public 26 → 36 notes, distractors only, queries unchanged).

- Add notes until each corpus reaches the section target.
- **Change no existing note's path, title, or heading text.** Every golden label is keyed on
  `path` + `heading`; renaming anything silently invalidates labels.
- Add no new labelled queries in this phase. The only manifest change is `expected_note_count`.

### Phase 2 — new labelled queries for the gaps

Roughly 15–25 new queries per corpus, targeting what the current sets do not cover:

1. **`known_item` regressions.** Single unambiguous answer, correct note at rank 1. The graph
   experiment did its damage here and nothing was watching. These are cheap to write and are the
   canary for any change that reorders results.
2. **Genuine note-level reach.** Evidence living in a note with *zero* lexical overlap with the
   query, reachable only because a retrieved note links to it. Model these on realistic q031: the
   query says "retention", the target note never uses the word, and the link carries you there.
   These are the queries that make reach measurable — write several, in both corpora.
3. **Section selection within a reached note.** The right note ranks top-5 but at the wrong
   heading. Public q023 is accidentally this shape; make it deliberate and labelled, because it
   is a distinct failure mode from reach and the two are currently conflated.
4. **Deep-tail evidence.** Now that the corpus exceeds the candidate pool, write queries whose
   evidence sits in the tail — the cases that were literally impossible to express before.

## Corpus conventions — follow these exactly

### `eval/public_vault` (fictional field-station domain: Atlas, Mercury, Garden, Research)

- Frontmatter ids: `01JEV0000000000000000000NN`, 26 chars, sequential. Continue from the highest
  existing value. **Every note needs an explicit `id`** — a note without one falls back to a path
  hash that changes on rename (`000 Daily Notes/2026-07-13.md` in the realistic corpus is the
  existing offender; do not add more).
- Timestamps: `utc_z`, e.g. `created: 2024-01-12T09:00:00Z`.
- Full frontmatter shape: `id`, `title`, optional `aliases: [...]`, `type`, `created`, `updated`,
  `tags: [...]`.

### `eval-realistic/corpus` (messy personal-vault style: homelab, papertrail, Larder, book notes)

- Frontmatter ids: per-cluster ULID prefixes already in use — `01M6A`…`01M6J`. Extend an existing
  cluster's range for a note in that cluster, or open a new prefix for a new cluster.
- Timestamps: `obsidian_local`, naive local time, e.g. `updated: 2026-06-02T08:56:23` (no `Z`).
- Style is deliberately inconsistent: some notes headingless, some with an H1, terse fragments,
  inline code, occasional profanity in note titles. **Match the existing voice** — a corpus of
  uniformly tidy notes would not test what this one exists to test.

### Both

- Fully synthetic and public-safe. No real hostnames, IPs, employers, or people. No content
  copied or paraphrased from a private vault. This is a committed, publishable corpus.
- **Never touch `eval-live/`** — it is gitignored and derived from real notes.
- Notes under `Templates/`, `.trash/`, `.obsidian/`, any dot-directory, anything tagged `#ignore`
  or `#secret`, and `*.excalidraw.md` are skipped by the loader. Do not rely on them.

## Distractor quality bar

This is where the work succeeds or fails. Volume alone is worthless.

- **Same-domain confusables, not filler.** A good distractor ranks top-3 for an existing query and
  is *not* gold. That taxes nDCG without touching completeness, which is what makes a benchmark
  discriminating. Lorem-ipsum padding inflates the entry count and measures nothing.
- **A distractor must never accidentally answer an existing query.** If it does, the labels become
  wrong rather than harder. Check each new note against the existing query set.
- **Link them realistically.** Wikilinks are a live retrieval signal in this project. Produce a
  realistic mix: a few hubs/MOCs linking many notes, chains of 2–3, plenty of leaves, and some
  genuine orphans. A corpus where every note is linked is as unrealistic as one where none are.
  `lint` reporting some orphans is expected and documented.
- Spread across the existing folder structure rather than dumping into one directory.

## Golden query file format — exact, and easy to get wrong

`golden_queries.jsonl`, one JSON object per line:

```json
{"id": "q031", "query": "...", "answerable": true, "category": "multi_note",
 "slices": ["complete_evidence", "homelab"],
 "relevant_evidence": [{"note_id": "01M6C000000000000000000003", "path": "200 Tech/Larder/Plan — Flask HTMX.md", "heading": "Plan — Flask HTMX", "grade": 3}],
 "required_evidence_groups": [["01M6C000000000000000000003#Plan — Flask HTMX"]],
 "gold_facts": ["..."], "forbidden_facts": ["..."]}
```

- **`eval/golden_queries.jsonl` uses compact separators** (`{"id":"q003","query":...}`, no spaces).
  **`eval-realistic/golden_queries.jsonl` uses spaced separators** (`{"id": "q031", ...}`). Match
  the file you are editing — a whitespace-only reformat of untouched lines makes the diff
  unreviewable.
- Both files are raw UTF-8 (`ensure_ascii=False`): em dashes appear literally as `—`, never as
  `—`. Note that `200 Tech/Larder/Plan — Flask HTMX.md` uses an em dash, not a hyphen.
- `heading` must match what `split_sections` produces (H1–H3). A headingless note's section has
  `heading: ""` and its group entry is `"<note_id>#"`. Verify rather than assume:
  ```bash
  uv run python -c "
  from vault_spider.corpus.loader import load_notes
  from vault_spider.corpus.chunker import split_sections
  n = {x.path: x for x in load_notes('eval-realistic/corpus')}['PATH HERE']
  print(n.note_id, [s.heading for s in split_sections(n)])"
  ```
- `grade` is 1–3; 3 means essential. `required_evidence_groups` is a list of groups, each a list
  of interchangeable members — a query is complete@k only when every group has a member in the
  top k.
- Reuse the existing `category` and `slices` vocabulary where it fits; invent sparingly.
- Update `expected_note_count` and `expected_query_count` in each `dataset.yaml`.

## Verification — required, after every batch

```bash
cd /Users/vy/Documents/Development/vault-spider
VAULT_SPIDER_CONFIG=eval/eval-config.yaml ./bin/vault-spider eval validate --dataset eval
VAULT_SPIDER_CONFIG=eval-realistic/eval-config.yaml ./bin/vault-spider eval validate --dataset eval-realistic
uv run pytest
```

`eval validate` cross-checks every label against the corpus — paths, note ids, headings, group
membership, expected counts — and fails with `contract_violation` on drift. It needs no API key.
It must return `"valid": true` with an empty `warnings` array. Do not hand back work that does not.

Also confirm the saturation problem is actually fixed:

```bash
uv run python -c "
from vault_spider.corpus.loader import load_notes
from vault_spider.corpus.chunker import split_sections
for root in ('eval/public_vault','eval-realistic/corpus'):
    notes = load_notes(root)
    secs = sum(len(split_sections(n)) for n in notes)
    print(f'{root}: {len(notes)} notes, {secs} sections  (need >= ~900)')"
```

### Re-baselining (needs an API key — ask before spending)

Growing the corpora **will move the recorded baselines**, which is expected and is the point. Do
not re-run the scored eval without checking first — it costs real embedding and rerank calls.
When cleared to run it, use an isolated Chroma path, never the live-vault index:

```bash
./bin/vault-spider --chroma-path /tmp/eval-expand sync --root eval/public_vault --reset
./bin/vault-spider --chroma-path /tmp/eval-expand eval run --dataset eval \
  --mode thorough --granularity mixed --k 5 --out /tmp/public-new.json
```

Record the new numbers in `eval/README.md` and note that they supersede the previous ones. Stale
baselines quoted as acceptance gates have already caused one wasted experiment.

## Constraints

- **Do not change any code under `vault_spider/`.** This is corpus and label work only. If you
  believe a loader or scorer change is required, stop and say so instead.
- Do not modify existing notes, queries, paths or headings except to add new ones.
- Do not commit. Leave everything in the working tree.
- Check `git branch --show-current` first. Branch `graph-augmented-retrieval` carries eval changes
  that `main` does not: graph slices on public q003/q010/q023 and realistic q017, a new realistic
  q031, and `expected_query_count: 31`. On `main` those are absent and the realistic count is 30.
  Confirm which base you are on before editing `dataset.yaml`, and say which you used.

## Report back

Notes added per corpus and where; before/after note and section counts; the `eval validate` output
for both datasets; `pytest` result; any label you had to touch and why; and anything you think is
wrong with this brief.
