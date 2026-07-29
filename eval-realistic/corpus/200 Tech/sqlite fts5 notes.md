---
updated: 2026-01-24T15:25:00
id: 01M6E000000000000000000136
created: 2026-07-22T14:05:00
---
`CREATE VIRTUAL TABLE docs USING fts5(content)` enables full-text search. Query with `WHERE docs MATCH 'keyword'` and rank results by relevance. Rebuilds the FTS table with `INSERT INTO docs(docs) VALUES('rebuild')`.
