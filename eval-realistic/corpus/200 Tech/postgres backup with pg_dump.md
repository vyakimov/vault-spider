---
updated: 2026-06-03T10:50:00
id: 01M6E000000000000000000141
created: 2026-05-01T19:10:00
---
`pg_dump -U user dbname > backup.sql` dumps schema and data as SQL. Use `-F custom -f backup.dump` for binary format (compresses better, faster restore). Restore: `pg_restore -U user -d dbname backup.dump`.
