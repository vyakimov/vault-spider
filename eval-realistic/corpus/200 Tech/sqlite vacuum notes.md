---
updated: 2026-02-25T16:42:00
id: 01M6E000000000000000000137
created: 2026-01-23T15:18:00
---
`VACUUM;` rewrites the entire database file, reclaiming fragmented space. Blocks all other queries. Set `PRAGMA auto_vacuum = FULL;` on new databases to auto-defragment on each commit (slower but no blocking).
