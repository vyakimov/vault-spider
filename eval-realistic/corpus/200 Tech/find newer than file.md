---
updated: 2026-07-17T11:37:00
id: 01M6E000000000000000000285
created: 2026-07-16T14:53:00
---
`find . -newer reference.txt` — finds files modified after reference.txt's mtime. Use `-anewer` for atime, `-cnewer` for ctime. Useful for incremental backups/CI diffs.
