---
updated: 2026-03-26T17:59:00
id: 01M6E000000000000000000138
created: 2026-02-24T16:31:00
---
`SELECT * FROM read_parquet('file.parquet');` directly queries parquet without loading to disk. Works on S3 too: `read_parquet('s3://bucket/file.parquet')`. DuckDB pushes filtering into the parquet scan, minimizing I/O.
