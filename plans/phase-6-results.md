# Phase 6 results (recorded 2026-07-07)

End-to-end capture flow verified against the **live vault** (`/Users/vy/Documents/Vault 14`),
confined to a `_e2e-test/` folder, using `obsctl` (→ running Obsidian) for mutations and
`vault-rag enrich` for planning. All test notes were trashed and the test folders removed;
the vault was left clean.

## Environment / vault option

- **Option 2** (live vault, confined to `_e2e-test/`) — not the second-vault option (that needs
  a GUI "open another vault").
- **Neighbor index caveat:** `vault-rag enrich` read each note's text from the live vault
  (`--root "/Users/vy/Documents/Vault 14"`) but drew *neighbors* from the existing dev index
  (`chroma_db`, built from `./input/Vault 14`, a slightly older snapshot of the same vault).
  Re-embedding the full live vault into a fresh collection was out of scope (cost/time). This is
  why the flow's optional "step 6: `retrieve` finds the note at its new path" was **not** verified
  here — the E2E notes live in the live vault, which isn't the indexed corpus. The distilled-note
  round-trip (step 7) was already verified in Phase 3 against the dev corpus.

## Frontmatter-at-capture answer (the phase's open question)

Probe: `obsctl create-note` a note **without** frontmatter, then read it back.

- **Templater does NOT fire on CLI-created notes** — no `id`/`created` were added. So
  `obsctl create-note` **must** supply `id` (a fresh ULID) and `created`/`updated` in
  `--frontmatter`. The skill/capture flow mints these.
- The **`update-time-on-edit` plugin DOES fire on CLI writes** — a bare CLI-created note got
  `updated` stamped automatically (consistent with Phase 0 V4). This is why obsctl's
  `manage_updated` default is `false`.

## Test matrix (all PASS)

| Test | Input | Plan (confidence) | Result |
|---|---|---|---|
| T1 | interview transcript | `type: transcript`, `source_type: transcript`, 3 inline links, 1 related (high) | id/created preserved through capture→merge→add-links→insert-related→rename; renamed to "OpenClaw Interview Transcript.md" |
| T2 | research dump | conservative title, mostly related (medium) | id/created preserved |
| T3 | web clipping (`--source-type web --source-url ...`) | `source_type: web` + `source_url` + `type: reference` (medium) | patch applied; id/created preserved |
| T4 | manual note (`type: idea`, pre-existing `[[OpenClaw]]`, `custom_probe: keepme`) | empty patch, one new link (high) | **type `idea` NOT overwritten**; **pre-existing `[[OpenClaw]]` NOT re-inserted**; **`custom_probe` survived**; id/created preserved |
| MOVE | dedicated move test | — | id/created preserved; **`updated` NOT bumped by move** |

Artifacts (plan JSON, step outputs, final note text) for T1–T4 are in
`plans/phase-6-artifacts/<test>/`.

## Invariant checks (per the runbook)

- `id` unchanged since creation: **PASS** for all tests.
- `created` unchanged: **PASS** for all tests.
- Unknown frontmatter key (`custom_probe`) planted at creation survives every step: **PASS** (T4).
- Existing `type` not overwritten by the planner; pre-existing link not re-inserted: **PASS** (T4).
- Move does not bump `updated`: **PASS** (MOVE test).
- `updated` bumped after content edits: **not asserted per-step.** The `update-time-on-edit`
  plugin throttles (`minMinutesBetweenSaves: 4`, event-driven — see Phase 0 V2), so `updated`
  does not reliably change between the rapid successive edits of an automated E2E run. The plugin
  *does* fire (proven by the capture probe); the throttle just makes step-by-step assertions
  unreliable, so the solid invariants (id/created preservation, move-not-bumping) were checked
  instead.

## Contract mismatch found and fixed

- **obsctl move/rename output parsing.** The backend prints `Renamed: <old> -> <new>` /
  `Moved: <old> -> <new>`; obsctl originally captured the whole tail as the new path, producing a
  malformed `path_after`. Fixed in obsctl (`_parse_destination` splits on `->`) with a regression
  test (`test_rename_parses_arrow_destination`, updated `test_move_success_no_updated_bump`).

## Minor observations (not blocking)

- `vault-rag enrich`'s `link_insertions[].target` sometimes carries the `.md` suffix (e.g.
  `OpenClaw Sandboxing.md`), so obsctl emits `[[OpenClaw Sandboxing.md|sandboxing]]`. Obsidian
  resolves the path-form link correctly; a future enrich tweak could strip `.md` for cleaner
  wikilink text.
- The obsidian `move` backend does not create the destination folder (ENOENT if missing). In
  practice enrich's `suggested_path` folders already exist in the corpus, so this is a non-issue;
  callers should target existing folders.

## Step 8 (convenience wrapper)

Skipped deliberately — the Phase 7 skill orchestrates the CLIs directly (no `tools/capture.py`).

## Definition of done

- All four tests pass all applicable invariant checks; MOVE test passes.
- Artifacts + this results file committed to the vault-rag repo.
- Live vault left clean (`_e2e-test/` removed; test notes trashed).
