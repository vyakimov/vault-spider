# Contextual Chunking v1 — Retrieval Comparison

Retrieval-stage evaluation on the public `eval/` corpus, isolating two effects:

```text
original implementation  ──code change only──▶  smarter chunking  ──summaries only──▶  smarter + context
```

Synthesis judging was out of scope.

## Headline Result

**Smarter chunking regressed retrieval substantially. Summaries recovered part of that loss but did
not get back to the original baseline.**

| Metric | original | smarter | smarter+context | Δ1 (smarter−orig) | Δ1 % | Δ2 (ctx−smarter) | Δ2 % | net (ctx−orig) | net % |
|---|---|---|---|---|---|---|---|---|---|
| mean nDCG@5 | 0.6883 | 0.5079 | 0.5422 | −0.1804 | −26.2% | +0.0343 | +6.8% | −0.1461 | −21.2% |
| mean group recall@5 | 0.8640 | 0.7193 | 0.7675 | −0.1447 | −16.7% | +0.0482 | +6.7% | −0.0965 | −11.2% |
| complete rate@5 | 0.7632 | 0.5789 | 0.6579 | −0.1843 | −24.1% | +0.0790 | +13.6% | −0.1053 | −13.8% |
| MRR | 0.6998 | 0.4948 | 0.5453 | −0.2050 | −29.3% | +0.0505 | +10.2% | −0.1545 | −22.1% |

The original run reproduced its historical sanity values (complete@5 0.7632 and group recall 0.8640
are exact matches; nDCG 0.6883 vs 0.6794 and MRR 0.6998 vs 0.6823 differ within reranker variance),
so the baseline arm is trustworthy.

The smarter-chunking arm was rerun against the same index to rule out reranker variance
(`smarter-chunking-rerun.json`): nDCG 0.5070 vs 0.5079, and group recall, complete rate, and MRR
identical to four decimals. **The regression is deterministic, not noise.**

The evidence-group recall guardrail fails for Δ1: mean group recall dropped 0.864 → 0.719, and it
dropped on 10 individual queries. This is a real retrieval-quality loss, not an nDCG-only artifact.

## What Δ1 Actually Measures

Section boundaries are **effectively identical across all three indexes: 1138 section entries and
1378 total entries in every variant**, with every section starting on the same body line. Comparing
section bodies directly: 362 of 1138 are byte-identical and the remaining 776 differ only by trimmed
trailing blank lines — **0 differ in content**. On this corpus the Markdown-aware chunker reproduced
the original chunker's boundaries.

This is a property of *this corpus*, not of the code. The new chunker is genuinely different
(`markdown-it-py`, token-based sizing at `TARGET_TOKENS=450 / MAX_TOKENS=600 / HARD_MAX_TOKENS=900`)
versus the original's character-based `max_chars=6000`. The new hard cap is roughly 40% of the old
one, so a corpus with longer sections would chunk differently. No section in `eval/public_vault` is
long enough to trigger the difference.

Δ1 therefore does *not* measure chunk-boundary quality. It measures:

1. **The rewritten chunk header template.** Every section chunk now carries a much larger boilerplate
   preamble (title, `Path:`, `Type:`, `Tags:`, `Section:`, `Heading path:`) before its body text:

   | index | median section length | median preamble | preamble share | sections < 300 chars |
   |---|---|---|---|---|
   | original | 396 ch | 64 ch | 16.5% | 393 |
   | smarter | 548 ch | 209 ch | 40.2% | 265 |
   | smarter+context | 1094 ch | 766 ch | 70.4% | 0 |

2. **The retrieval/fusion rewrite** — `searcher.py` (+301 lines), `fusion.py` (+53),
   `evidence.py` (+27), and the mixed-granularity fusion path.

3. **A bundled config change:** `rerank_top_k` 30 → 60 (`vault_spider/config.py`). This rides inside
   Δ1 and is a confound — it was not isolated by this experiment.

**Hypothesis (not established by this run):** boilerplate that is near-identical across all 1138
chunks now occupies ~40% of the median chunk's embedded text, diluting the distinctive signal and
making chunks harder to tell apart. This is consistent with the breadth of the regression (27 of 38
answerable queries got worse) and with why summaries — which add back per-note distinctive content —
recover part of the loss. Confirming this requires an ablation that was not part of this plan.

