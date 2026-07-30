# Graph-Augmented Retrieval: design discussion

A conversation about [graph-augmented-retrieval-report.md](graph-augmented-retrieval-report.md)
(2026-07-28, Victor + Claude). The report documents the graph-layer attempt and why it made
retrieval worse; this discussion is a design-level critique of it and sketches where to go next.

---

## Q1: High-level design analysis of the report — can anything in the design be improved?

The report is an unusually honest post-mortem — the granularity mismatch (d.1) and the
bonus-vs-reranker tension (d.3) are correctly identified, and the d.2 retest is exactly how a
null result should be handled. The critique below is additive, not a re-litigation.

### 1. The root design error: a query-independent signal was injected as a query-relevance score

A wikilink asserts "these notes belong together" — it knows nothing about any particular query.
The propagated score is just `seed_relevance × edge_discount`; it contains zero information
about whether the *neighbour* answers the *question*. The only component that ever evaluates
query × neighbour-text is the cross-encoder, and the post-rerank bonus overrides precisely that
judgement with the query-blind term. The report's d.3 describes this as a tension between
inertness and unguardedness, but it is stronger: a category error, and it predicts the exact
observed pattern — diffuse harm on every query (relatedness ≠ relevance most of the time) and
wins only where they happen to coincide. Any retry that keeps "graph score competes with
relevance score" will reproduce this. The report's alternative #1 (use the graph for synthesis
context, not ranking) is the right conclusion because it routes the relatedness signal to the
one place where relatedness *is* the question being asked.

### 2. The eval never ran the ablation that separates the benign half from the harmful half

The design bundles three mechanisms: (a) widen the candidate pool, (b) reserve rerank slots,
(c) post-rerank bonus. All measurements are of the bundle. The report's own reasoning says the
harm lives in (c) plus slot displacement, while the completeness thesis only needs (a)+(b) —
get the neighbour in front of the reranker and let it judge. That variant (bonus weight = 0,
slots kept) is the only configuration for which the original precision argument in section (a)
actually holds, and it was never measured. The "mechanism is subtractive" verdict is therefore
about the bundle, not the thesis. One cheap ablation would tell you whether the reranker, given
the chance, ever picks up a graph-reached note. If it doesn't, the case is truly closed.

### 3. The evaluation measures the wrong layer for the motivating use case

The flagship example — "describe the backup chain and retention" — is judged by whether the
*answer* contains the retention policy, but the entire eval is retrieval-stage nDCG@5 /
complete@5 at fixed k=5. A fixed-k ranking metric structurally cannot credit "the answer model
had the context it needed" and maximally punishes insertion — d.5 notes the asymmetry but
treats it as bad luck rather than a mismatch between metric and goal. If alternative #1 is
pursued, an answer-level completeness eval is needed first, ahead of everything currently in
the report's "evaluation work this needs regardless" list.

### 4. Two smaller design points

- **Fixed-k eviction is a choice, not a law.** Every completeness loss in d.2 was an eviction.
  A "fill, don't displace" rule — graph candidates may only replace results below an absolute
  reranker-confidence threshold, or expansion enlarges k rather than competing within it —
  caps the downside at zero by construction and would have prevented the q037/q009/q001/q023
  regressions outright. A stronger version of the dominance gate in (e).
- **A single global `GRAPH_WEIGHT` is ill-posed.** Fused scores are min-max normalized *per
  query*, so the propagated score's magnitude means different things on different queries, and
  it is then added to a cross-encoder score on yet another scale. Tuning 0.15 down to 0.03
  tunes an average over incommensurable scales — one more reason the tuning path is rightly
  deprioritized.

