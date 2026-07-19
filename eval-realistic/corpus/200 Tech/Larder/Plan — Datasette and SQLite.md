---
updated: 2026-06-02T08:56:23
id: 01M6C000000000000000000002
created: 2026-04-12T09:50:02
---
# Plan — Datasette and SQLite

A [[Larder]] plan note — the low-effort option.

Publish the pantry database with Datasette; edits happen through `sqlite-utils` on the command
line or a spreadsheet import. Zero frontend work, faceted browsing for free.

Rejected because the workflow that matters is **adding items at the kitchen counter from the
phone**, ideally by scanning the barcode — and Datasette is read-oriented; writes would mean
bolting on plugins or dropping to the CLI, which nobody will do while holding groceries.
