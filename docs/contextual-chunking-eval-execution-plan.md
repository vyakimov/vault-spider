# Contextual Chunking Evaluation Execution Plan

## Purpose

This plan measures two separate questions on the public `eval/` corpus:

1. Does the new Markdown-aware chunking and mixed retrieval implementation improve retrieval over
   the original implementation?
2. Starting from that smarter implementation, does adding one canonical note summary to each
   document/chunk improve retrieval further?

The comparison must isolate those effects:

```text
original implementation
        │
        │ code change only
        ▼
smarter chunking, no summaries
        │
        │ summary context only
        ▼
smarter chunking + note summaries
```

Do not treat the contextual result versus the original result as the only comparison. The first
delta attributes changes to chunking/retrieval; the second attributes changes to summaries.

This is a retrieval-stage evaluation. Synthesis judging is out of scope unless requested after the
retrieval results are understood.

## Why Use Separate Git Worktrees?

The original implementation is the current `main` commit:

```text
5c78cf329bdb85d26a13bfdba73de5cc9f533a43
```

The smarter chunking/context implementation currently exists as uncommitted changes in the main
working directory. Repeatedly switching one working directory between `main` and a feature branch
would be risky because:

- the feature implementation is presently a large dirty worktree;
- summary jobs and canonical eval summaries are being generated concurrently under ignored
  `eval/context-data/`;
- each implementation needs its own dependencies/configuration context while the eval is running;
- accidental branch switching could obscure which code produced an index or result;
- the original and smarter implementations must never reuse a Chroma collection.

Use two worktrees instead:

```text
<development-parent>/vault-spider/                 feature/contextual-chunking
<development-parent>/vault-spider-original-eval/   main at 5c78cf3
```

Both code versions remain available simultaneously. Commands can be rerun, commit hashes can be
recorded, and each result can be traced to the implementation that produced it.

## Current State the Executing Agent Must Preserve

At the time this plan was written:

- The primary worktree is on `main` at `5c78cf3`.
- Smarter chunking, mixed retrieval, canonical summary storage, and persistent eval configuration
  changes are uncommitted in that worktree.
- Manual summary generation is ongoing in `eval/context-data/jobs/`.
- Completed canonical summaries will live in `eval/context-data/summaries/`.
- `eval/context-data/` is gitignored and must not be staged.
- `docs/data_map.html` is an unrelated untracked file; do not stage or remove it without explicit
  user direction.
- The network-free suite most recently passed with 585 tests.

Before doing anything, run:

```bash
git status -sb
git branch --show-current
git rev-parse HEAD
```

If reality differs, adapt without resetting, discarding, overwriting, or silently staging existing
user changes.

## Fixed Experiment Settings

Every variant must use:

```text
dataset:       eval
stage:         retrieval
mode:          thorough
granularity:   mixed
n:             10
k:             5
collection:    vault_notes
corpus:        eval/public_vault
```

All three runs must use the same:

- public eval corpus and labels;
- OpenRouter embedding model;
- OpenRouter rerank model;
- API/base URL configuration;
- skip directories and ignored tags;
- machine environment, as far as practical.

The eval result records the embedding and rerank model names. Abort the comparison if those fields
differ between result files.

The contextual configuration keeps `contextual_bm25: false`. Therefore the second delta measures
the effect of summaries on dense retrieval and reranking, not a simultaneous BM25 policy change.

## Persistent Artifact Layout

Disposable indexes and canonical summaries remain local and gitignored:

```text
eval/context-data/
├── chroma-original/
├── chroma-baseline/
├── chroma-contextual/
├── jobs/
└── summaries/
```

Raw eval results and the final analysis must be permanent, reviewable repository artifacts:

```text
eval/results/contextual-chunking-v1/
├── README.md
├── original-main.json
├── smarter-chunking.json
├── smarter-plus-context.json
└── comparison.md
```

Commit this results directory on the feature branch. Do not save canonical result files only under
`/tmp` or `eval/context-data/`.

The result JSON includes absolute dataset paths. Before committing, replace only:

- `dataset.path` with `eval/dataset.yaml`;
- `dataset.corpus_root` with `eval/public_vault`.

Do not alter metrics, run settings, query scores, timestamps, or model identifiers.

## Phase 1: Put the Implementation on a Feature Branch

From the primary dirty worktree:

1. Confirm `HEAD` is `5c78cf3`.
2. Create the feature branch without discarding the dirty changes:

   ```bash
   git switch -c feature/contextual-chunking
   ```

3. Review the full diff and run:

   ```bash
   uv run ruff check .
   uv run pytest -q
   uv run pyright vault_spider
   git diff --check
   ```

