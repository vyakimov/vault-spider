# Graph-Augmented Retrieval: motivation, implementation, and why it didn't pay off

**Status:** built and measured 2026-07-26 on branch `graph-augmented-retrieval`, not shipped.
Net negative on both golden evals. 576 tests green; the code is complete and correct — the
hypothesis is what failed.

---

## a) Why a graph layer should have helped

### The gap it targets

Hybrid retrieval scores every chunk **independently** against the query. BM25 asks "does this
text share the query's words?"; the embedding side asks "does this text mean something similar?"
Both are functions of one chunk's content in isolation. A candidate that cannot justify itself
on its own text cannot be retrieved, however relevant it is.

But notes in a vault are not written to be read in isolation. A note assumes its neighbours and
delegates to them by link rather than by restating them. From the realistic eval corpus:

> `Plan — Flask HTMX.md`: "Nightly `sqlite3 .backup` into the [[NAS Snapshot Replication]] path
> on [[LordByron]]."
>
> `NAS Snapshot Replication.md`: "Hourly snapshots of the main volume, keep **24 hourly and 30
> daily**..."

Ask "for the built pantry app, describe the backup chain and retention" and the second note is
required, yet it contains no query term — not "pantry", not "app", not even "retention". It also
sits in a different embedding neighbourhood, because it is about NAS scheduling, not about the
application. **Lexical and semantic retrieval are both blind to it by construction.** Better
embeddings do not help; the signal is not in the text.

The link is the signal. And it is a good one:

- **It is human-authored.** Unlike an inferred similarity edge, a wikilink is a deliberate
  assertion by the vault's author that two notes belong together. That is a higher-precision
  relation than cosine distance, and it is *orthogonal* to both existing channels rather than a
  third correlated view of the same text.
- **It is free.** No entity extraction, no LLM pass, no community summarisation, no second
  datastore. The edges already exist and are already parsed by lint.
- **It is deterministic**, so it does not undermine the reproducibility the retrieval contract
  depends on.

### The expected effect on recall and precision

**Recall** was the primary thesis. The golden eval scores *complete evidence groups*: a
multi-note query is only complete when every required group appears in the top k. The July
baseline's failures were exactly this shape — queries retrieving one required note and missing
the second. If the missing note is linked from the found one, expansion reaches it and
completeness rises.

**Precision** was expected to hold, for two reasons:

1. **The reranker as guard.** Expansion only widens the *candidate pool*; a cross-encoder then
   judges every candidate against the query. Irrelevant neighbours get demoted. The graph
   proposes; the reranker disposes.
2. **Degree damping.** Propagation is divided by the log-scaled degree of both endpoints, so a
   glossary, MOC, or daily note linking half the vault contributes a vanishing score per
   neighbour and cannot flood the pool.

A second-order argument: every link added through the `lint`/`enrich` hygiene loop would become
a retrieval edge, so curation work would start paying retrieval dividends.

### Limitations known in advance

- Edges are **note-level**; candidates are **section-level**.
- **Orphans gain nothing** — acceptable, and already surfaced by `lint`.
- **One hop only.** Evidence pairs that are merely co-cited by a shared hub (two hops apart)
  were expected to remain out of reach.

Hold on to the first of these. It is the one that mattered.

---

## b) How it was implemented

Three layers, all gated so that any failure degrades to today's behaviour.

### 1. Graph construction and persistence (`corpus/`, `index/`)

`vault_spider/corpus/links.py` already resolved wikilinks the way Obsidian does — aliases,
frontmatter links (`parents: "[[Daily Notes]]"`), attachments, fenced and inline code, self-links
— and was already shared by lint and the web reading view. That resolver was reused wholesale;
the only new work was making it available to the indexer.

- **`loader.Note` taught to satisfy the `LinkNode` protocol** (`stem`, `aliases`,
  `frontmatter_text`). This matters more than it looks: without `aliases`, links through
  frontmatter aliases silently produce no edge. It required moving `alias_list` and
  `frontmatter_text` into `corpus/frontmatter.py` to avoid an import cycle.
