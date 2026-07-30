# Reranker-Gated Graph Expansion: implementation plan

**Status:** proposed  
**Scope:** simplify the existing `graph-augmented-retrieval` branch so the graph is used only
for candidate generation and the reranker is the final relevance gate for graph-expanded
candidates.  
**Assumption:** the live vault contains no transclusions worth designing for. Transclusion-aware
indexing, link-context augmentation, and synthetic edge records are out of scope.

---

## 1. Decision

Keep the persisted one-hop wikilink graph and the existing eligibility gates, but remove every
graph contribution to post-rerank scoring.

The resulting retrieval pipeline is:

```text
BM25 + embeddings
        |
      fusion
        |
        +----------------------+
        |                      |
top direct rerank pool    top fused notes as seeds
                               |
                         one-hop expansion
                               |
                         graph candidates
        |                      |
        +---------- union -----+
                    |
                 reranker
                    |
          ordinary recency policy
                    |
              final top results
```

The graph may cause a candidate to be shown to the reranker. It may not increase that
candidate's score after the reranker has judged it.

This deliberately narrows the hypothesis:

> Some relevant passages are absent from the normal rerank pool but are linked from notes that
> hybrid retrieval finds. Once those passages are admitted, the reranker can recognize their
> relevance from their own text.

This design does not attempt to solve cases where the relationship is understandable only from
the sentence containing the link. If the simplified experiment cannot improve retrieval, that
result becomes evidence for a later relation-aware design rather than a reason to add the graph
bonus back.

---

## 2. Goals

1. Preserve the complete direct rerank pool used by the graph-disabled baseline.
2. Add a small, deterministic set of graph candidates on top of that pool.
3. Require every graph-added candidate to receive a valid reranker score.
4. Let the reranker, followed only by the existing non-graph recency policy, determine whether a
   graph candidate reaches the final results.
5. Preserve all folder, tag, type, provenance, date, and `must_include` filters.
6. Preserve the current failure behavior: a missing/stale graph or reranker failure falls back to
   ordinary retrieval.
7. Keep the current retrieval contract shape and graph provenance for diagnostics.
8. Produce an evaluation that isolates this mechanism from graph-direction, section-selection,
   query-routing, and graph-weight experiments.

---

## 3. Non-goals

- No transclusion support or transclusion-aware indexing.
- No linked-content or linked-title augmentation of embeddings/BM25.
- No link-context text supplied to the reranker.
- No post-rerank graph bonus, tie-break, authority prior, or score interpolation.
- No Personalized PageRank or multi-hop traversal.
- No LLM query classifier or graph-specific query routing.
- No public CLI, MCP, or web configuration flags in this pass.
- No graph schema or retrieval contract shape change.
- No tuning sweep over seed count, decay, degree damping, or candidate caps before the
  reranker-only mechanism has been measured.

---

## 4. Current state and the minimal change

The current branch already does most of the candidate-generation work:

- expansion runs only in `thorough` mode with a configured reranker and a healthy graph;
- graph expansion happens after fusion;
- the ordinary direct rerank pool is selected first;
- graph candidates are appended to the rerank call rather than replacing direct candidates;
- expanded entries pass through the same `allowed_ids` filter;
- reranker failure discards graph-only results;
- the output contract records the seed note in a nullable `graph` block.

The harmful behavior is concentrated after reranking:

```python
graph_bonus = GRAPH_WEIGHT * propagated_score
relevance_score = reranked_score + graph_bonus
```

The first implementation milestone removes that path:

```python
relevance_score = reranked_score
```

The existing recency policy remains unchanged and applies identically to direct and graph
candidates. In this plan, “reranker is the final gatekeeper” means that no graph-specific signal
is allowed after reranking; it does not remove the baseline recency behavior.

There is one additional correctness tightening: only graph candidates actually admitted to and
scored by the reranker may be materialized as graph-added result rows. Expansion may discover
more candidates than fit in the additional rerank budget; those unscored candidates must not
leak into large result sets with a synthetic fused score of `0.0`.

