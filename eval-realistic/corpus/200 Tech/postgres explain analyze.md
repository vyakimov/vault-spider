---
updated: 2026-05-28T19:33:00
id: 01M6E000000000000000000140
created: 2026-04-26T18:57:00
---
`EXPLAIN ANALYZE SELECT ...;` shows query plan and actual row counts. Look for sequential scans on large tables (add an index), high I/O costs, or hash aggregate performance. `ANALYZE` runs the query, so use carefully on writes.