- **The graph is built during `sync`, from the same deduplicated note set that is indexed** —
  never from a second vault walk, which could disagree with the indexed set.
- **Edges are stored on document entries** as a canonical JSON list of target `note_id`s, with
  `graph_schema_version`, a snapshot hash, and node/edge counts on the collection.
- **Integrity is explicit.** On load, adjacency is rebuilt from the entries and the hash
  re-derived: `ok`, `missing` (index predates the feature), or `stale` (hash/count/shape
  mismatch). Anything but `ok` disables expansion and **never raises**.
- **Failure-safe ordering preserved**: all embedding work, then deletes, then adds, then graph
  metadata, then the hash *last*. A crash mid-write leaves a usable index and a detectably stale
  graph rather than a silently wrong one.
- Notes whose *content* is unchanged still get their edges refreshed, because a link target's
  title or alias can change without the linking note's `content_hash` moving.
- No `--reset` required: one ordinary `sync` backfills an existing index.

### 2. Retrieval-time expansion (`retrieval/searcher.py`)

Runs **after fusion, before reranking**. BM25, embeddings, fusion and every filter behave
exactly as before.

Eligibility requires all three: `mode == "thorough"`, a reranker configured, `graph_status == "ok"`.

1. Collapse the fused frame by `note_id`; take the top **10** notes as seeds.
2. Walk **one hop**, symmetrically (outgoing links *and* backlinks), excluding seeds.
3. Score each neighbour:
   `propagated = seed_fused × 0.5 / max(1, √(ln(2+deg_seed) × ln(2+deg_neighbour)))`
4. Keep the best **20** neighbours; map them back to entries with a **single** batched Chroma
   query, taking each note's best 3 sections.
5. Every expanded entry must pass through the same `allowed_ids` set as direct candidates —
   the single gate enforcing folder/tag/type/provenance/date/must-include. Expansion can never
   route a candidate around a filter.
6. **Reserved rerank-pool slots**: up to 10, on top of the usual top-30 by fused score.
7. **Post-rerank bonus**: `relevance = reranked_score + 0.15 × propagated`, before recency.
8. If reranking fails or returns nothing usable, graph candidates and boosts are discarded and
   retrieval falls back to fused ranking, byte-identical to today.

**Steps 6 and 7 are deliberate deviations from the original plan**, and they are the engineering
core of this work:

- The plan specified pool admission by `max(fused_score, propagated_score)` and nothing else.
  That is **inert**. `relevance_score` is overwritten by the reranker afterwards, so if the
  wanted note was already inside the top-30 pool — which it usually is — the output is
  byte-identical and the feature does nothing at all.
- Admission was independently broken: fusion min-max scales into [0,1], so the 30th direct
  candidate sits around 0.5–0.65 while a realistic propagated score is ≤0.28. Graph candidates
  would essentially never enter the pool, and *never* for hub-adjacent notes — precisely the
  case being targeted.
- Reserved slots had to cover **every** graph-reached candidate, not merely ones absent from
  fusion: a neighbour sitting at fused rank 45 is exactly as absent from the reranker as one
  with no fused score at all.

### 3. Contract and surfaces

- CLI schema **v2 → v3**. Candidates carry a nullable `graph` block
  (`seed_note_id`, `seed_path`, `hop_count`, `propagated_score`); `scores.fused` is `0.0` for a
  candidate reached only by expansion, and `scores.final` includes the bonus when one applied.
- `why` stays a string, with a deterministic `linked from <note>` variant.
- `stats` and `sync` report `graph_status` / `graph_nodes` / `graph_edges` /
  `graph_schema_version`. Integrity logic lives in `vault_spider/index/graph.py`, shared by the
  writable `IndexStore` and the read-only `DatabaseReader` that actually serves `stats`.
