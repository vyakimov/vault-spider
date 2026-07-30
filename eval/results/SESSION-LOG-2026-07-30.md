# Eval session log — 2026-07-30

Every eval run of this session, in order, with what was held constant and what varied. Written so the
reasoning is traceable later, including the three conclusions that turned out to be wrong and why.

**Read this first if you are about to trust a number from an earlier round.** Rounds 1–3 are
superseded. Their conclusions were artifacts of variables held constant across every arm.

---

## Constant across every run in this session

| setting | value |
|---|---|
| embedding model | `qwen/qwen3-embedding-8b` |
| rerank model | `cohere/rerank-4-pro` |
| stage | `retrieval` (no synthesis judging anywhere) |
| mode | `thorough` (reranker always active) |
| `n` (results returned) | 10 |
| `k` (metric cutoff) | 5 |
| collection | `vault_notes` |
| `semantic_weight` | 0.5 |
| `top_k` (per-retriever candidates) | 150 |
| `combine_strategy` | `rrf`, `rrf_k=60` |
| `rerank_use_ranks` | `True` until round 5, then bypassed by `score_geometry` |
| `recency_weight` | 0.2 (only used by `multiplicative`) |
| `recency_decay_days` | 365 |
| `contextual_bm25` | `false` everywhere — summaries never entered BM25 |

Corpora, both unchanged all session:

| dataset | notes | queries | answerable | unanswerable |
|---|---|---|---|---|
| `eval` (public) | 240 | 44 | 38 | 6 |
| `eval-realistic` | 649 | 44 | 38 | 6 |

Verified identical between `main` and the feature branch:
`git diff --quiet main...feature/contextual-chunking -- eval/public_vault eval/dataset.yaml eval/golden_queries.jsonl`

---

## Round 1 — original three-arm comparison (SUPERSEDED)

`eval/results/contextual-chunking-v1/`. Executed from `docs/contextual-chunking-eval-execution-plan.md`.

**Varied:** the implementation (original `main` `5c78cf3` → feature branch `a6beab3`), then summaries
on/off.
**Held constant, and this was the fatal flaw:** `rerank_top_k=60` on both feature arms vs `30` on the
original arm, and `recency_boost_enabled=True` everywhere.

| file | code | summaries | rerank_top_k | recency | granularity | nDCG | recall | complete | MRR |
|---|---|---|---|---|---|---|---|---|---|
| `original-main.json` | `5c78cf3` | — | 30 | ON | mixed | 0.6883 | 0.8640 | 0.7632 | 0.6998 |
| `smarter-chunking.json` | `a6beab3` | no | 60 | ON | mixed | 0.5079 | 0.7193 | 0.5789 | 0.4948 |
| `smarter-chunking-rerun.json` | `a6beab3` | no | 60 | ON | mixed | 0.5070 | 0.7193 | 0.5789 | 0.4948 |
| `smarter-plus-context.json` | `a6beab3` | yes | 60 | ON | mixed | 0.5422 | 0.7675 | 0.6579 | 0.5453 |

**Concluded (wrongly):** the chunking/retrieval rewrite regressed nDCG 26%. Summaries a partial
repair.
**Why wrong:** `rerank_top_k` differed between the original and feature arms and was never isolated.

---

## Round 2 — section-granularity ablation (SUPERSEDED)

Same directory, `section-*.json`. Bypasses `_mixed_fusion`, which only runs for `granularity=mixed`.

**Varied:** granularity `mixed` → `section`, same three indexes, no re-embedding.
**Held constant:** `rerank_top_k=60` on feature arms, recency ON everywhere — the same blind spot.

| file | code | summaries | rerank_top_k | recency | nDCG | recall | complete | MRR |
|---|---|---|---|---|---|---|---|---|
| `section-original-main.json` | `5c78cf3` | — | 30 | ON | 0.6781 | 0.8377 | 0.7368 | 0.6989 |
| `section-smarter-chunking.json` | `a6beab3` | no | 60 | ON | 0.5417 | 0.7281 | 0.6316 | 0.5524 |
| `section-smarter-plus-context.json` | `a6beab3` | yes | 60 | ON | 0.5537 | 0.7149 | 0.5789 | 0.5946 |

**Concluded (wrongly):** mixed fusion causes only 24% of the regression; the summary benefit does not
survive.
**Why wrong:** this ablation appeared to exonerate the retrieval code precisely because the real cause
(`rerank_top_k`) was present on both sides of it too.

### `combine(max)` scoring fix, measured here

