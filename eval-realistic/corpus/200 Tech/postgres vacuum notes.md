---
updated: 2026-04-27T18:16:00
id: 01M6E000000000000000000139
created: 2026-03-25T17:44:00
---
`VACUUM ANALYZE;` reclaims dead rows and updates stats. Blocks writes; run off-hours. Enable `autovacuum` (default) so vacuum runs in the background. For large tables, `VACUUM ANALYZE table_name;` is faster.
