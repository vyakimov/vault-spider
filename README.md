# vault-rag

Hybrid retrieval, cited answers, and health checks for an Obsidian vault.

It indexes your Markdown notes into ChromaDB and a BM25 index, fuses the two, optionally reranks,
and answers questions **with citations back to the notes** — or abstains when the notes don't
contain the answer. Every command prints a single JSON envelope on stdout, so it is as usable by an
agent as it is by a human.

Your vault is never committed, and nothing about your particular setup is baked into the source:
paths, folder names and tag conventions all live in a gitignored `config.yaml`.

## Install

```bash
uv sync
cp .env.example .env                # OpenRouter key + models
cp config.yaml.example config.yaml  # where your vault is
```

Edit `.env` with an [OpenRouter](https://openrouter.ai/keys) key, and `config.yaml` with the path to
your vault. Then:

```bash
uv run vault-rag sync            # index the vault (embeds every note; takes a few minutes)
uv run vault-rag stats
```

## Use

```bash
# Find notes
uv run vault-rag retrieve --query "wireguard setup" --mode fast

# Answer a question, with citations — abstains rather than guessing
uv run vault-rag synthesize --query "How did I set up the VPN, and why that way?"

# Vault health
uv run vault-rag lint --format text
```

`vault-rag schema` prints the full machine-readable command and contract schema. All output is
`{"ok": true, "action", "result", "meta"}` on success and `{"ok": false, "action", "error"}` on
failure (exit 1) — **check `ok`, not the exit code.**

There is also a Streamlit UI:

```bash
uv run streamlit run scripts/streamlit_app.py
```

## How it works

A note is indexed twice: once whole (`document` granularity) and once per heading-delimited section
(`section`). Retrieval runs BM25 and embedding search over the chosen pool, fuses the rankings
(Reciprocal Rank Fusion by default), optionally reranks the top candidates with a cross-encoder, and
applies an exponential recency boost.

- `--mode fast` skips reranking; `--mode thorough` reranks.
- `--granularity document` searches whole notes; `section` searches sections; `mixed` searches the
  section pool with a cap of 3 sections per note.

Synthesis feeds the top candidates to a chat model under a strict contract: cite every claim, or
abstain. An answer that cites nothing is treated as an abstention.

## Vault health — `lint`

Read-only by default. It reports what you'd actually act on:

| check | what it finds |
|---|---|
| `dangling_targets` | unresolved `[[links]]`, ranked by how many notes want them — the best notes to write next |
| `empty_notes` | stubs, ranked by inbound links — the most-linked empty note is the most valuable to fill |
| `conflict_copies` | `Note 1.md` sitting beside `Note.md` (Obsidian sync artifacts) |
| `broken_wikilinks` | every unresolved link occurrence |
| `duplicate_ids`, `duplicate_titles` | identity collisions |
| `invalid_timestamps` | naive or unparseable `created`/`updated`/`date` |
| `orphans` | notes with no links in or out |
| `stale_distilled` | a distilled note whose sources changed after it was written |

Link resolution follows Obsidian: frontmatter links (`parents: "[[Daily Notes]]"`) are real edges,
`aliases` resolve, and `[[diagram.png]]` resolves to an attachment rather than being called broken.

Two opt-in fixers write to the vault:

```bash
uv run vault-rag lint --fix              # add MISSING id/created/updated (never edits a value)
uv run vault-rag lint --fix-timestamps   # rewrite naive timestamps as offset-aware
```

## Compounding

- `synthesize --save` persists a high-confidence, well-cited answer as a **distilled note**
  (`type: distilled`) under `vault.distilled_dir`. Distilled notes are regenerable pointers to their
  sources — raw notes always win on conflict, and `lint` flags a distilled note as stale once a
  source outranks it in age.
- `enrich` is a read-only **planner**: given a note, it retrieves the neighbourhood and proposes a
  title, a frontmatter patch, inline links and a folder. It never mutates anything; applying a plan
  is a separate tool's job.

## Configuration

Everything installation-specific is in `config.yaml` (gitignored — see `config.yaml.example`):
vault root, skipped folders, never-indexed tags, the distilled folder, the Chroma path, and the
timestamp policy. Secrets stay in `.env`.

Notes carrying `#secret` or `#ignore` (in the body or in frontmatter `tags:`) are **never indexed** —
they stay in Obsidian but never reach the vector store or an LLM. Excalidraw drawings are skipped
too: they are `.md` files whose bodies are compressed drawing data, not prose.

## Development

```bash
uv run pytest    # network-free; uses a fake provider, no API key needed
```

The package is layered: `corpus/` (load, parse, chunk) → `index/` (Chroma + BM25) → `retrieval/`
(fusion, search, evidence) → `synthesis/` (cited answers) → `compounding/` (distill, lint).
`AGENTS.md` has the full architecture.
