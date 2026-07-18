# Vault Spider public evaluation corpus

This directory contains a fictional, public-safe Obsidian-style vault and a labelled query set for
evaluating Vault Spider. It contains no notes copied from a private vault, no real hostnames or IP
addresses, and no personal or employer information.

## Layout

- `public_vault/` — 26 Markdown notes with stable frontmatter IDs.
- `golden_queries.jsonl` — one labelled query per line.
- `eval-config.yaml` — portable UTC timestamp policy for this corpus.

The corpus is designed to exercise known-item lookup, semantic paraphrase, multi-note synthesis,
section selection, aliases, temporal preference, conflicting old/current notes, metadata filters,
ambiguity, and abstention. Paths and headings in the golden set are intentionally stable evaluation
identifiers; changing them requires updating the labels.

## Try it with the current CLI

Use an isolated Chroma directory so the benchmark never touches the live-vault index:

```bash
VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider sync \
  --root eval/public_vault \
  --reset \
  --chroma-path /tmp/vault-spider-public-eval

VAULT_SPIDER_CONFIG=eval/eval-config.yaml \
./bin/vault-spider retrieve \
  --query "Which component buffers readings during an outage?" \
  --mode thorough \
  --granularity mixed \
  --chroma-path /tmp/vault-spider-public-eval
```

The corpus intentionally includes standalone distractor notes, so `lint` reports some orphans.
With `eval-config.yaml`, it should report no broken links, duplicate identities, missing fields, or
invalid timestamps.

`golden_queries.jsonl` is the input contract proposed by the Obsidian note “Vault Spider
Evaluation Specification”. A future `vault-spider eval validate` command should validate it, and
`vault-spider eval run` should execute it and emit a versioned results envelope.

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