`fixed-*.json`. **Varied:** only the routed-child score transform in `_mixed_fusion`
(`dot+1` → `exp(-(2-2cos))+1`). Indexes unchanged.

| file | nDCG | vs buggy |
|---|---|---|
| `fixed-smarter-chunking.json` | 0.5075 | −0.0004 |
| `fixed-smarter-plus-context.json` | 0.5422 | 0.0000 |

Ranking-inert: both transforms are monotonic in cosine and everything downstream consumes rank order.
Kept anyway — the inflated value was reported to callers as the `semantic` score.

---

## Round 3 — per-feature isolation (SUPERSEDED)

`eval/results/isolation-v1/`. One branch per variable off `exp/base`.

**Varied:** exactly one feature per branch.
**Held constant:** `rerank_top_k=30` everywhere (the round-1 flaw fixed), **recency ON everywhere**
(the next blind spot).

| branch | feature added | granularity | nDCG | recall | complete | MRR |
|---|---|---|---|---|---|---|
| `exp/base` | none (markdown-it chunker, dead weighted RRF, typing) | mixed | 0.6738 | 0.8377 | 0.7368 | 0.6954 |
| `exp/provenance-preamble` | provenance header | mixed | 0.6709 | 0.8246 | 0.7105 | 0.6925 |
| `exp/note-summary` | per-note summary | mixed | 0.6976 | 0.9035 | 0.8158 | 0.7022 |
| `exp/mixed-mode` | document routing | mixed | 0.6891 | 0.8377 | 0.7368 | 0.7020 |
| `exp/base` | none | section | 0.6771 | 0.8509 | 0.7632 | 0.6902 |
| `exp/provenance-preamble` | provenance header | section | 0.7017 | 0.8465 | 0.7368 | 0.7145 |
| `exp/note-summary` | per-note summary | section | 0.6811 | 0.8465 | 0.7368 | 0.7057 |
| `exp/mixed-mode` | document routing | section | 0.6790 | 0.8509 | 0.7632 | 0.6924 |

`exp/mixed-mode` is identical to base at section granularity, as it must be — a correctness check on
the branch split.

### The `rerank_top_k` discovery

Same code as round 1, one line changed.

| file | summaries | rerank_top_k | recency | nDCG | recall | complete |
|---|---|---|---|---|---|---|
| `combined-rerank30-mixed.json` | no | **30** | ON | 0.6974 | 0.8509 | 0.7368 |
| `combined-rerank30-mixed-rerun.json` | no | 30 | ON | 0.6998 | 0.8509 | 0.7368 |
| `combined-rerank30-section.json` | no | 30 | ON | 0.6969 | 0.8465 | 0.7368 |
| `combined-ctx-rerank30-mixed.json` | yes | 30 | ON | 0.7142 | 0.9254 | 0.8421 |
| `combined-ctx-rerank30-section.json` | yes | 30 | ON | 0.7156 | 0.8728 | 0.7632 |

**Concluded (wrongly):** the entire round-1 regression was `rerank_top_k`, and the feature set with
summaries beats baseline.
**Why wrong:** correct about `rerank_top_k`, wrong about the verdict — recency was still ON in every
arm, and it flattered the feature arms.

**Variance estimate from the rerun pair: ±0.0024 nDCG on identical inputs.** Across non-identical
reruns elsewhere, ±0.01–0.02.

---

## Round 4 — recency and `rerank_top_k` swept, two corpora (CURRENT for baseline comparison)

`eval/results/rerank-sweep-v1/`. `eval run` gained `--rerank-top-k` and `--recency-boost`; recency
now defaults **off** for evals and both settings are recorded in every result file.

### 4a. `rerank_top_k` sweep — new baseline with summaries, `eval`, recency OFF

**Varied:** `rerank_top_k` only.

| file | rerank_top_k | nDCG | recall | complete | MRR |
|---|---|---|---|---|---|
| `ctx-k10-norecency.json` | 10 | 0.7774 | 0.8772 | 0.7895 | 0.8217 |
| `ctx-k20-norecency.json` | 20 | 0.7868 | 0.8904 | 0.7895 | 0.8311 |
| `ctx-k30-norecency.json` | 30 | 0.7770 | 0.8904 | 0.7895 | 0.8202 |
| `ctx-k45-norecency.json` | 45 | 0.7825 | 0.9035 | 0.8158 | 0.8180 |
| `ctx-k60-norecency.json` | 60 | 0.7912 | 0.9035 | 0.8158 | 0.8333 |
| `ctx-k90-norecency.json` | 90 | 0.7812 | 0.9035 | 0.8158 | 0.8158 |