**On the report's own recommendations:** alternative #1 (synthesis context) is the right first
move and dissolves points 1 and 4 entirely; section-level edges (#2) is the right fix *if*
graph-in-ranking is ever revisited, but only after the ablation in point 2 shows the reranker
cooperates. Seconded: the branch has the feature on by default and shouldn't merge that way.

---

## Q2: Why is the post-rerank bonus necessary at all? Why can't the reranker be the final step?

Short answer: the bonus isn't logically necessary — it compensates for the fact that the
reranker fails on the motivating case for *the same reason* the first-stage retrieval does.
Making the reranker final is coherent, but it quietly gives up on the query the feature was
built for.

Walk the flagship example with the reranker final. The target note,
`NAS Snapshot Replication`, contains no query vocabulary — not "pantry," not "app," not
"retention." That's why BM25 and embeddings miss it. But a cross-encoder is also just a
function of `(query text, candidate text)`. Hand it that pair and it sees a question about a
pantry app's backup chain next to a note about NAS snapshot scheduling, and it scores the pair
low — correctly, by its own lights, since nothing in the text connects them. The connective
evidence ("the app's plan links here for its backup path") lives on the *edge*, and the
reranker never sees the edge. So with reranker-as-final-arbiter, graph expansion escorts the
note into the pool and the reranker escorts it right back out.

That's the trap the design was in, visible in the report's history (b.2): the original plan
*was* essentially "widen the pool, let the reranker decide," and it was found to be inert. The
bonus was the escape hatch — a way to make the link signal survive to the final ranking. But it
survives by being applied *after* the reranker, i.e. by overruling it, which is where all the
measured damage comes from. The design was stuck choosing between an inert feature and an
unguarded one.

Two caveats to "reranker-final is inert":

1. **There is a middle class of queries where it isn't inert**: neighbours that *are* textually
   relevant to the query but were underscored or missed by fusion — especially now that the
   corpora are 3× the candidate pool, so top-150 no longer sweeps everything. For those, pool
   widening + reranker-final captures the win at provably zero precision cost. The existing
   data is only weak evidence against this class existing (q023's ten admitted candidates
   changed nothing, but that was a granularity failure, not a test of this).
2. **The trap has a third exit — the report's alternative #6**: give the reranker the edge as
   *input* instead of overriding its output — e.g. prepend "linked from *Plan — Flask HTMX*
   (which matched this query)" to the candidate text before cross-encoding, or include a
   snippet of the linking note's context around the link. Then the model judges the pair *with*
   the connective evidence and remains the genuine final authority.

If graph-in-ranking is revisited, the sequence: measure reranker-final (bonus = 0) to size the
middle class; if the no-shared-text class still matters, move the link signal into the
reranker's input. The post-hoc bonus was the one placement of the signal that could never be
safe — it's the only design in which the link systematically outvotes the model that actually
read the query.

---

## Q3: Could the two be combined? E.g. if the linked note is small, append/prepend it to the linking note; if large, treat it as pool widening. Or is that hacky?

Not hacky in spirit — this is essentially **transclusion-aware indexing**, a recognized pattern
(document expansion / contextual chunking are the same move). The vault's semantics support it:
when `Plan — Flask HTMX` says "backup into the [[NAS Snapshot Replication]] path," the author
is delegating detail to the neighbour; inlining that detail at index time materializes the
delegation. It lands in the right place mechanically — the retention-policy text becomes part
of what BM25 and the embedder *see* for the plan note, so the flagship query matches lexically
and semantically, no post-rerank override needed, and it works in fast mode too. It's the
report's alternative #3 taken from "append linked titles" to "append linked content."

What *is* hacky is **size as the switch**:

1. **Size is a proxy for the real criterion.** What you want to know is whether the link is a
   *dependency* (delegated detail) or a *sibling reference* (related but independent). A link
   into a large note can still delegate one small section (`[[NAS Snapshot
   Replication#Retention]]`), and a small note can be a mere see-also. Cleaner signals: the
   author's own transclusion syntax (`![[...]]` literally means "inline this here") and the
   section anchor when the link has one. A rule like "inline the linked *section* (or the whole
   note if short and unsectioned), capped at N chars" keys off structure rather than byte count
   and avoids the discontinuity where a note crossing a size threshold silently flips
   mechanisms.
2. **Provenance.** If inlined text is stored as part of the host note's document, retrieval can
   surface — and the answer model can quote — text that isn't actually in the note being cited.
   Fix: split *embedding/BM25 text* from *display text* — augment what gets indexed, store the
   original, record "includes context from [[X]]" so synthesis can cite the true source.
3. **Staleness cascade.** Today a note reindexes when its own content changes. Once neighbours'
   text is baked in, editing the retention note must dirty every note that inlines it. The
   report already fought a mild version of this (edges refreshed on unchanged content);
   content inlining makes it a real invalidation graph. Tractable — adjacency is already
   stored — but it's the main new cost.

On the "large → pool widening" half: decouple it rather than pair it. The two paths are
qualitatively different mechanisms (one changes what the index says, the other changes what the
reranker sees), so a size-based fork makes every eval result a blend of two features. Given the
branch's evidence that bare pool widening does little, the better companion for the large-note
case is the rerank-time variant from Q2: admit the neighbour to the pool and build its
cross-encoder input as *linking-note context + neighbour section*. That is the same
combination, but with one unified principle behind both halves — **the link's content travels
with the candidate to wherever relevance is judged** — rather than two unrelated fallbacks.
Small/delegated → judged at embedding time; large/independent → judged by the reranker, with
the edge in evidence.

Done that way it's not a hack — it's probably the most principled version of the whole graph
idea, because the graph stops competing with relevance scoring and starts feeding it.