- Web results mark an expanded hit `↗ linked`. MCP needs no new arguments.
- Constants are internal — no CLI, MCP or web flags this release.

---

## c) Evaluation

### Method

**One index, copied, with the feature disabled on the copy.** Both corpora were synced once,
the directory duplicated, and the `graph_*` collection metadata stripped from the duplicate so
it reads `missing`. Because expansion is strictly gated on `graph_status == "ok"`, and the
ineligible path performs no concat, uses the same pool, and adds `+0.0`, the control is
byte-identical to pre-feature behaviour.

This is tighter than comparing git revisions: identical code, identical model IDs, identical
embeddings, even a shared query-embedding cache. The only difference is the graph.

The public control reproduced the committed baseline exactly — 0.8333 / 0.8816 / 0.9306 against
a recorded 0.833 / 0.882 / 0.931 over the same 24 scored queries. The realistic control lands at
0.96 / 0.9293 / 0.94 against a recorded 0.958 / 0.9315 / 0.938, the small difference explained by
the scored set growing from 24 to 25 with the addition of q031. Neither shows model drift, which
is the evidence that the deltas below are real.

### Results

Retrieval stage, `--mode thorough --granularity mixed --k 5`.

| | public complete@5 | public nDCG@5 | realistic complete@5 | realistic nDCG@5 | realistic MRR |
|---|---|---|---|---|---|
| graph off | 0.8333 | 0.8816 | 0.96 | 0.9293 | 0.94 |
| graph on | 0.8333 | **0.8714** | 0.96 | **0.8921** | **0.8867** |

**Completeness — the metric the feature was built to move — did not move on either corpus.**
nDCG fell on both; MRR fell on the realistic set.

### Per-query

The one designed win:

| query | before | after | |
|---|---|---|---|
| realistic **q031** `graph_direct` | 0.8772 | **1.0** | `NAS Snapshot Replication` reached purely over the link, promoted to rank 1 |

The flagship case, unchanged:

| query | before | after | |
|---|---|---|---|
| public **q023** `graph_direct` | 0.6131 | 0.6131 | identical; still misses `Overview#Objectives` |

Expansion demonstrably *fired* on q023 — `applied: true`, 5 neighbour notes, 15 entries added,
10 admitted to the rerank pool — and changed nothing.

The costs:

| query | before | after | |
|---|---|---|---|
| realistic **q001** `known_item` | 1.0 | **0.5** | correct note pushed rank 1 → 3 |
| realistic **q023** `known_item` | 1.0 | **0.5** | correct note pushed rank 1 → 3 |
| realistic q007 | 0.9386 | 0.8855 | |
| public q007 | 0.6643 | 0.4525 | a required section pushed out of the top 5 |
| public q005, q006 | — | slight drop | reordering within the matched set |

### A measurement note

The plan's acceptance gate (complete@5 > 0.875, nDCG@5 ≥ 0.894) quoted **superseded** numbers,
predating the 2026-07-19 corpus growth. The true contemporaneous baseline is 0.833 / 0.882. The
gate as written was unreachable by construction, independent of anything this feature did.

---

## d) Why the a-priori reasoning didn't pan out

### 1. Granularity mismatch — the decisive one

Edges are note-level. Scoring, labels, and the reading experience are all **section**-level.

q023 is the clean demonstration. Its required evidence is
`Atlas Sensor Hub Overview#Objectives`. The Overview note was **already in the top 5 before
expansion** — at `#System outline`. The graph brought in a note that was never missing. The
failure was the reranker choosing the wrong *heading* within the right note, and note-level
expansion is structurally incapable of addressing that.

This also means **no hyperparameter setting could have rescued q023.** Seeds, neighbour cap,
decay and weight all change *which notes* enter the pool. q023 never needed a different note.

### 2. The corpora are too small for reach to be the bottleneck

`top_k = 150` against a 36-note (public) or 57-note (realistic) corpus means fusion sweeps
**the entire corpus** into the candidate frame. Every note is already a candidate. Recall of
notes is already 100%.