Flat. `rerank_top_k` is a non-parameter once recency is off.

### 4b. Pool size × recency, 2×2 — `eval`, summaries

**Varied:** `rerank_top_k` and `recency_boost_enabled`. Nothing else.

| file | rerank_top_k | recency | nDCG | recall |
|---|---|---|---|---|
| `ctx-k30-norecency.json` | 30 | OFF | 0.7770 | 0.8904 |
| `ctx-k60-norecency.json` | 60 | OFF | 0.7912 | 0.9035 |
| `ctx-k30-recency.json` | 30 | ON (multiplicative) | 0.6847 | 0.8904 |
| `ctx-k60-recency.json` | 60 | ON (multiplicative) | 0.5063 | 0.7456 |

30→60 delta: **+0.0142** with recency off, **−0.1784** with it on. The pool-size penalty is entirely
the recency interaction — the reranker does not degrade on a wider candidate set.

### 4c. Three-way baseline comparison, both corpora

**Varied:** implementation and summaries. **Held constant:** `rerank_top_k=30`, recency **OFF**,
mixed granularity.

| file | corpus | configuration | nDCG | recall | complete | MRR |
|---|---|---|---|---|---|---|
| `ORIGINAL-k30-norecency.json` | eval | original `main` | **0.8168** | 0.8904 | 0.7895 | **0.8860** |
| `plain-k30-norecency.json` | eval | new baseline, no summaries | 0.8082 | 0.8640 | 0.7632 | — |
| `ctx-k30-norecency.json` | eval | new baseline, summaries | 0.7770 | 0.8904 | 0.7895 | 0.8202 |
| `plain-k60-norecency.json` | eval | new baseline, no summaries | 0.8074 | 0.8640 | 0.7632 | — |
| `REALISTIC-ORIGINAL-k30-norecency.json` | realistic | original `main` | **0.9193** | **0.9737** | **0.9474** | **0.9342** |
| `REALISTIC-newbase-plain-k30-norecency.json` | realistic | new baseline, no summaries | 0.9038 | 0.9474 | 0.9211 | 0.9132 |
| `REALISTIC-newbase-ctx-k30-norecency.json` | realistic | new baseline, summaries | 0.8839 | 0.9474 | 0.9211 | 0.8947 |

Same ordering on both corpora: original > no summaries > with summaries.

### 4d. Cost of the old recency implementation, original `main`

| file | corpus | recency | nDCG | MRR |
|---|---|---|---|---|
| `ORIGINAL-k30-norecency.json` | eval | OFF | 0.8168 | 0.8860 |
| round 1 `original-main.json` | eval | ON | 0.6883 | 0.6998 |
| `REALISTIC-ORIGINAL-k30-norecency.json` | realistic | OFF | 0.9193 | 0.9342 |
| `REALISTIC-ORIGINAL-k30-recency.json` | realistic | ON | 0.8584 | 0.8605 |

The old multiplicative recency cost **0.129 nDCG / 0.186 MRR** on `eval` and **0.061 / 0.074** on
`eval-realistic`. It never improved any metric on either corpus.

---

## Round 5 — score-geometry recency (CURRENT)

Implements "Preserve score geometry" from the vault note *Designing Recency-Aware Reranking for RAG*:
keep the reranker's raw scores, give freshness a query-specific budget
`λ_q = s_(k) − s_(k+B)` measured from the gaps straddling the cutoff, rank on `A_i = s_i + λ_q·f_i`.
Freshness is the plain negative exponential `exp(-age_days / decay_days)` in `[0,1]` — the old
`+ 1.0` shift existed only so the multiplicative blend read as a boost rather than a penalty.

`recency_strategy` selects `score_geometry` (new default) or `multiplicative` (legacy, kept for A/B).
`recency_rank_budget` is B.

### 5a. Pool-size invariance — the point of the exercise

`eval`, summaries, recency ON. **Varied:** `rerank_top_k` and `recency_strategy`.

| strategy | k=30 nDCG | k=60 nDCG | 30→60 delta |
|---|---|---|---|
| `multiplicative` (old) | 0.6847 | 0.5063 | **−0.1784** |
| `score_geometry` B=3 | 0.7808 | 0.7873 | **+0.0065** |
| recency OFF (reference) | 0.7770 | 0.7912 | +0.0142 |

The new strategy tracks the recency-off reference. Pool-size dependence is gone.

### 5b. B sweep — `eval`, summaries, `rerank_top_k=30`

**Varied:** `recency_rank_budget` only.

