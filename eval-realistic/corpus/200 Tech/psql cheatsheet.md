---
updated: 2026-02-10T17:59:00
id: 01M6E00000000000000000000J
created: 2026-01-08T16:31:00
---
`psql -U user -d dbname -h localhost` connects; `\dt` lists tables, `\d tablename` shows schema. `\copy table_name to 'file.csv' WITH (FORMAT csv, HEADER)` exports; `SELECT count(*) FROM table_name;` for row count. `EXPLAIN ANALYZE SELECT ...` shows query plan; add `ANALYZE` to run actual timing. Set `\pset pager off` to disable pager on first connect.