A mechanism whose entire value proposition is *reaching notes that scoring cannot reach* has
nothing to contribute when nothing is unreachable. All it can do is reorder — and reordering
is where the risk lives, not the reward. The feature's value should scale with corpus size
relative to the candidate pool; both eval corpora sit far below that threshold. The live vault
(667 notes, 2 900 entries) is the regime where the premise might actually hold, and it was
never measured.

### 3. The precision guard doesn't guard the thing that broke

The (a) argument was "the reranker demotes irrelevant neighbours, so precision is safe." That
holds for *pool widening*. It does not hold for the **post-rerank bonus** — and the bonus had to
be added, because pool widening alone is inert (see b.2).

The bonus is applied *after* the cross-encoder has spoken, so it can and does override the very
judgement that was supposed to be the safeguard. The precision argument in (a) silently stopped
applying the moment the design was corrected to be non-inert. That tension is intrinsic, not an
implementation slip: a signal that only reorders the pool changes nothing, and a signal that
survives the reranker is by definition unguarded by it.

### 4. It is applied uniformly to queries that cannot benefit

`known_item` queries have one unambiguous answer, usually already at rank 1. Expansion offers
them nothing and charges them anyway: two such queries lost half their nDCG apiece, their
correct note displaced to rank 3 by inserted neighbours. The feature has no notion of "this
query doesn't need help."

Roughly: the wins are concentrated in a small class of multi-note queries; the costs are spread
across every query. With only ~1 query per corpus in the winning class, the sum is negative.

### 5. The metric is far more sensitive to the harm than to the benefit

With 2–3 labelled items inside the top 5, inserting one candidate above a gold item can halve
nDCG. Completeness — the metric expansion targets — is comparatively insensitive, and is
capped: it cannot exceed 1.0 for queries already complete. So the design perturbs a
rank-sensitive metric in order to move an insensitive one, on a corpus where the insensitive one
was already near ceiling (0.96 realistic).

### 6. Degree damping is weakest exactly where the motivation was strongest

The motivating picture was a well-linked vault with MOC/hub structure. But damping divides by
√(ln·ln) of both degrees, so **the better-connected the hub, the smaller the propagated score.**
The mechanism is strongest for sparse leaf-to-leaf links and weakest for the hub-mediated
structure the argument leaned on. The guard against hub flooding and the source of hub value
are the same term.

### 7. Target selection preceded diagnosis

q003, q010 and q023 were adopted as targets because they were the failing queries — not because
their failures had been shown to be note-reachability failures. Two of three were known in
advance to be unreachable (q003 shared-hub, q010 unlinked orphans). The third turned out not to
be a reachability failure at all. The feature was aimed at a target set that, on inspection,
contained no valid targets.

---

## e) What to tune, and what to try instead

### Hyperparameters, in descending order of expected value

| constant | current | direction | rationale |
|---|---|---|---|
| `GRAPH_WEIGHT` | 0.15 | **↓ 0.02–0.05** | At ~0.017 per rank position, 0.15 × 0.5 shifts ~4 positions — enough to displace a rank-1 answer. This is the single biggest lever on the observed harm. |
| `GRAPH_RESERVED_POOL_SLOTS` | 10 | **↓ 2–3** | 10 of a 30-slot pool is a third of the reranker's attention spent on links. |
| `GRAPH_SEED_COUNT` | 10 | ↓ 5 | Seeds 6–10 are weak fused hits; their neighbours are mostly noise. |
| `GRAPH_NEIGHBOR_CAP` | 20 | ↓ 10 | |
| `GRAPH_DECAY` | 0.5 | ↓ 0.25 | |
| `rerank_top_k` | 30 | ↑ 40 | Enlarging the pool instead of reserving within it avoids displacement entirely, at reranker cost. |
| damping function | `√(ln·ln)` | — | See d.6; consider damping the *neighbour* degree only, leaving hub-seeded propagation intact. |

