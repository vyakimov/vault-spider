# Vault Spider realistic synthetic evaluation corpus

A **fully synthetic, public-safe** corpus styled after a real, messy personal vault. Unlike
`eval/` (clean synthetic prose) it mimics how vault notes actually look; unlike the gitignored
live-derived dataset, **every entity here is invented** — no note is copied or derived from a
private vault, so this directory can be committed and shared.

## The fictional world

- **Marionette** — a self-hosted agent gateway (gateway on the `Bramble` VPS, node on the
  `PuddleJumper` home Mac), with a pairing runbook, permissions config, and a macOS TCC incident
  (`Photo Sync Fuckery`).
- **Lantern** — a second agent harness run in parallel, with its own conventions.
- **Homelab** — a headscale-coordinated Tailscale network (`foxglove.example` MagicDNS names,
  subnet router, tailnet-only nginx), a QNAP NAS (`LordByron`), and an archived pre-CGNAT
  port-forwarding setup for temporal-conflict queries.
- **papertrail** — an OCR pipeline (Tesseract vs PaddleOCR, a CUDA OOM incident, deskewing).
- **Larder** — a pantry app with two competing plan notes (decision queries).
- **Personal** — *The Brothers Karamazov* summary + name glossary (aliases: Mitya/Dmitri,
  Alyosha/Alexei; entity collision: Liza Khokhlakova vs Lizaveta Smerdyashchaya), a recipe,
  and two empty daily-note templates (one without a frontmatter `id`).

## Realism features carried over from the live corpus's style

Stub notes and index/MOC hubs with wikilinks (some deliberately dangling), pasted-ChatGPT
answers with Q&A structure and a typo'd command, `**bold**` and `Step N ---` headings,
non-breaking spaces inside headings, deliberate typos (`uv snyc`, `cv2.mineAreaRect` in prose),
inconsistent frontmatter, `#finalised` tags, trailing junk words, heading-less bodies labeled
via the `""` preamble convention, and empty daily templates as distractors.

## Usage

The baseline config stores embeddings persistently under
`eval-realistic/context-data/chroma-baseline`; no `/tmp` override is needed:

```bash
VAULT_SPIDER_CONFIG=eval-realistic/eval-config.yaml \
./bin/vault-spider eval validate --dataset eval-realistic

VAULT_SPIDER_CONFIG=eval-realistic/eval-config.yaml \
./bin/vault-spider sync --reset

VAULT_SPIDER_CONFIG=eval-realistic/eval-config.yaml \
./bin/vault-spider eval run --dataset eval-realistic \
  --out results.json
```

For contextual evaluation, use `eval-realistic/eval-contextual-config.yaml`. It keeps canonical
summaries in `eval-realistic/context-data/summaries` and contextual embeddings in
`eval-realistic/context-data/chroma-contextual`:

```bash
VAULT_SPIDER_CONFIG=eval-realistic/eval-contextual-config.yaml \
./bin/vault-spider context prepare

# Have Codex/Claude Code fill every job under eval-realistic/context-data/jobs.
VAULT_SPIDER_CONFIG=eval-realistic/eval-contextual-config.yaml \
./bin/vault-spider context import

VAULT_SPIDER_CONFIG=eval-realistic/eval-contextual-config.yaml \
./bin/vault-spider sync --reset

VAULT_SPIDER_CONFIG=eval-realistic/eval-contextual-config.yaml \
./bin/vault-spider eval run --dataset eval-realistic \
  --out contextual-results.json
```

All `context-data/` artifacts are persistent locally, gitignored, and separate from the public
eval and live-vault stores.

57 notes, 30 golden queries (24 answerable, 6 abstention/ambiguity). Labels follow the same
conventions as `eval/README.md`; paths and headings are stable evaluation identifiers.
