---
updated: 2026-03-04T11:17:00
id: 01M6E00000000000000000000C
created: 2026-02-02T10:13:00
---
`fd "\.rs$" src/` finds all .rs files in src/; `-x` runs a command per result: `fd "\.log" --exec rm {}`. `-d 2` limits recursion depth; `-e md` filters by extension. Respects .gitignore by default (use `--no-ignore` to override). Faster and more intuitive than find.
