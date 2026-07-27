---
updated: 2026-03-05T16:02:00
id: 01M6E000000000000000000117
created: 2026-02-03T19:58:00
---
`tar -c --listed-incremental=snar.db -f backup.tar files/` creates an incremental backup; subsequent runs only add changed files. Use `-x --listed-incremental=snar.db` to restore, and keep the `.snar` snapshot file between runs.