4. Stage only the contextual-chunking implementation, tests, configs, generated codebase maps, and
   documentation. Do not use an unreviewed `git add -A`; specifically exclude:

   ```text
   eval/context-data/
   docs/data_map.html
   ```

5. Commit the implementation and record the resulting feature commit SHA. Do not push unless the
   user requests it.

The feature commit is essential: otherwise the smarter results cannot be traced to an immutable
code state.

## Phase 2: Create the Original-Code Worktree

After the primary directory is on the feature branch:

```bash
git worktree add ../vault-spider-original-eval main
```

Verify the new worktree:

```bash
git -C ../vault-spider-original-eval rev-parse HEAD
git -C ../vault-spider-original-eval status -sb
```

Its SHA must be `5c78cf329bdb85d26a13bfdba73de5cc9f533a43`, and it must be clean.

The original worktree will not contain `.env`. Make the existing secrets available without copying
or committing them. A local gitignored symlink is acceptable:

```bash
ln -s /Users/vy/Documents/Development/vault-spider/.env \
  ../vault-spider-original-eval/.env
```

If the repository has moved, resolve the primary worktree path first. Never print `.env` contents.

## Phase 3: Validate Corpus Identity

From both worktrees, validate the dataset:

```bash
VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider eval validate --dataset eval
```

Also verify that the feature branch did not alter evaluation inputs:

```bash
git diff --quiet main...feature/contextual-chunking -- \
  eval/public_vault eval/dataset.yaml eval/golden_queries.jsonl
```

Any difference in those paths invalidates the A/B comparison and must be investigated before
embedding.

Expected public corpus counts:

```text
notes:       240
queries:      44
answerable:   38
unanswerable:  6
```

## Phase 4: Run the Original Implementation

Run from `../vault-spider-original-eval`. Use explicit absolute output/index paths because the old
configuration predates the persistent eval layout.

First create the permanent results directory in the feature worktree:

```bash
mkdir -p /Users/vy/Documents/Development/vault-spider/eval/results/contextual-chunking-v1
```

Build the original index:

```bash
VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider sync \
  --root eval/public_vault \
  --reset \
  --chroma-path \
  /Users/vy/Documents/Development/vault-spider/eval/context-data/chroma-original
```

Run the original eval:

```bash
VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider eval run \
  --dataset eval \
  --chroma-path \
  /Users/vy/Documents/Development/vault-spider/eval/context-data/chroma-original \
  --stage retrieval \
  --mode thorough \
  --granularity mixed \
  -n 10 \
  --k 5 \
  --out \
  /Users/vy/Documents/Development/vault-spider/eval/results/contextual-chunking-v1/original-main.json
```

The interrupted earlier attempt may have left `chroma-original` partially populated. `--reset` is
mandatory and safely rebuilds it.

Historical sanity values recorded for this corpus are:

```text
complete@5:                0.7632
mean evidence recall@5:    0.8640
mean nDCG@5:               0.6794
MRR:                       0.6823
```

The rerun need not be byte-identical because an external reranker can vary, but a large unexplained
difference requires checking model names, corpus identity, and configuration before continuing.

## Phase 5: Run Smarter Chunking Without Context

Return to the feature worktree. Its committed `eval/eval-config.yaml` must specify:

```yaml
index:
  chroma_path: context-data/chroma-baseline
  contextual: false
```

Build and score:

```bash
VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider sync --reset

VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider eval run \
  --dataset eval \
  --stage retrieval \
  --mode thorough \
  --granularity mixed \
  -n 10 \
  --k 5 \
  --out eval/results/contextual-chunking-v1/smarter-chunking.json
```

This is the only result that should be compared directly with `original-main.json` to attribute a
delta to smarter chunking/mixed retrieval.

## Phase 6: Finish and Import Manual Summaries

Do not call OpenRouter to generate summaries. The contextual config uses:

```yaml
index:
  contextual: true
  context_source: manual
  context_path: context-data/summaries
  contextual_bm25: false
```

Wait until the user’s summary-generation process has completed every JSON job under
`eval/context-data/jobs/`.

Before import, audit the jobs:

- exactly 240 job files;
- every `summary` is a non-empty string;
- every summary is within the 1,200-character contract;
- `generated_by` identifies an LLM/coding agent rather than falsely claiming human authorship;
- no note body, note ID, fingerprint, title, or job schema field was changed.

Import is all-or-nothing:

```bash
VAULT_SPIDER_CONFIG=eval/eval-contextual-config.yaml \
./bin/vault-spider context import
```

Then:

```bash
VAULT_SPIDER_CONFIG=eval/eval-contextual-config.yaml \
./bin/vault-spider context status
```

