# Recency, `rerank_top_k`, and a two-corpus baseline comparison

Supersedes [`../isolation-v1/README.md`](../isolation-v1/README.md), which in turn superseded
[`../contextual-chunking-v1/comparison.md`](../contextual-chunking-v1/comparison.md). Each earlier
round held a variable constant across every arm and was therefore blind to it. This round tests the
last of them: the recency boost.

All runs: `stage retrieval`, `mode thorough`, `granularity mixed`, `n 10`, `k 5`,
embedding `qwen/qwen3-embedding-8b`, rerank `cohere/rerank-4-pro`. Every result file records
`recency_boost_enabled` and `rerank_top_k` in its `run` block.

## 1. The recency boost is costly on both corpora

Original `main`, `rerank_top_k=30`:

| corpus | recency | nDCG@5 | recall@5 | complete@5 | MRR |
|---|---|---|---|---|---|
| `eval` (240 notes) | OFF | **0.8168** | 0.8904 | 0.7895 | **0.8860** |
| `eval` | ON | 0.6883 | 0.8640 | 0.7632 | 0.6998 |
| `eval-realistic` (649 notes) | OFF | **0.9193** | **0.9737** | 0.9474 | **0.9342** |
| `eval-realistic` | ON | 0.8584 | 0.9605 | 0.9474 | 0.8605 |

Disabling it is worth **+0.129 nDCG / +0.186 MRR** on `eval` and **+0.061 nDCG / +0.074 MRR** on
`eval-realistic`. It never helped any metric on either corpus.

This is a larger effect than anything in the contextual-chunking work, and it was on in every
measurement taken before this round.

## 2. `rerank_top_k` is a non-parameter once recency is off

New baseline with summaries, `eval`, recency OFF:

| `rerank_top_k` | 10 | 20 | 30 | 45 | 60 | 90 |
|---|---|---|---|---|---|---|
| nDCG@5 | 0.7774 | 0.7868 | 0.7770 | 0.7825 | 0.7912 | 0.7812 |
| recall@5 | 0.8772 | 0.8904 | 0.8904 | 0.9035 | 0.9035 | 0.9035 |

Flat, no trend, spread within run-to-run variance. Pool size stops mattering.

## 3. The pool-size regression was recency, not the reranker

The 2×2 that settles it (`eval`, new baseline with summaries, nDCG / recall):

| | recency OFF | recency ON |
|---|---|---|
| `rerank_top_k=30` | 0.7770 / 0.8904 | 0.6847 / 0.8904 |
| `rerank_top_k=60` | 0.7912 / 0.9035 | 0.5063 / 0.7456 |
| **30 → 60 delta** | **+0.0142 / +0.0131** | **−0.1784 / −0.1448** |

With recency off, a larger pool is marginally *better*. The entire penalty lives in the interaction,
so the reranker is not degrading on weaker candidates — it is being overridden.

Mechanism. With `rerank_use_ranks=True` the reranker's scores are discarded and replaced by
`1.0 - (position / (pool - 1)) * 0.5`, which always spans `[0.5, 1.0]` regardless of pool size. The
adjacent-rank gap is therefore `0.5 / (pool - 1)`: 0.0172 at pool 30, 0.0085 at pool 60. Recency
multiplies by `0.8 + 0.2 * factor` with `factor ∈ [1, 2]`, a fixed ~0.15 absolute swing at typical
relevance. Dividing swing by gap, recency can move a document ~9 positions at pool 30 and ~18 at
pool 60. Doubling the pool doubles recency's reach through the reranker's ordering.

Note the irony: the comment at `config.py:63` says ranks are used *"so recency can't amplify score
gaps that don't mean much."* The rank conversion does fix that, and introduces this — a rank scale
that silently depends on pool size.

## 4. With recency off, the feature work is net negative on both corpora

`rerank_top_k=30`, recency OFF, mixed:

### `eval` (240 notes)

| configuration | nDCG@5 | recall@5 | complete@5 | MRR |
|---|---|---|---|---|
| **original `main`** | **0.8168** | 0.8904 | 0.7895 | **0.8860** |
| new baseline, no summaries | 0.8082 | 0.8640 | 0.7632 | — |
| new baseline, with summaries | 0.7770 | 0.8904 | 0.7895 | 0.8202 |

### `eval-realistic` (649 notes)

| configuration | nDCG@5 | recall@5 | complete@5 | MRR |
|---|---|---|---|---|
| **original `main`** | **0.9193** | **0.9737** | **0.9474** | **0.9342** |
| new baseline, no summaries | 0.9038 (−0.0155) | 0.9474 (−0.0263) | 0.9211 (−0.0263) | 0.9132 |
| new baseline, with summaries | 0.8839 (−0.0354) | 0.9474 (−0.0263) | 0.9211 (−0.0263) | 0.8947 |

The ordering is identical on both corpora: **original > no summaries > with summaries.** The original
implementation wins or ties every metric in both.

Summaries cost ordering quality consistently: −0.031 nDCG on `eval`, −0.020 on `eval-realistic`. On
`eval` they bought +0.026 recall and +0.026 complete in exchange; on `eval-realistic` they bought
nothing — recall and complete are identical to the no-summaries arm, so the nDCG and MRR loss is
unpaid for.

This reverses `isolation-v1`, which found summaries worth +0.024 nDCG / +0.066 recall. That
measurement had recency ON, which was masking the comparison in the summaries' favour.

## Conclusions

1. **Ship `recency_boost_enabled=False`.** Largest, most consistent win measured, on both corpora.
   Consider whether the feature is worth keeping at all rather than just defaulting off.
2. **Do not ship the contextual-chunking work as a retrieval improvement.** Once recency is
   controlled for, it does not beat the baseline on either corpus. The summaries specifically make
   ranking worse for no reliable coverage gain.
3. **`rerank_top_k` needs no tuning** once recency is off. Leave it at 30.
4. The `rerank_use_ranks` normalization should be pool-size independent, or the recency weight should
   scale with the rank gap. As written the two features are coupled through a hidden constant.

## Caveats

- One run per cell except where noted; observed variance on repeated runs is ±0.01–0.02 nDCG. The
  ~0.015–0.035 gaps in section 4 are above that but not hugely, so "not shown to be better" is a
  fairer reading than "conclusively worse."
- `k=5`, mixed granularity, retrieval stage only. No synthesis judging.
- The recency sweep varied only `recency_boost_enabled`. `recency_weight` and `recency_decay_days`
  were left at 0.2 and 365 and were not swept.
- `eval-realistic` summaries were manual jobs stamped `generated_by: claude-code`, 649 files,
  imported at coverage 1.0, all within the 1,200-character contract.

## Tooling added

`eval run` now takes `--rerank-top-k N` and `--recency-boost` (recency defaults **off** for evals,
since it reweights on note dates and its value is a property of the corpus rather than of
retrieval). Both are recorded in every result file's `run` block so this class of hidden-variable
error cannot recur silently.
