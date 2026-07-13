---
name: vault
description: >-
  Search, answer from, and maintain the user's Obsidian vault using
  vault-rag (retrieval / synthesis / lint / enrich) and obsctl (safe note
  mutations). Use when the user asks what they know or wrote about something, or
  wants notes found, captured, enriched, filed, or vault health checked.
---

# vault

Thin orchestration over three JSON CLIs. This file encodes **when to use which tool** — it holds
no ranking, YAML, or path logic (that lives in the CLIs). Every CLI prints one JSON envelope;
**check the `"ok"` field, never exit codes.**

## Tools & preconditions

- **`vault-rag`** — run from the repo via `uv run vault-rag ...`; needs `.env` (OpenRouter) and
  `config.yaml` (vault root, skip dirs). Read-only against the vault except `synthesize --save`.
  The corpus root comes from `config.yaml` (`vault.root`), so `--root` can usually be omitted.
- **`obsctl`** — on PATH; **needs the Obsidian app running.** All vault mutations go through it.
- **`obsidian`** — the official CLI; read-only use here (`read`, `backlinks`, `unresolved`, `tags`).
  Errors print `Error:` text with exit 0.

`vault-rag schema` and `obsctl schema` describe every command; full flags are in
[references/commands.md](references/commands.md).

## Decision rules

**Find notes vs. answer a question**
- User wants to *find or open* notes → `vault-rag retrieve`; present the candidate list.
- User asks a *question* → `vault-rag synthesize`; present the answer with citations.

**Retrieval depth**
- Proper nouns, note titles, "where did I write X" → `retrieve --mode fast --granularity document`.
- Conceptual / multi-note, "what do I know about X" → `--mode thorough --granularity mixed`.
- Escalate fast → thorough when fast results look off-topic (no title/keyword overlap).

**Abstention** — if `synthesize` returns `abstained: true`, tell the user what's missing and offer
a broader retrieve. Never pad an abstained answer.

**Saving distilled notes** — offer `synthesize --save` only when the answer is confidence
high/medium AND cites ≥2 notes AND the question is reusable (research-y, not operational). Ask
first; never save silently. After saving, remind that `vault-rag sync` indexes it.

**Capture & enrichment** — new material → capture into `Inbox/`, then offer enrichment. Both are
multi-step and have a fixed apply order and frontmatter policy: follow
[references/capture-and-enrichment.md](references/capture-and-enrichment.md).

**Maintenance** — "vault health / broken links / cleanup" → `vault-rag lint --root <vault>`;
summarize counts, list top findings. Fixes are the user's decisions. Remind about `vault-rag sync`
after any batch of captures or edits (or run it if they agree).

## Mutations — hard rules

- Every `obsctl` mutation: run with `--dry-run` first, show the diff, then apply on confirmation.
- Never construct a frontmatter patch containing `id`, `created`, `updated`, or `tags`.
- Move/rename only with explicit user approval of the exact destination.
- Anything `obsctl` reports as `ambiguous_target` or `contract_violation` → surface verbatim; do
  not work around it.

## Output conventions

- Retrieval hits: one `title — path` line each with the one-line `why`.
- Synthesis answers: render citations as `[[title]]` references the user can open.
- Errors: quote `error.type: message` from the envelope rather than paraphrasing.
