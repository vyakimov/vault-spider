---
updated: 2026-06-02T16:22:00
id: 01M6E000000000000000000270
created: 2026-06-01T11:38:00
---
`timeout 30s mycommand` — kills mycommand if it runs >30 seconds. Exit code 124 on timeout, else subprocess's code. Useful in scripts to prevent hangs.
