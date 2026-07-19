---
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000005
created: 2026-03-21T16:44:09
---
A [[technote]] on DuckDB.

Query a CSV without importing anything:
`select * from 'expenses-2026.csv' where amount > 100 order by amount desc;`

Parquet the same way, globs work: `from 'data/*.parquet'`.

`INSTALL httpfs; LOAD httpfs;` and you can query files straight off https URLs, which feels
illegal but isn't.