### Conditional application — the highest-leverage change

Most of the measured damage is on queries that never needed expansion. Cheap gates:

- **Dominance gate.** Skip expansion when the top fused candidate leads the second by a wide
  margin — the signature of a known-item lookup. This alone would have prevented the two
  1.0 → 0.5 regressions.
- **Flatness gate.** Apply expansion only when the top-k fused scores are close together, the
  proxy for "no single note answers this."
- **Near-miss targeting.** Boost only neighbours that *also* appear in fusion at rank ~6–20 —
  i.e. corroborated by two independent channels — rather than admitting unranked notes.

### Alternative approaches, most promising first

1. **Use the graph for synthesis context, not retrieval ranking.** Retrieve exactly as today,
   then pull linked neighbours of the cited notes into the answer model's context window. This
   captures the entire recall thesis from (a) — the answer gets the retention policy — while
   touching no ranking metric, so it cannot regress nDCG or MRR by construction. Given that the
   observed harm is *all* ranking harm and the observed benefit is *all* evidence completeness,
   this looks like the right shape for the idea.

2. **Section-level edges.** The direct fix for d.1, the decisive failure. Attribute each link to
   the section it appears in and expand section → section. The pieces exist:
   `extract_wikilinks` already returns line numbers and `split_sections` carries
   `line_start`/`line_end`, so the attribution is mechanical. This would let expansion address
   "wrong heading in the right note", which is the failure actually present in the corpus.

3. **Index-time link context.** Append linked-note titles to the embedded document text so the
   graph influences the *embedding* rather than the ranking. Cheaper at query time, inherently
   precision-preserving, and it makes the signal available in `fast` mode too.

4. **Personalized PageRank** seeded by fused scores. Handles the shared-hub / two-hop case
   (q003) that one hop cannot, still deterministic. Worth attempting only after d.2 is
   addressed — more reach does not help when reach is not the bottleneck.

5. **Backlink count as a static authority prior**, query-independent, folded into fusion rather
   than applied post-rerank. Much smaller blast radius.

6. **Link provenance as a reranker input** rather than a post-hoc bonus — mention the linking
   note in the reranked document text, or use the graph only to break ties. Keeps the
   cross-encoder as the genuine final authority, resolving the tension in d.3.

### Evaluation work this needs regardless

- **Measure on a corpus large enough for reach to bind.** Both eval corpora are smaller than the
  candidate pool. `eval-live/` (51 notes) has the same problem. A corpus of several hundred
  notes, or a smaller `top_k`, is required before any graph result is meaningful.
- **Fix the q023 label or the note.** If `Overview#System outline` genuinely answers the query,
  the label is wrong; if not, the note wants re-sectioning. Either way it should stop being
  cited as a graph target.
- **Add known-item queries as an explicit regression slice.** They are where the harm landed and
  nothing was watching them.
- **Keep the strip-metadata A/B.** It is materially better than cross-revision comparison and
  costs one directory copy.

---

## Appendix: files changed

Index and corpus: `corpus/frontmatter.py`, `corpus/loader.py`, `corpus/vault.py`,
`index/graph.py` (new), `index/store.py`, `index/reader.py`.
Retrieval: `retrieval/searcher.py`, `retrieval/evidence.py`.
Contract and surfaces: `cli.py`, `web/format.py`, `web/templates/_results.html`,
`web/static/app.css`.
Eval: graph slices on public q003/q010/q023 and realistic q017; new realistic q031;
`expected_query_count` 30 → 31.
Docs: `README.md`, `AGENTS.md`, `skills/vault/references/commands.md`,
`tools/build_codebase_map.py`.

576 tests pass, ruff clean. Committed to branch `graph-augmented-retrieval`; not merged, and the
feature is enabled by default in that code — it should not reach `main` in this state without
either the tuning pass in (e) or an explicit off-by-default gate.