## Δ1: Smarter Chunking − Original

27 of 38 answerable queries regressed, 2 improved, 9 unchanged. Group recall dropped on 10 queries
(q003, q004, q005, q006, q007, q009, q019, q035, q037, q038).

### Five largest regressions

| query | category | nDCG | group recall |
|---|---|---|---|
| q038 | multi_note | 0.920 → 0.237 (−0.682) | 1.00 → 0.50 |
| q004 | known_item | 0.646 → 0.000 (−0.646) | 1.00 → 0.00 |
| q005 | temporal | 0.987 → 0.556 (−0.431) | 1.00 → 0.50 |
| q009 | single_note_factual | 0.624 → 0.237 (−0.387) | 1.00 → 0.50 |
| q035 | known_item | 0.387 → 0.000 (−0.387) | 1.00 → 0.00 |

### Only improvements

| query | category | nDCG | group recall |
|---|---|---|---|
| q008 | incident | 0.556 → 0.907 (+0.351) | 0.50 → 1.00 |
| q001 | known_item | 0.444 → 0.626 (+0.182) | 1.00 → 1.00 |

### Failure shape

For the worst cases the correct evidence is present in the index under the same heading — it simply
ranks outside the top 5:

- **q004** ("Which Atlas ports are publicly exposed and which application ports stay internal?",
  slices `table` + `networking`). Original ranked `Service Port Registry → Service Port Registry`
  at 2 and `Atlas Sensor Hub Deployment → Current production shape` at 4. Smarter retrieved neither
  in the top 5; both are indexed but unranked. The `table` and `networking` slices both went
  0.646 → 0.000.
