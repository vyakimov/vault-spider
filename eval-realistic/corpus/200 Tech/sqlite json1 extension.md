---
updated: 2026-07-23T14:08:00
id: 01M6E000000000000000000135
created: 2026-06-21T13:52:00
---
`SELECT json_extract(data, '$.field') FROM table;` queries JSON fields as native SQLite columns. `json_each()` unnests arrays. Most distributions compile it in; if missing, rebuild SQLite with `-DSQLITE_ENABLE_JSON1`.
