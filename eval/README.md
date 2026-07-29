# Vault Spider public evaluation corpus

This directory contains a fictional, public-safe Obsidian-style vault and a labelled query set for
evaluating Vault Spider. It contains no notes copied from a private vault, no real hostnames or IP
addresses, and no personal or employer information.

## Layout

- `public_vault/` — 240 Markdown notes with stable frontmatter IDs. The corpus is deliberately
  larger than the retrieval candidate pool (`top_k = 150` per channel, so ~300 entries at most)
  against 1138 section entries. Below that ratio every section is a candidate on every query and
  the benchmark cannot measure retrieval *reach* at all — only reordering.
- `golden_queries.jsonl` — one labelled query per line.
- `dataset.yaml` — the manifest `vault-spider eval` consumes (schema version, file locations,
  expected counts).
- `eval-config.yaml` — portable UTC timestamp policy for this corpus.

The corpus is designed to exercise known-item lookup, semantic paraphrase, multi-note synthesis,
section selection, aliases, temporal preference, conflicting old/current notes, metadata filters,
ambiguity, and abstention. Paths and headings in the golden set are intentionally stable evaluation
identifiers; changing them requires updating the labels.

## Validate and run

`vault-spider eval validate` cross-checks every label against the corpus (paths, note ids,
headings, group membership, expected counts) and fails with `contract_violation` on drift — run it
after any change to `public_vault/` or `golden_queries.jsonl`. `vault-spider eval run` validates,
executes the queries against the index, and emits a versioned results contract
(`results_schema_version: 1`).

Use an isolated Chroma directory so the benchmark never touches the live-vault index:

```bash
VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider eval validate --dataset eval

VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider sync \
  --root eval/public_vault \
  --reset \
  --chroma-path /tmp/vault-spider-public-eval

VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider eval run \
  --dataset eval \
  --chroma-path /tmp/vault-spider-public-eval \
  --out eval-results.json
```

Set `VAULT_SPIDER_CONFIG` for validate and run too: it keeps the corpus walk (skip dirs, ignore
tags) identical to what `sync` indexed. `eval run` refuses (`config_mismatch`) to score an index
whose paths do not exactly match the corpus.

## Recorded baseline

Measured 2026-07-27 on the 240-note corpus, retrieval stage, `--mode thorough --granularity
mixed --k 5`, 38 answerable queries scored:

| metric | eval (public) | eval-realistic |
|---|---|---|
| complete@5 | 0.7632 | 0.9474 |
| mean group recall@5 | 0.8640 | 0.9737 |
| mean nDCG@5 | 0.6794 | 0.8788 |
| MRR | 0.6823 | 0.8816 |

These supersede every earlier figure. The pre-expansion corpora scored ~0.88 nDCG@5, which
looked better only because every section fit inside the candidate pool — the benchmark was
near ceiling and could not register a retrieval change either way.

**Public is the discriminating corpus; eval-realistic is not.** Realistic sits near ceiling
(0.95 complete@5) because its notes are short and lexically distinctive, so BM25 alone
separates them. Size was necessary but not sufficient: a corpus can be large and still
uninformative if its notes are too easy to tell apart. Judge retrieval changes on `eval/`
and use `eval-realistic/` to check you have not broken the messy-vault cases.

The default run scores retrieval only: nDCG@k, per-group evidence recall@k, complete@k (all
required groups covered), and MRR of the first grade-3 hit, aggregated overall and per
category/slice. Unanswerable queries are skipped in this stage. `--stage synthesis` additionally
synthesizes an answer per query and scores abstention (unanswerable queries must abstain),
citation coverage of the required groups, and `gold_facts`/`forbidden_facts` via an LLM judge —
those fact metrics inherit the judge model's variance, unlike the deterministic retrieval stage.
Useful knobs: `--mode`, `--granularity`, `-n`, `--k`, `--n-context`, `--only <query-id>` for
debugging a single query.

The corpus intentionally includes standalone distractor notes, so `lint` reports some orphans.
With `eval-config.yaml`, it should report no broken links, duplicate identities, missing fields, or
invalid timestamps.

## Label conventions

Each query contains:

- `id`: stable query identifier.
- `query`: the text sent to retrieval or synthesis.
- `answerable`: whether the corpus contains enough evidence.
- `category`: one primary evaluation category.
- `slices`: additional dimensions used for segmented reporting.
- `relevant_evidence`: graded note/section labels. Grade 3 directly answers, grade 2 is required
  supporting evidence, and grade 1 is related but insufficient.
- `required_evidence_groups`: all outer groups must be satisfied; any member inside a group may
  satisfy that group.
- `gold_facts`: atomic facts expected in a complete answer.
- `forbidden_facts`: plausible but incorrect facts that should not appear.

Unanswerable queries have empty evidence and fact arrays. The evaluator should score those through
abstention metrics rather than retrieval relevance metrics.