| B | nDCG | recall | complete | MRR |
|---|---|---|---|---|
| recency OFF | 0.7770 | 0.8904 | 0.7895 | 0.8202 |
| 1 | **0.7872** | 0.9035 | 0.8158 | 0.8180 |
| 3 | 0.7808 | 0.8904 | 0.7895 | 0.8180 |
| 5 | 0.7481 | 0.8640 | 0.7632 | 0.7882 |
| 10 | 0.7068 | 0.8377 | 0.7368 | 0.7424 |
| `multiplicative` | 0.6847 | 0.8904 | 0.7895 | 0.6987 |

B behaves as an intuitive dial: small budgets are free or slightly positive, larger ones degrade
smoothly and monotonically. Every B including 10 beats the old multiplicative strategy.

### 5c. `eval-realistic`, summaries, `rerank_top_k=30`

| configuration | nDCG | recall | complete | MRR |
|---|---|---|---|---|
| recency OFF | 0.8839 | 0.9474 | 0.9211 | 0.8947 |
| `score_geometry` B=3 | 0.8839 | 0.9474 | 0.9211 | 0.8947 |
| `score_geometry` B=10 | 0.8839 | 0.9474 | 0.9211 | 0.8947 |
| `multiplicative` | 0.8437 | 0.9474 | 0.9211 | 0.8465 |

Identical to recency-off at every B — a **perfect no-op**, while the old strategy still costs 0.040
nDCG / 0.048 MRR.

Investigated rather than assumed. Budgets are non-zero and do scale with B (measured λ_q ranges
0.003–0.066 across queries, roughly tripling from B=3 to B=10). The corpus was generated in bulk, so
freshness is tightly clustered — many notes share exactly 0.853, spread is min 0.5625 / max 0.9864 /
std 0.121. Candidate-to-candidate freshness *differences* are therefore ~0.06, making the bonus
difference `λ_q × 0.06` ≈ 0.001–0.004, well below the reranker's gaps between top candidates. So
recency correctly declines to reorder anything where freshness carries no discriminating signal.

That is the "robust to different score distributions" design goal holding: the old strategy damaged
this corpus anyway, because it operated on rank-flattened scores whose gaps are uniform and
artificially small.

### 5d. Net effect

At `rerank_top_k=30` on `eval`, the old recency implementation cost 0.0923 nDCG against recency-off.
`score_geometry` at B=1–3 costs nothing and gains slightly. The full ~0.096 nDCG the old
implementation destroyed is recovered while still expressing a freshness preference.

Files: `geom-k30-B{1,3,5,10}.json`, `geom-k60-B3.json`, `REALISTIC-geom-k30-B{3,10}.json`,
`REALISTIC-mult-k30.json`.

## Round 6 — merge decision (CURRENT, DECISIVE)

`eval/results/merge-decision-v1/`. The comparison every earlier round was missing: the recency fix
applied to the *original* code, against the feature work, with both using the fixed recency.

**Varied:** implementation (`feat/recency-score-geometry` = `main` + recency fix only, vs
`exp/new-baseline` = markdown-it chunker + document-routing mixed mode ± summaries) and B.
**Held constant:** `recency_strategy=score_geometry`, `rerank_top_k=30`, mixed granularity, `n=10`,
`k=5`, recency ON except one reference row.

Branch A's index is `chroma-original` — the recency fix changes only retrieval, so the index built
from `5c78cf3` is byte-valid for it.

### `eval` (240 notes)

| configuration | B | nDCG | recall | complete | MRR |
|---|---|---|---|---|---|
| **A: `main` + recency fix** | 1 | **0.8103** | 0.8904 | 0.7895 | **0.8772** |
| A: `main` + recency fix | 3 | 0.7939 | 0.8772 | 0.7632 | 0.8509 |
| A: `main` + recency fix (recency OFF reference) | — | 0.8168 | 0.8904 | 0.7895 | 0.8860 |
| B: new baseline, no summaries | 1 | 0.7983 | 0.8640 | 0.7632 | 0.8640 |
| B: new baseline, no summaries | 3 | 0.7847 | 0.8509 | 0.7368 | 0.8421 |
| B: new baseline, summaries | 1 | 0.7941 | **0.9035** | **0.8158** | 0.8311 |
| B: new baseline, summaries | 3 | 0.7808 | 0.8904 | 0.7895 | 0.8180 |

### `eval-realistic` (649 notes)

