---
updated: 2026-05-20T17:49:00
id: 01M6E00000000000000000000W
created: 2026-04-18T14:41:00
---
`htop` is traditional, fast, shows processes and memory; `btop` (newer) adds per-core CPU graphs, disk I/O, and network tabs. Both support `-u user` to filter by user, `-K` for kill menu. btop requires more deps (Python) but has better visuals for system monitoring. Pick htop for remote SSH (lighter), btop for local debugging.