- **q038** ("How long are PostgreSQL transaction logs kept, and what backup frequency was originally
  proposed?"). Original ranked both evidence groups at 1 and 3. Smarter kept only
  `Atlas Backup Policy Draft 2023 → Original Proposal` at rank 5 and dropped
  `Atlas Log Retention Policy → Retention Periods` entirely.

This is a **ranking** failure, not a chunking or indexing failure.

## Δ2: Summaries − Smarter Chunking

11 queries improved, 15 regressed, 12 unchanged — but the improvements are much larger than the
regressions, so every overall metric rises. Group recall dropped on 4 queries (q006, q015, q018,
q024).

### Five largest improvements

| query | category | nDCG | group recall |
|---|---|---|---|
| q004 | known_item | 0.000 → 0.646 (+0.646) | 0.00 → 1.00 |
| q038 | multi_note | 0.237 → 0.877 (+0.640) | 0.50 → 1.00 |
| q023 | multi_note | 0.387 → 0.877 (+0.490) | 0.50 → 1.00 |
| q010 | single_note_factual | 0.321 → 0.764 (+0.442) | 0.33 → 0.67 |
| q019 | multi_note | 0.000 → 0.416 (+0.416) | 0.00 → 1.00 |

### Five largest regressions

| query | category | nDCG | group recall |
|---|---|---|---|
| q015 | ambiguous_entity | 0.387 → 0.000 (−0.387) | 1.00 → 0.00 |
| q018 | alias | 0.387 → 0.000 (−0.387) | 1.00 → 0.00 |
| q037 | multi_note | 0.613 → 0.307 (−0.306) | 0.50 → 0.50 |
| q008 | incident | 0.907 → 0.629 (−0.278) | 1.00 → 1.00 |
| q006 | temporal | 0.295 → 0.080 (−0.215) | 0.50 → 0.00 |

Summaries restore exactly the queries the header rewrite broke (q004 and q038 return to their
original ranks) — the strongest support for the dilution hypothesis above.

The regressions cluster on queries that require **distinguishing near-duplicate notes**:
`ambiguous_entity` (−0.228 nDCG), `alias` (−0.064), `historical` (−0.215), `current_configuration`
(−0.202), `dns` (−0.202), `privacy` (−0.200). A one-per-note canonical summary makes all sections of
a note look alike, which is the opposite of what disambiguation queries need. On q015 and q018 the
correct note left the top 5 entirely.

## Category Breakdown (nDCG | group recall)

| category | n | original | smarter | smarter+context | Δ1 nDCG | Δ2 nDCG |
|---|---|---|---|---|---|---|
| alias | 2 | 0.567 \| 0.750 | 0.415 \| 0.750 | 0.352 \| 0.250 | −0.152 | −0.064 |
| ambiguous_entity | 2 | 0.566 \| 1.000 | 0.444 \| 1.000 | 0.215 \| 0.500 | −0.122 | −0.228 |
| decision_lookup | 1 | 0.631 \| 1.000 | 0.500 \| 1.000 | 0.431 \| 1.000 | −0.131 | −0.069 |
| incident | 1 | 0.556 \| 0.500 | 0.907 \| 1.000 | 0.629 \| 1.000 | +0.351 | −0.278 |
| known_item | 8 | 0.810 \| 1.000 | 0.657 \| 0.750 | 0.715 \| 0.875 | −0.152 | +0.058 |
| metadata_filter | 1 | 1.000 \| 1.000 | 1.000 \| 1.000 | 1.000 \| 1.000 | 0.000 | 0.000 |
| multi_note | 9 | 0.585 \| 0.667 | 0.340 \| 0.444 | 0.502 \| 0.667 | −0.245 | +0.162 |
| section_lookup | 5 | 0.775 \| 0.900 | 0.593 \| 0.900 | 0.544 \| 0.900 | −0.182 | −0.049 |
| semantic_paraphrase | 2 | 0.594 \| 1.000 | 0.464 \| 1.000 | 0.358 \| 1.000 | −0.130 | −0.106 |
| single_note_factual | 3 | 0.711 \| 0.778 | 0.396 \| 0.611 | 0.676 \| 0.722 | −0.315 | +0.279 |
| temporal | 4 | 0.692 \| 1.000 | 0.444 \| 0.625 | 0.426 \| 0.750 | −0.248 | −0.017 |

Every category except `incident` (n=1) and `metadata_filter` (n=1) regressed under Δ1.

**Categories still below the original baseline even after summaries:** `alias` (0.567 → 0.352, and
recall collapsed 0.750 → 0.250), `ambiguous_entity` (0.566 → 0.215, recall 1.000 → 0.500),
`temporal` (0.692 → 0.426), `semantic_paraphrase` (0.594 → 0.358), `section_lookup`
(0.775 → 0.544), `decision_lookup` (0.631 → 0.431), `known_item` (0.810 → 0.715), `multi_note`
(0.585 → 0.502). Only `metadata_filter` held at 1.000 and only `incident` improved net.

## Slice Regressions Worth Noting

Slices where the overall picture hides a specific failure:

| slice | n | original | smarter | smarter+context | note |
|---|---|---|---|---|---|
| table | 1 | 0.646 \| 1.000 | 0.000 \| 0.000 | 0.646 \| 1.000 | total loss under smarter, fully recovered by summaries |
| networking | 1 | 0.646 \| 1.000 | 0.000 \| 0.000 | 0.646 \| 1.000 | same query (q004) |
| architecture | 1 | 0.352 \| 0.500 | 0.000 \| 0.000 | 0.303 \| 0.500 | not recovered |
| graph_shared_hub | 1 | 0.352 \| 0.500 | 0.000 \| 0.000 | 0.303 \| 0.500 | not recovered |
| historical | 1 | 0.629 \| 1.000 | 0.295 \| 0.500 | 0.080 \| 0.000 | degrades at every step; recall reaches 0 |
| current_configuration | 1 | 0.939 \| 1.000 | 0.646 \| 1.000 | 0.444 \| 0.500 | degrades at every step |
| dns | 1 | 0.939 \| 1.000 | 0.646 \| 1.000 | 0.444 \| 0.500 | same query |
| project | 1 | 0.500 \| 1.000 | 0.387 \| 1.000 | 0.000 \| 0.000 | summaries destroy it |
| recipe | 1 | 0.431 \| 1.000 | 0.387 \| 1.000 | 0.000 \| 0.000 | summaries destroy it |
| validation | 1 | 0.500 \| 1.000 | 0.387 \| 1.000 | 0.000 \| 0.000 | summaries destroy it |
| retention | 3 | 0.850 \| 1.000 | 0.456 \| 0.833 | 0.646 \| 1.000 | recall recovered, nDCG not |
| conflict | 3 | 0.723 \| 1.000 | 0.453 \| 0.667 | 0.446 \| 0.667 | not recovered |
| single_note | 10 | 0.750 \| 0.950 | 0.678 \| 0.900 | 0.584 \| 0.900 | degrades at every step |

The `historical` / `current_configuration` / `project` / `recipe` / `validation` slices get worse at
*both* steps — summaries actively hurt there. These are the "which version of this note is the right
one" cases.

## Conclusions

### Did smarter chunking improve retrieval?

**No — it regressed retrieval sharply and reproducibly.** nDCG@5 fell 26.2%, group recall 16.7%,
complete rate 24.1%, MRR 29.3%. 27 of 38 answerable queries got worse; the evidence-group recall
guardrail failed on 10 of them. A rerun reproduced the numbers to within 0.001 nDCG, so this is not
reranker variance.

Because section boundaries are identical across variants apart from trimmed trailing whitespace
(1138 sections, same start lines, 0 content differences), the regression cannot be attributed to
chunk boundaries. The candidate causes are the enlarged chunk
header template, the `searcher`/`fusion` rewrite, and the bundled `rerank_top_k` 30 → 60 change —
which this experiment did not separate.

### Did summaries improve over smarter chunking?

**Yes, modestly — but they are a partial repair, not a win.** All four overall metrics rose (nDCG
+6.8%, group recall +6.7%, complete rate +13.6%, MRR +10.2%), and the largest gains land precisely
on the queries the smarter arm broke. But summaries also caused 15 query-level regressions and
dropped group recall on 4 queries, concentrated in disambiguation categories (`ambiguous_entity`
−0.228, `alias` recall 0.750 → 0.250) where one canonical per-note summary makes a note's sections
indistinguishable from each other.

Net of both steps, the new implementation is still **21.2% worse on nDCG and 11.2% worse on group
recall** than the original `main` implementation.

> **Superseded in part — see the Section-Granularity Ablation below.** Re-measuring Δ2 on a
> retrieval stack that bypasses the new mixed fusion shows the summary benefit above is largely an
> artifact of repairing that path, not a genuine retrieval gain.

### Recommendation

Do not ship this as-is. Before re-measuring summaries, isolate the Δ1 regression with three
ablations against the original chunk header template:

1. smarter chunking with the **original** header preamble (tests the dilution hypothesis);
2. smarter chunking with `rerank_top_k` back at 30 (removes the bundled config confound);
3. the retrieval/fusion rewrite alone on the original index.

The summary experiment is only interpretable once the baseline it builds on is not itself broken.

---

# Addendum: Section-Granularity Ablation

`_mixed_fusion` (`searcher.py:131`) only executes when `granularity == "mixed"`. Re-running all
three arms at `--granularity section` bypasses it entirely, against the **same three indexes** — no
re-embedding, only the retrieval path changes. Everything else (models, corpus, `n`, `k`, mode) is
unchanged.

| arm | stack | nDCG@5 | recall@5 | complete@5 | MRR |
|---|---|---|---|---|---|
| original | mixed | 0.6883 | 0.8640 | 0.7632 | 0.6998 |
| original | section | 0.6781 | 0.8377 | 0.7368 | 0.6989 |
| smarter | mixed | 0.5079 | 0.7193 | 0.5789 | 0.4948 |
| smarter | section | 0.5417 | 0.7281 | 0.6316 | 0.5524 |
| smarter+context | mixed | 0.5422 | 0.7675 | 0.6579 | 0.5453 |
| smarter+context | section | 0.5537 | 0.7149 | 0.5789 | 0.5946 |

The original implementation is nearly **insensitive** to granularity (nDCG 0.6883 vs 0.6781). The new
implementation is not — which is itself evidence that the new mixed path is doing something the old
one didn't.

## Finding 1: mixed fusion is a minority cause of the Δ1 regression

| metric | Δ1 at mixed | Δ1 at section | attributable to `_mixed_fusion` |
|---|---|---|---|
| nDCG@5 | −0.1804 | −0.1364 | −0.0440 (**24%** of the drop) |
| recall@5 | −0.1447 | −0.1096 | −0.0351 (24%) |
| complete@5 | −0.1843 | −0.1052 | −0.0791 (43%) |
| MRR | −0.2050 | −0.1465 | −0.0585 (29%) |

**Removing the mixed-fusion path recovers only about a quarter of the nDCG regression.** Roughly 76%
survives with that code bypassed.

This corrects the main analysis above, which listed the `searcher`/`fusion` rewrite as a leading
suspect. It is a real contributor but the minority one. Since chunk boundaries are identical
across indexes, the majority cause must lie in what changed about the *embedded text* — the enlarged
header preamble (16.5% → 40.2% of median chunk) — or in the non-mixed portions of the retrieval
changes (`evidence.py`, `reader.py`, `rerank_top_k` 30 → 60). Ablation 1 in the Recommendation above
is now the highest-priority experiment.

## Finding 2: the summary benefit does not survive on a near-original stack

Δ2 (summaries − no summaries), measured under each retrieval stack:

| metric | mixed stack | section stack (near-original) |
|---|---|---|
| nDCG@5 | +0.0343 (+6.8%) | +0.0120 (**+2.2%**) |
| recall@5 | +0.0482 (+6.7%) | −0.0132 (**−1.8%**) |
| complete@5 | +0.0790 (+13.6%) | −0.0527 (**−8.3%**) |
| MRR | +0.0505 (+10.2%) | +0.0422 (+7.6%) |

**The evidence-group recall guardrail fails for Δ2 once mixed fusion is removed**, and complete@5 —
the strictest metric, "did we get every evidence group" — drops 8.3%. Only nDCG and MRR stay
positive, i.e. summaries reorder the top of the list favourably while retrieving *less* of the
required evidence.

Query level at section granularity: 13 improved, 11 regressed, 14 unchanged, with group recall
dropping on 6 queries (q002, q006, q020, q021, q024, q039).

| direction | queries |
|---|---|
| largest gains | q038 (+0.544, multi_note), q019 (+0.540, multi_note), q004 (+0.515, known_item), q023 (+0.490, multi_note), q036 (+0.387, multi_note) |
| largest losses | q006 (−0.518, temporal), q013 (−0.500, section_lookup), q020 (−0.500, decision_lookup), q021 (−0.431, section_lookup), q040 (−0.369, section_lookup) |

The split is coherent and mechanistic: **every large gain is `multi_note`/`known_item`** — find the
right *note* — and **three of five large losses are `section_lookup`** — find the right *section
within* a note. A single canonical per-note summary prepended to all of that note's sections makes
the note easier to locate and its sections harder to tell apart. That is the same effect flagged for
`ambiguous_entity` and `alias` in the main analysis, now visible as the dominant trade-off once the
mixed-fusion repair effect is stripped out.

## Revised Conclusion on Summaries

The earlier "yes, modestly" verdict was measured on top of a broken retrieval path. On a stack that
bypasses that path, summaries are **not a retrieval win**: +2.2% nDCG bought at −1.8% group recall
and −8.3% complete rate. Most of the +6.8% seen at mixed granularity was summaries compensating for
`_mixed_fusion`, not adding signal.

If summaries are pursued further, the per-note-canonical design is the thing to revisit — a summary
scoped to the section, or one used only for document-granularity entries and not copied onto every
child section, would target the `multi_note` gains without the `section_lookup` cost.

## Files

`section-original-main.json`, `section-smarter-chunking.json`, `section-smarter-plus-context.json`.
Command shape (paths per arm as in [README.md](README.md)):

```bash
VAULT_SPIDER_CONFIG=<arm config> \
./bin/vault-spider eval run \
  --dataset eval --stage retrieval --mode thorough --granularity section -n 10 --k 5 \
  --out eval/results/contextual-chunking-v1/section-<arm>.json
```

## Reproduction

See [README.md](README.md) for commit SHAs, models, timestamps, and the exact commands.

---

# Addendum 2: The `combine(max)` Scoring Fix

## The defect

`_mixed_fusion` scored the two semantic sources with different transforms and merged them with
`max`:

- direct hits: `exp(-chroma_distance) + 1`
- parent-routed children: raw `dot(query, embedding) + 1`

Embeddings are L2-normalized and the collection uses Chroma's default `l2` space, so
distance = 2 − 2·cos. The two formulas therefore disagree for every cos < 1 — routed children scored
~0.11–0.14 higher than an identical direct hit — and `max` locked in the inflated value.

Fixed at `searcher.py:246` by reconstructing the distance so both paths share one scale:

```python
values[child_id] = float(np.exp(-(2.0 - 2.0 * cosine)) + 1.0)
```

Gates after the fix: `ruff` clean, `pytest` 585 passed, `pyright` 0 errors.

## Measured effect: essentially none

| metric | smarter (buggy) | smarter (fixed) | Δ | ctx (buggy) | ctx (fixed) | Δ |
|---|---|---|---|---|---|---|
| nDCG@5 | 0.5079 | 0.5075 | −0.0004 | 0.5422 | 0.5422 | 0.0000 |
| recall@5 | 0.7193 | 0.7193 | 0.0000 | 0.7675 | 0.7675 | 0.0000 |
| complete@5 | 0.5789 | 0.5789 | 0.0000 | 0.6579 | 0.6579 | 0.0000 |
| MRR | 0.4948 | 0.4948 | 0.0000 | 0.5453 | 0.5453 | 0.0000 |

Two queries moved on the smarter arm (q001 +0.021, q043 −0.033); the contextual arm was bit-identical
across all 44 queries.

## Why it was inert

Both transforms are **strictly monotonic in cosine**:

| cos | `dot+1` (buggy) | `exp(-(2−2cos))+1` (fixed) |
|---|---|---|
| 0.50 | 1.5000 | 1.3679 |
| 0.80 | 1.8000 | 1.6703 |
| 0.95 | 1.9500 | 1.9048 |
| 1.00 | 2.0000 | 2.0000 |

Everything downstream of `combined_semantic` consumes **rank order**, not score magnitude:

- `weighted_reciprocal_rank_fusion` takes ranked id lists and scores them `weight / (k + rank)`
- `expand()` picks each document's top-3 children by sorting on the score

A monotonic distortion cannot change either. So the wrong scale never reached a decision.

## Why keep the fix

It is still a real defect, on two counts:

1. The `semantic` value reported in every output row and in debug output was inflated for
   routed sections — wrong numbers surfaced to callers and to anyone tuning the system.
2. It is a latent landmine. Any non-monotonic consumer — a score threshold, a linear blend, the
   `minmax` or `zsigmoid` combine strategies — would have turned it into a real ranking bug. Mixed
   mode currently forces `mixed_rrf`, which is the only reason it stayed hidden.

## Bearing on the regression

None. The Δ1 regression is unchanged at −0.1808 nDCG against the original baseline. This eliminates
the scoring bug as a candidate cause and leaves the chunk header preamble as the leading suspect,
per Addendum 1.

## Mixed mode is still net-negative after the fix

Comparing mixed against plain section search **on the same index**:

| arm | mixed | section | mixed's contribution |
|---|---|---|---|
| original (cap only) | 0.6883 | 0.6781 | **+0.0102** |
| smarter, fixed | 0.5075 | 0.5417 | **−0.0342** |
| smarter+context, fixed | 0.5422 | 0.5537 | **−0.0115** |

The baseline's 3-sections-per-note diversity cap adds value. The document-routing pipeline that
replaced it subtracts value on both new indexes, with the scoring bug ruled out. The remaining
suspects inside `_mixed_fusion` are structural rather than arithmetic:

- the hard **top-3 children per document** truncation, applied before fusion — a note's 4th-best
  section can never surface through the parent path;
- the hardcoded **80/20 direct-vs-parent weight split**, which is not in `SearchParams`, has no
  comment justifying it, and was never swept;
- likewise hardcoded: the top-20 document cut and the 2,000-child cap.

## Files

`fixed-smarter-chunking.json`, `fixed-smarter-plus-context.json`. Same commands as the canonical
mixed runs; only `searcher.py` changed, no re-embedding.
