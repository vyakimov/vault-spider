# Contextual Chunking v1 — Eval Run Record

Retrieval-stage A/B/C evaluation on the public `eval/` corpus, executed per
[`docs/contextual-chunking-eval-execution-plan.md`](../../../docs/contextual-chunking-eval-execution-plan.md).

**Analysis: [comparison.md](comparison.md).**

## Code Under Test

| arm | commit | worktree |
|---|---|---|
| original implementation | `5c78cf329bdb85d26a13bfdba73de5cc9f533a43` (`main`) | `../vault-spider-original-eval` |
| smarter chunking (both arms) | `a6beab343a86ab79ca7aefb0dca9ccf26908c5e6` (`feature/contextual-chunking`) | primary |

Eval inputs were verified identical between the two commits:

```bash
git diff --quiet main...feature/contextual-chunking -- \
  eval/public_vault eval/dataset.yaml eval/golden_queries.jsonl   # clean
```

Pre-commit gates on the feature commit: `ruff` clean, `pytest` 585 passed, `pyright` 0 errors,
`git diff --check` clean.

## Models

Identical across all runs (verified from the `run` block of each result file):

- embedding: `qwen/qwen3-embedding-8b`
- rerank: `cohere/rerank-4-pro`

## Corpus

- notes: 240
- queries: 44 (38 answerable, 6 unanswerable)
- labeled notes: 35, distractor notes: 205
- index entries: 1378 in every variant (240 document + 1138 section)

## Summary Generation

- 240 manual summary jobs under `eval/context-data/jobs/`, imported all-or-nothing.
- `generated_by: claude-code`; `generator_model` not recorded by the generating process.
- Audit before import: 240 files, all summaries non-empty and within the 1,200-character contract,
  no note body / note ID / fingerprint / title / schema field altered.
- `context status` gate: `ready_count 240`, `missing_count 0`, `stale_count 0`, `coverage 1.0`.
- Contextual sync envelope: `source manual`, `missing_notes 0`, `stale_notes 0`, `failed_notes []`,
  `coverage 1.0`, `summary_hits 240`, `ready_sections 1138`.
- No OpenRouter chat calls were made for summary generation. Sync did call the embedding provider,
  since summary-enriched text needs new vectors.

## Fixed Experiment Settings

`dataset eval`, `stage retrieval`, `mode thorough`, `granularity mixed`, `n 10`, `k 5`,
collection `vault_notes`, corpus `eval/public_vault`.

## Results

| file | run timestamp (UTC) | nDCG@5 | recall@5 | complete@5 | MRR |
|---|---|---|---|---|---|
| [original-main.json](original-main.json) | 2026-07-29T23:13:34Z | 0.6883 | 0.8640 | 0.7632 | 0.6998 |
| [smarter-chunking.json](smarter-chunking.json) | 2026-07-29T23:26:48Z | 0.5079 | 0.7193 | 0.5789 | 0.4948 |
| [smarter-plus-context.json](smarter-plus-context.json) | 2026-07-29T23:38:47Z | 0.5422 | 0.7675 | 0.6579 | 0.5453 |
| [smarter-chunking-rerun.json](smarter-chunking-rerun.json) | 2026-07-29T23:39:31Z | 0.5070 | 0.7193 | 0.5789 | 0.4948 |

`smarter-chunking-rerun.json` is a variance check against the same index, not a fourth variant. It
confirms the Δ1 regression is deterministic rather than reranker noise.

### Section-granularity ablation

Added 2026-07-30. Same three indexes, `--granularity section` instead of `mixed`, which bypasses the
new `_mixed_fusion` path (`searcher.py:131`). No re-embedding; only the retrieval path differs.

| file | run timestamp (UTC) | nDCG@5 | recall@5 | complete@5 | MRR |
|---|---|---|---|---|---|
| [section-original-main.json](section-original-main.json) | 2026-07-30T07:18:35Z | 0.6781 | 0.8377 | 0.7368 | 0.6989 |
| [section-smarter-chunking.json](section-smarter-chunking.json) | 2026-07-30T07:17:38Z | 0.5417 | 0.7281 | 0.6316 | 0.5524 |
| [section-smarter-plus-context.json](section-smarter-plus-context.json) | 2026-07-30T07:18:12Z | 0.5537 | 0.7149 | 0.5789 | 0.5946 |

Findings: `_mixed_fusion` accounts for only ~24% of the Δ1 nDCG regression, and the Δ2 summary
benefit does not survive — group recall −1.8% and complete rate −8.3% on this stack. See the
Addendum in [comparison.md](comparison.md).

## Exact Commands

Original arm, from `../vault-spider-original-eval`:

```bash
VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider sync \
  --root eval/public_vault \
  --reset \
  --chroma-path /Users/vy/Documents/Development/vault-spider/eval/context-data/chroma-original

VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider eval run \
  --dataset eval \
  --chroma-path /Users/vy/Documents/Development/vault-spider/eval/context-data/chroma-original \
  --stage retrieval --mode thorough --granularity mixed -n 10 --k 5 \
  --out /Users/vy/Documents/Development/vault-spider/eval/results/contextual-chunking-v1/original-main.json
```

Smarter arm, from the primary worktree:

```bash
VAULT_SPIDER_CONFIG=eval/eval-config.yaml ./bin/vault-spider sync --reset

VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider eval run \
  --dataset eval --stage retrieval --mode thorough --granularity mixed -n 10 --k 5 \
  --out eval/results/contextual-chunking-v1/smarter-chunking.json
```

Contextual arm, from the primary worktree:

```bash
VAULT_SPIDER_CONFIG=eval/eval-contextual-config.yaml ./bin/vault-spider context import
VAULT_SPIDER_CONFIG=eval/eval-contextual-config.yaml ./bin/vault-spider context status
VAULT_SPIDER_CONFIG=eval/eval-contextual-config.yaml ./bin/vault-spider sync --reset

VAULT_SPIDER_CONFIG=eval/eval-contextual-config.yaml \
./bin/vault-spider eval run \
  --dataset eval --stage retrieval --mode thorough --granularity mixed -n 10 --k 5 \
  --out eval/results/contextual-chunking-v1/smarter-plus-context.json
```

## Local Artifacts (not committed)

Chroma indexes and canonical summaries stay under gitignored `eval/context-data/`:

```text
eval/context-data/
├── chroma-original/      original-main.json
├── chroma-baseline/      smarter-chunking.json + rerun
├── chroma-contextual/    smarter-plus-context.json
├── jobs/                 240 manual summary jobs
└── summaries/            240 imported canonical summaries
```

They are preserved for reproducibility. The only edit made to the committed JSON was normalizing
`dataset.path` to `eval/dataset.yaml` and `dataset.corpus_root` to `eval/public_vault`; metrics, run
settings, query scores, timestamps, and model identifiers are untouched.
