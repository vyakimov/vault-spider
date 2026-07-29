---
updated: 2026-06-23T17:19:00
id: 01M6E000000000000000000291
created: 2026-06-22T20:11:00
---
`ps aux | grep nginx` lists all processes and filters by name. Use `ps aux | awk '$3>50'` to find processes using more than 50% CPU, or sort by field: `ps aux --sort=-%cpu`.
