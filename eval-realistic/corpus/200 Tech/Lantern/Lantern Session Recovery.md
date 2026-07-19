---
updated: 2026-06-02T08:46:12
id: 01M6A000000000000000000008
created: 2026-05-24T18:12:09
---
# Lantern Session Recovery

A [[Lantern]] [[technote]] — how a crashed session comes back.

Every session appends to a journal file under `~/.lantern/journal/<session-id>.jsonl` before
acting, never after. On restart Lantern replays the journal in order and resumes at the first
unacknowledged entry.

The gotcha: replay is **strictly ordered**, so a corrupt line stops recovery for that session.
`lantern journal verify` finds the bad line; truncate from there and accept losing the tail.

Do not share journal directories between machines — the session id embeds the hostname and a
replay on the wrong machine refuses with `journal_host_mismatch`.

#lantern #recovery
