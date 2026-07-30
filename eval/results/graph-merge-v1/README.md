# Graph expansion, measured after the merge

Does one-hop wikilink expansion help now that `main` carries Markdown-aware chunking, optional note
summaries, and score-geometry recency? **No.** It is net-negative on both corpora and inert in one
configuration.

Branch `graph-augmented-retrieval` at the merge of `main` (`992c976`) plus `origin`'s
`76af2ae`. Compared against the same code without graph expansion.

Settings held constant: `stage retrieval`, `mode thorough`, `granularity mixed`, `n 10`, `k 5`,
`rerank_top_k 30`, embedding `qwen/qwen3-embedding-8b`, rerank `cohere/rerank-4-pro`.

## Graph expansion is genuinely active

Verified directly rather than assumed — a silent no-op would have looked like a clean result:

```
graph_status: ok | 240 nodes, 323 edges (eval)
                 | 649 nodes, 159 edges (eval-realistic)
6/6 sampled queries: applied=True, 51–60 entries added each, rows carrying graph provenance
```

Indexes were reused: entry text is unchanged by this branch, so an ordinary sync backfilled
`graph_outgoing` metadata with **zero re-embedding** (240 and 649 notes all `unchanged`).

## `eval` (240 notes, 323 edges)

| configuration | nDCG | recall | complete | MRR | vs no-graph |
|---|---|---|---|---|---|
| plain, recency off | 0.7868 | 0.8640 | 0.7632 | 0.8627 | — |
| plain, recency B=1 | 0.7868 | 0.8640 | 0.7632 | 0.8627 | **−0.0151 nDCG, −0.0145 MRR** |
| summaries, recency off | 0.7901 | 0.9035 | 0.8158 | 0.8311 | — |
| summaries, recency B=1 | 0.7953 | 0.9167 | 0.8421 | 0.8180 | **0.0000 on every metric** |

Query level, against `main` at the same settings:

- **plain:** 3 of 38 changed. q020 `decision_lookup` 1.0000 → 0.6309, q002 `semantic_paraphrase`
  0.4847 → 0.2723, q007 `temporal` +0.0074. Recall and complete are untouched, so graph-promoted
  entries are not finding new evidence — they are displacing correctly-ranked evidence in the top 5.
- **summaries:** **0 of 38 changed.** ~55 candidates are added per query and none reach the top 5.

## `eval-realistic` (649 notes, 159 edges)

| configuration | nDCG | recall | complete | MRR |
|---|---|---|---|---|
| plain, no graph | 0.9038 | 0.9474 | 0.9211 | 0.9132 |
| **plain, graph** | 0.8729 (**−0.0309**) | 0.9342 (**−0.0132**) | 0.9211 | 0.8684 (**−0.0448**) |
| summaries, no graph | 0.8839 | 0.9474 | 0.9211 | 0.8947 |
| **summaries, graph** | 0.8447 (**−0.0392**) | 0.9211 (**−0.0263**) | 0.8947 (**−0.0264**) | 0.8465 (**−0.0482**) |

Negative on every metric in both arms, including the evidence-group recall guardrail.

Query level:

- **plain:** 5 of 38 changed, 3 worse and 2 better. Worst is q040 `section_lookup` 1.0000 → 0.0000
  with recall 1.00 → 0.00 — a perfect result destroyed. Best is q038 `multi_note` +0.2372 with recall
  0.50 → 1.00, which is exactly the case graph expansion is designed for.
- **summaries:** 4 of 38 changed, **all worse**, again including q040 → 0.0000.

`q040` fails identically in both arms: a `section_lookup` query where expansion pulls in a linked
note that outranks the correct section. That single query accounts for roughly a third of the
realistic nDCG loss.

## Reading

Two consistent patterns across corpora:

1. **Expansion displaces rather than discovers.** On `eval` plain, recall and complete never move —
   only the ordering degrades. The wins it does produce (`q038`, +0.24 with recall 0.50 → 1.00) are
   real but rarer than the losses.
2. **Summaries and graph expansion address the same weakness, and summaries win.** On `eval` with
   summaries, expansion becomes completely inert: direct retrieval is strong enough that promoted
   neighbours never clear the top 5. On `eval-realistic` the two actively conflict, and the combined
   arm is the worst of the four.

The sparser link graph on `eval-realistic` (159 edges over 649 notes, versus 323 over 240) is the
likelier reason it does worse there: fewer, weaker links mean promoted neighbours are less often
relevant.

This agrees with the pre-merge assessment from 2026-07-26, which measured graph retrieval as
net-negative and left it unshipped. The new chunker, summaries and recency fix do not rescue it.

## Caveat on tuning

`GRAPH_WEIGHT = 0.15` was tuned against rank-derived relevance spanning `[0.5, 1.0]`. Score-geometry
recency ranks on the reranker's raw scores, whose spread differs per query, so the merge rescales the
bonus by that spread rather than adding a fixed amount; the factor is exposed per row as
`_relevance_spread`. These numbers therefore measure graph expansion *as rescaled*. Re-tuning
`GRAPH_WEIGHT` against raw-score geometry is the obvious next experiment if the feature is pursued —
though on `eval` with summaries the bonus would have to grow by a large factor to change anything at
all, and on `eval-realistic` the failure mode is a wrong note outranking a correct section, which a
smaller weight would mitigate but a larger one would worsen.

## Files

`graph-{plain,ctx}-eval-{norecency,recency}.json`, `graph-{plain,ctx}-realistic-norecency.json`.
Comparison baselines: `../merge-decision-v1/FINAL-candidate-{plain,ctx}-eval.json` and
`../rerank-sweep-v1/REALISTIC-newbase-{plain,ctx}-k30-norecency.json`.