---

## 5. Target invariants

The implementation should make these properties explicit and testable.

### 5.1 Direct-pool preservation

Let `D` be the ordered direct rerank pool produced with graph expansion disabled:

```text
D = fused.head(rerank_top_k)
```

With graph expansion enabled, the reranker input must be:

```text
D + G
```

where `G` contains only deduplicated graph-admitted candidates not already in `D`.

The graph must never shorten, replace, or reorder `D` before the reranker call.

### 5.2 Bounded additive work

`G` must be capped independently of `rerank_top_k`. Rename
`GRAPH_RESERVED_POOL_SLOTS` to `GRAPH_EXTRA_RERANK_CANDIDATES` to describe its actual role.

Initial value:

```text
GRAPH_EXTRA_RERANK_CANDIDATES = 10
```

The normal pool therefore remains 30 candidates and the maximum rerank request becomes 40.

### 5.3 Reranker-only graph relevance

- Remove `GRAPH_WEIGHT`.
- Remove the `graph_bonus` DataFrame column.
- Remove all graph arithmetic from `relevance_score`.
- `propagated_score` may rank candidates for admission into `G`; it may not affect final
  relevance.
- A graph-only candidate must have a non-null reranker score before it can appear in results.

### 5.4 Failure-safe fallback

If the reranker raises, returns no usable ranking, or fails provider validation:

- remove graph-only rows;
- clear graph admission provenance;
- return the same fused/recency fallback the graph-disabled path would return;
- report `fallback_reason: "rerank_unavailable"`.

### 5.5 Filter safety

Graph expansion must continue to use `allowed_ids` as the single filter gate. Do not add a second
filter implementation.

### 5.6 Determinism

- Stable-sort seed notes and graph candidates.
- Resolve ties by entry ID.
- Preserve the direct pool's existing order before the reranker.
- Report the exact IDs admitted through the graph in debug/test instrumentation where practical.

---

## 6. Candidate admission algorithm

Implement admission as a distinct step rather than letting graph discovery implicitly mutate the
candidate frame.

### Step 1: capture the baseline direct pool

Immediately before graph candidates are added:

```text
direct_pool_ids = first min(len(fused), rerank_top_k) fused IDs
```

This list is authoritative for the direct-pool-preservation invariant.

### Step 2: discover graph candidates

Reuse the current machinery for the first ablation:

- collapse fused entries by `note_id`;
- take the existing top seed count;
- walk the existing symmetric one-hop graph;
- keep the current damping and neighbor cap;
- query Chroma within reached notes;
- retain the current per-note section cap;
- apply `allowed_ids`.

Keeping these choices fixed makes removal of the bonus the only material retrieval hypothesis
change. Outgoing-only traversal and broader section admission are separate follow-up experiments
described later.

### Step 3: identify candidates whose admission is graph-caused

Candidates eligible for `G` are graph-reached entry IDs not already in `direct_pool_ids`.
This includes:

- entries absent from the hybrid candidate frame; and
- entries present in fusion but below the ordinary rerank cutoff.

Deduplicate by entry ID. Sort by propagated admission score descending, then entry ID ascending.
Take at most `GRAPH_EXTRA_RERANK_CANDIDATES`.

### Step 4: materialize only selected graph-only entries

For selected entries absent from the fused frame:

- add the minimum score/raw-score rows needed for contract assembly and fallback cleanup;
- use genuine BM25 and scoped semantic scores where already available;
- keep `fused_score = 0.0`, as required by the v3 contract.

Do not materialize discovered graph-only entries that were not selected for the rerank call.

### Step 5: call the reranker once

The reranker receives:

```text
pool_ids = direct_pool_ids + graph_admitted_ids
```

Every graph-admitted candidate must be present in the validated reranker response. Existing
OpenRouter response validation remains authoritative.

