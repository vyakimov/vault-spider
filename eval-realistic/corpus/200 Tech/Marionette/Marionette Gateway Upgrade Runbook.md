---
updated: 2026-06-02T09:10:31
id: 01M6J000000000000000000001
created: 2026-04-28T10:22:14
---
# Marionette — Gateway Upgrade Runbook

A [[Marionette]] [[technote]] — upgrading the gateway on [[Bramble]] without breaking the pair.

## Before

Read the release notes for config-key renames; snapshot the VPS; note the currently installed
version somewhere you will actually look.

## Order of operations

1. Upgrade the gateway on Bramble first.
2. Upgrade the node on [[PuddleJumper]] **in the same sitting** — a half-upgraded pair is an
   unsupported state and behaves accordingly.
3. Re-run the smoke checks from [[Marionette Remote Shell Runbook]].

## After

Watch the first cron-driven session complete end to end before calling it done. Config
migrations announce themselves in the gateway log with `migrated:` lines — read them once
instead of discovering them in a month.
