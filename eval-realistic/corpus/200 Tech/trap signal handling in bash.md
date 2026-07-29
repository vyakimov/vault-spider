---
updated: 2026-03-06T10:30:00
id: 01M6E000000000000000000274
created: 2026-03-05T15:30:00
---
`trap 'rm /tmp/temp.txt' EXIT` — runs cleanup on script exit. `trap 'echo quit' SIGINT` handles Ctrl+C. Common signals: EXIT, SIGTERM, SIGINT. Quoted or double-quoted, evaluated on trigger.