### Step 6: apply ordinary ranking

Convert reranker output using the existing `rerank_use_ranks` behavior. Then:

```text
relevance_score = reranked_score
boosted_score = existing recency calculation
```

There is no graph-specific score after this point.

### Step 7: attach provenance only where the graph affected admission

Attach the candidate's `graph` block when graph expansion admitted it into the rerank pool.
Candidates already in the normal direct pool do not need graph provenance because the graph did
not cause their admission.

This makes the `graph` block causally meaningful:

> This candidate was judged because a retrieved note linked to it.

---

## 7. File-by-file implementation

### `vault_spider/retrieval/searcher.py`

1. Delete `GRAPH_WEIGHT`.
2. Rename `GRAPH_RESERVED_POOL_SLOTS` to `GRAPH_EXTRA_RERANK_CANDIDATES`.
3. Update graph comments to describe candidate admission rather than rank promotion.
4. Separate graph discovery from graph admission:
   - capture `direct_pool_ids`;
   - compute `graph_admitted_ids`;
   - materialize only admitted graph-only IDs;
   - send `direct_pool_ids + graph_admitted_ids` to the reranker.
5. Delete `graph_bonus` construction.
6. Set `relevance_score` directly from `reranked_score`.
7. Keep the existing reranker-failure cleanup, tightening it to the admitted graph-only IDs.
8. Restrict graph provenance on output rows to admitted graph candidates.
9. Update debug information:
   - remove `weight`;
   - replace `reserved_pool_slots` with `extra_rerank_candidate_cap`;
   - add `direct_rerank_pool_size`;
   - add `graph_entries_discovered`;
   - add `graph_entries_admitted`;
   - add `total_rerank_pool_size`;
   - add `graph_entries_returned`.

Do not change seed count, neighbor cap, damping, direction, or sections per note in this commit.

### `tests/test_searcher_unit.py`

Replace bonus-oriented fixtures and assertions with gatekeeper-oriented tests. The current
deliberately irrelevant leaf is useful as a negative control but should no longer be expected to
surface merely because it is linked.

Add a deterministic reranker test provider that can distinguish:

- a relevant graph-only target that hybrid retrieval cannot reach;
- an irrelevant linked target;
- ordinary direct candidates.

Required unit tests:

1. **Relevant graph candidate survives.** A graph-only passage receives a high reranker score and
   reaches the final results without a bonus.
2. **Irrelevant graph candidate is rejected.** A linked but query-irrelevant passage receives a
   low reranker score and does not displace the expected top results.
3. **Direct pool is preserved.** The first `rerank_top_k` reranker inputs are byte-for-byte the
   graph-disabled direct pool, in the same order.
4. **Graph work is additive and capped.** The request contains at most
   `rerank_top_k + GRAPH_EXTRA_RERANK_CANDIDATES` unique IDs.
5. **Below-cutoff direct candidate can be graph-admitted.** An entry already in fusion but below
   the direct rerank cutoff is added exactly once.
6. **Unadmitted discovery does not leak.** A graph-only entry discovered outside the additional
   cap never appears in output, even with a large `n_results`.
7. **No graph score survives reranking.** Given identical reranker position and recency metadata,
   a graph candidate and direct candidate follow the same final-score path.
8. **Rerank failure is graph-neutral.** The result matches the graph-disabled fused fallback and
   carries no graph provenance.
9. Preserve existing tests for fast mode, no reranker, stale graph, filter enforcement, and
   deterministic caps.

Delete `test_the_bonus_reaches_the_final_score` and all imports/assertions involving
`GRAPH_WEIGHT`.

### `tests/test_evidence.py`

Keep the nullable `graph` block contract. Add or update assertions that:

- `propagated_score` is diagnostic/admission metadata, not part of `scores.final`;
- `why == "linked from …"` is used for graph-admitted results unless a top-three rerank
  explanation takes precedence;
