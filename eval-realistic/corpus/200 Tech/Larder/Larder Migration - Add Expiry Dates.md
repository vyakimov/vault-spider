---
tags:
  - homelab
updated: 2026-03-16T10:58:00
id: 01M6C000000000000000000004
created: 2026-04-13T09:26:00
---
Added an optional `expiry_date` column to the items table using a zero-downtime migration. The app checks for the column at startup and runs the migration if it's missing. Existing items get `NULL` for expiry, which the UI treats as "no expiry set" and skips in shelf-life warnings. The migration itself is just an ALTER TABLE with a default of NULL, so it's fast even on a table with 50,000+ archived items. Deployed without downtime or backups.
