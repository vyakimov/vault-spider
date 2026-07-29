---
updated: 2026-02-03T10:00:00
id: 01M6E00000000000000000000B
created: 2026-01-01T09:00:00
---
`rg -i "pattern" --type rust` searches case-insensitively in Rust files only; `rg --files-with-matches` shows file names only. Use `rg -l` to skip large binary files; `-A 3 -B 1` adds context lines. Much faster than grep on large codebases due to parallelism and gitignore respect.