- directly admitted candidates without graph-caused admission retain `graph: null`.

### `tests/test_cli.py`, `tests/test_web_format.py`, and `tests/test_web_routes.py`

Update only expectations whose prose claims a graph bonus. The JSON shape remains unchanged.
Verify that the web's `↗ linked` marker still appears for a graph-admitted candidate that survives
the reranker.

### `vault_spider/cli.py`

Keep schema version 3 because no field is added, removed, or retyped.

Update schema descriptions:

- `scores.final`: ordinary rerank/recency result; no graph bonus.
- `graph.propagated_score`: candidate-admission signal only.
- `graph`: indicates that graph expansion admitted the candidate to the reranker.

### Documentation and generated architecture map

After the behavior passes its acceptance gates:

- update `README.md`;
- update `AGENTS.md`;
- add an addendum to `docs/graph-augmented-retrieval-report.md`;
- update the hand-maintained graph retrieval prose in `tools/build_codebase_map.py`;
- regenerate `docs/codebase-map.html` and `docs/codebase-map.json`.

The documentation must not say that graph candidates receive a nudge, boost, or post-rerank
promotion.

---

## 8. Evaluation protocol

Evaluation must compare the simplified mechanism with a graph-disabled control, using the same
code, index contents, model IDs, and query embedding cache.

### 8.1 Variants

Run these two required variants:

1. **Control:** graph metadata stripped so `graph_status == "missing"`.
2. **Reranker-gated graph:** healthy graph, additive candidates, no graph bonus.

The historical graph-plus-bonus results in
`docs/graph-augmented-retrieval-report.md` are context, not the primary control.

### 8.2 Datasets

Run retrieval-stage evaluation on:

- `eval/` as the discriminating public corpus;
- `eval-realistic/` as the messy-vault regression corpus.

Use:

```text
--mode thorough --granularity mixed --k 5
```

Retain the metadata-stripping A/B procedure from the report. Save the complete per-query outputs,
not only aggregate tables.

### 8.3 Required aggregate and slice metrics

Record:

- complete@5;
- mean evidence-group recall@5;
- mean nDCG@5;
- MRR;
- graph-direct slice metrics;
- known-item slice metrics;
- number of graph-admitted candidates sent to the reranker;
- number and percentage reaching the final top five;
- number of previously missing evidence groups supplied;
- number of baseline evidence groups evicted;
- reranker document count and retrieval latency.

### 8.4 Per-query diagnostics

For every query changed by graph expansion, record:

- direct rerank pool IDs;
- graph-admitted IDs and seed paths;
- reranker rank for each admitted candidate;
- final top five before and after;
- evidence groups gained or lost;
- whether the graph candidate was absent from fusion or merely below the rerank cutoff.

These diagnostics answer the central mechanism question: does the reranker ever recognize useful
graph-supplied evidence?

### 8.5 Acceptance gates

The simplified design is useful enough to retain only if all of the following hold:

1. At least one previously missing required evidence group is supplied on the public
   `graph_direct` slice.
2. Graph expansion improves at least two queries across the two corpora, rather than producing a
   single fragile demonstration.
3. Overall complete@5 does not fall on either corpus.
4. No known-item query loses its required grade-3 evidence from the top five.
5. Overall nDCG@5 and MRR do not fall by more than 0.005 absolute on either corpus.
6. No regression is caused by direct-pool displacement before reranking.
7. Every returned graph-admitted candidate has a non-null reranker score.
8. The maximum rerank request remains bounded at
   `rerank_top_k + GRAPH_EXTRA_RERANK_CANDIDATES`.
9. Median thorough-mode retrieval latency does not increase by more than 35% on the evaluation
   workload.

If retrieval-model nondeterminism changes conclusions near a threshold, repeat each variant three
times and compare the distribution rather than selecting the best run.

Failure to meet the first two gates means candidate widening is not demonstrating positive value.
Do not compensate by restoring a graph bonus.

