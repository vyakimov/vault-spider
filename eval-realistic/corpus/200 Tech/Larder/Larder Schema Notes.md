---
updated: 2026-06-02T09:10:31
id: 01M6J000000000000000000006
created: 2026-04-22T20:33:47
---

A [[Larder]] implementation note on the SQLite schema.

Three tables and no cleverness: `items` (name, barcode, unit), `stock` (item_id, quantity,
location, expiry), `log` (every add/remove, append-only). Locations are a plain text column —
"freezer", "pantry", "under the stairs" — a lookup table felt like ceremony.

The append-only `log` is the part that has paid off: quantity drift gets debugged from history
instead of argued about. See [[Barcode Scanning Notes]] for how rows get created.