| configuration | B | nDCG | recall | complete | MRR |
|---|---|---|---|---|---|
| **A: `main` + recency fix** | 1 | **0.9193** | **0.9737** | **0.9474** | **0.9342** |
| **A: `main` + recency fix** | 3 | **0.9193** | **0.9737** | **0.9474** | **0.9342** |
| B: new baseline, no summaries | 3 | 0.9038 | 0.9474 | 0.9211 | 0.9132 |
| B: new baseline, summaries | 3 | 0.8839 | 0.9474 | 0.9211 | 0.8947 |

### Verdict

**A wins nDCG and MRR on both corpora at every B tested**, and wins every metric outright on
`eval-realistic`. The recency fix alone, on the original retrieval code, is the best configuration
measured this session.

The one thing the feature work does better: on `eval`, summaries at B=1 give the best **coverage** of
any arm — recall 0.9035 vs A's 0.8904, complete 0.8158 vs 0.7895 — while costing 0.016 nDCG and
0.046 MRR. That trade does not reproduce on `eval-realistic`, where summaries leave recall and
complete unchanged and only cost ordering.

Recency is now nearly free: with the fix it costs 0.0065 nDCG on `eval` at B=1 and exactly nothing on
`eval-realistic`, against the old implementation's 0.129 and 0.061.

**Decision: merge `feat/recency-score-geometry` into `main`. Hold the chunking, mixed-mode and
summary work on branches.**

---

## Round 7 — merged configuration, verified

The state actually merged to `main`: Markdown-aware chunker + optional summaries + geometry
recency at B=1, **without** the document-routing mixed mode or the provenance preamble.

`eval`, k=30, mixed, recency ON via score_geometry B=1:

| configuration | nDCG | recall | complete | MRR |
|---|---|---|---|---|
| candidate, summaries off (shipped default) | 0.8019 | 0.8640 | 0.7632 | 0.8772 |
| candidate, summaries on (opt-in) | 0.7953 | **0.9167** | **0.8421** | 0.8180 |
| `main` + recency fix only (round 6 reference) | 0.8103 | 0.8904 | 0.7895 | 0.8772 |

Consistent with rounds 3–6: the chunker costs a little nDCG, and summaries trade ordering for
coverage. Summaries-on reaches the highest recall and complete rate measured in the entire session,
which is why the machinery ships enabled-by-config rather than removed.

Files: `merge-decision-v1/FINAL-candidate-{plain,ctx}-eval.json`.

---

## What each round changed about the conclusions

| round | claim | status |
|---|---|---|
| 1 | chunking rewrite regresses retrieval 26% | **false** — was `rerank_top_k` |
| 2 | mixed fusion causes 24% of it; summaries don't help | **false** — same hidden variable |
| 3 | `rerank_top_k` was the cause; feature set beats baseline | half right — cause correct, verdict wrong (recency still on) |
| 4 | recency is costly; baseline beats the feature work on both corpora | **current** |
| 5 | score-geometry recency is pool-size invariant and costs nothing; B is a well-behaved dial | **current** |
| 6 | `main` + recency fix beats the feature work on both corpora | **current, decisive** |
| 7 | shipped state verified: chunker + opt-in summaries + recency B=1, no mixed routing | **merged to main** |

## Method lessons

1. **A variable held constant across every arm of an A/B is invisible to all of them.** This happened
   twice — `rerank_top_k`, then `recency_boost_enabled`. Post-hoc ablation on a bundled diff cannot
   catch it; one-variable branches can.
2. **Record every ranking-relevant setting in the result file.** Rounds 1–3 are hard to audit because
   their `run` blocks omit `rerank_top_k` and `recency_boost_enabled`. Fixed in round 4.
3. **Eval with recency off.** It reweights on note dates, so its measured value is a property of the
   corpus date distribution, not of the retrieval design. Turn it on deliberately when that is what
   you are testing.
4. **Sanity-check the split, not just the result.** `exp/mixed-mode` matching base exactly at section
   granularity confirmed the branch carried what it claimed.

## Known gaps

- No synthesis-stage judging anywhere this session.
- `k=5` and `n=10` only; no cutoff sweep.
- `recency_decay_days` never swept (365 throughout). `recency_weight` now applies only to the
  legacy `multiplicative` strategy and was left at 0.2.
- The pairwise-preference formulation floated as an open question in the vault note is not implemented.
- `contextual_bm25: true` never measured.
- `exp/base` is not perfectly eval-neutral: 0.6738 vs the original's 0.6883 on mixed, because the
  markdown-it chunker trims trailing blank lines and so changes 776 of 1138 embedded chunk texts.
  Per-feature deltas in round 3 are therefore quoted against `exp/base`, not `main`.
- One run per cell except the two noted reruns.