---

## 9. Follow-up experiments, only if diagnosed

Do not bundle these with the first reranker-only implementation. Each changes a different part of
the hypothesis.

### 9.1 Outgoing-only traversal

The stored graph retains outgoing and incoming adjacency. If reranker diagnostics show backlinks
dominate admitted false positives, add `graph_outgoing(note_id)` or equivalent and compare:

- outgoing only;
- incoming only;
- symmetric.

Prefer outgoing-only in production unless backlinks demonstrate independent gains.

### 9.2 Broader section admission

The first pass preserves `GRAPH_SECTIONS_PER_NOTE = 3`. If a gold neighbor note is reached but its
required section is not sent to the reranker, run a section-admission ablation:

- current top three semantically nearest sections per reached note;
- all allowed sections from fewer reached notes, under a global entry cap;
- query-scoped round-robin selection across reached notes.

The additional rerank entry cap must remain explicit. Do not interpret “all sections” as an
unbounded reranker request.

### 9.3 Conditional expansion

If graph expansion produces useful wins but unacceptable known-item noise or latency, then test a
dominance/flatness gate. Query routing is a cost and precision optimization, not part of proving
the core candidate-generation mechanism.

### 9.4 Relation-aware reranking

If relevant graph candidates consistently receive low reranker scores despite oracle evidence
that they are needed, the simple hypothesis has failed in the expected way: candidate text alone
does not explain the relationship.

The next design may provide the ordinary wikilink's surrounding source sentence to the reranker.
That is explicitly outside this implementation and must not be approximated with a post-rerank
bonus.

---

## 10. Rollout and rollback

1. Implement and test on the existing graph branch.
2. Run the graph-disabled and reranker-gated evaluations.
3. Record results in an addendum to the graph retrieval report.
4. Merge automatic expansion only if the acceptance gates pass.
5. If the gates fail:
   - leave graph persistence available for stats/web/link features if desired;
   - disable retrieval-time expansion;
   - retain the negative evaluation;
   - move to relation-aware reranking only if the per-query diagnostics justify it.

Rollback is straightforward because the persisted graph does not alter BM25 or embeddings.
Disabling the eligibility path returns retrieval to the ordinary hybrid/rerank pipeline without
requiring an index reset.

---

## 11. Suggested commit sequence

1. **Make graph expansion reranker-gated**
   - remove the bonus;
   - introduce additive admission terminology;
   - materialize only admitted candidates;
   - update debug fields.

2. **Replace promotion tests with gatekeeper tests**
   - relevant and irrelevant graph-only candidates;
   - direct-pool preservation;
   - cap, filter, failure, and no-leak invariants.

3. **Record reranker-only graph evaluation**
   - run both corpora;
   - add the per-query and aggregate report addendum;
   - make the ship/no-ship decision.

4. **Refresh contracts and documentation**
   - schema prose, README, AGENTS, codebase-map source and generated artifacts.

Keep any outgoing-only, section-admission, or query-gating experiment in a later commit so its
effect remains independently measurable.

---

## 12. Completion checklist

- [ ] Direct rerank pool is unchanged before graph candidates are appended.
- [ ] Graph candidate admission has a separate hard cap.
- [ ] `GRAPH_WEIGHT` and all graph-bonus arithmetic are gone.
- [ ] No graph-only candidate can appear without being admitted and reranked.
- [ ] Graph failure and reranker failure preserve the ordinary fallback.
- [ ] Filters remain authoritative through `allowed_ids`.
- [ ] Retrieval contract remains schema v3 and documentation reflects the new semantics.
- [ ] Network-free unit and integration tests pass.
- [ ] `ruff` passes.
- [ ] Public and realistic A/B evaluation results are recorded.
- [ ] Acceptance gates produce an explicit ship/no-ship decision.
- [ ] Codebase-map prose and generated files are refreshed if the behavior ships.
