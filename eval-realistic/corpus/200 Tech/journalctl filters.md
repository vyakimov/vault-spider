---
updated: 2026-02-21T10:50:00
id: 01M6E000000000000000000081
created: 2026-01-19T19:10:00
---
`journalctl -u nginx -n 50 --since today` — show last 50 lines from nginx unit since today. Use `-p err` for errors only, `--follow` to tail, and `--no-pager` for script-friendly output.
