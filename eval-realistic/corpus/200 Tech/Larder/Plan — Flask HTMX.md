---
updated: 2026-06-02T08:56:23
id: 01M6C000000000000000000003
created: 2026-04-13T21:30:46
---
# Plan — Flask HTMX

The [[Larder]] plan that was built.

- Flask + HTMX + SQLite, one container on [[PuddleJumper]].
- Phone-first UI; the add-item flow opens the camera and scans the barcode, falls back to a
  fuzzy name search against previous items.
- Quantities are integers with a unit string; no attempt at recipe math.
- Nightly `sqlite3 .backup` into the [[NAS Snapshot Replication]] path on [[LordByron]].

The barcode requirement is what killed [[Plan — Datasette and SQLite]]: input at the counter
beats query features.