Required gate:

```text
ready_count:   240
missing_count:   0
stale_count:     0
```

If import fails or coverage is incomplete, stop and repair the jobs. Do not silently evaluate
partial context.

## Phase 7: Run Smarter Chunking With Context

Build the isolated contextual index:

```bash
VAULT_SPIDER_CONFIG=eval/eval-contextual-config.yaml \
./bin/vault-spider sync --reset
```

Inspect the sync envelope. Require:

```text
context.source:          manual
context.missing_notes:   0
context.stale_notes:     0
context.failed_notes:    []
context.coverage:        1.0
```

Manual mode makes no summary-generation chat calls. Sync still calls the configured embedding
provider because the summary-enriched document/chunk text needs new vectors.

Run the identical eval:

```bash
VAULT_SPIDER_CONFIG=eval/eval-contextual-config.yaml \
./bin/vault-spider eval run \
  --dataset eval \
  --stage retrieval \
  --mode thorough \
  --granularity mixed \
  -n 10 \
  --k 5 \
  --out eval/results/contextual-chunking-v1/smarter-plus-context.json
```

## Phase 8: Analyze the Results

For each result, extract:

- `aggregates.retrieval.mean_ndcg_at_k`;
- `aggregates.retrieval.mean_group_recall_at_k`;
- `aggregates.retrieval.complete_rate_at_k`;
- `aggregates.retrieval.mrr`;
- all `by_category` retrieval aggregates;
- all `by_slice` retrieval aggregates;
- query-level retrieval scores for regressions and improvements.

Create `comparison.md` with:

1. A table of all four overall metrics for all three variants.
2. Absolute and percentage deltas:
   - smarter minus original;
   - contextual minus smarter.
3. The five largest query improvements and regressions for each delta.
4. Category and slice regressions, even if the overall average improved.
5. Model names, commit SHAs, timestamps, corpus counts, context coverage, and exact commands.
6. A conclusion answering separately:
   - Did smarter chunking improve retrieval?
   - Did summaries improve over smarter chunking?

Use evidence-group recall as a guardrail. The original plan explicitly requires investigation when
mean group recall drops, even if nDCG improves. Also inspect short-section or BM25-heavy query
regressions rather than relying only on aggregate means.

If a delta is very small or surprising, rerun the affected variant before drawing a conclusion;
`thorough` mode uses an external reranker and can have some variance. Save reruns as additional
files rather than overwriting the canonical first run.

## Phase 9: Make the Results Permanent

Create `eval/results/contextual-chunking-v1/README.md` containing:

- original commit SHA;
- feature commit SHA;
- summary generation source/model if known;
- embedding and rerank model names;
- corpus and query counts;
- date/time of each run;
- the exact three commands;
- links to the result JSON files and `comparison.md`;
- a statement that indexes/summaries remain under gitignored `eval/context-data/`.

Normalize only the two absolute dataset location fields in each JSON result, as described above.
Then validate:

```bash
python -m json.tool eval/results/contextual-chunking-v1/original-main.json >/dev/null
python -m json.tool eval/results/contextual-chunking-v1/smarter-chunking.json >/dev/null
python -m json.tool eval/results/contextual-chunking-v1/smarter-plus-context.json >/dev/null
git diff --check
```

Stage only the permanent result artifacts and any intentionally updated evaluation documentation.
Commit them on `feature/contextual-chunking`. Do not stage Chroma files, query caches, manual jobs,
canonical summaries, `.env`, or unrelated files.

## Cleanup

After results are committed and no reruns are needed:

- the original worktree may be removed with `git worktree remove`, but only after confirming it is
  clean;
- remove only the `.env` symlink in that worktree, never the source `.env`;
- keep all three Chroma directories and canonical summaries for reproducibility unless the user
  explicitly requests deletion;
- do not merge or push the feature branch without explicit user direction.

## Completion Checklist

- [ ] Smarter implementation committed on `feature/contextual-chunking`.
- [ ] Original worktree pinned to `5c78cf3`.
- [ ] Eval inputs identical between worktrees.
- [ ] Original index rebuilt and result saved.
- [ ] Smarter no-context index rebuilt and result saved.
- [ ] 240 LLM-generated summaries imported and ready.
- [ ] Contextual sync reports 100% coverage.
- [ ] Contextual result saved with identical eval settings.
- [ ] Model identifiers match across all three result files.
- [ ] Overall, category, slice, and query-level deltas analyzed.
- [ ] Absolute dataset paths normalized in committed JSON.
- [ ] Permanent result README and comparison committed.
- [ ] Gitignored indexes/summaries preserved locally.
