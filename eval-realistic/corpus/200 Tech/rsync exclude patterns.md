---
updated: 2026-02-04T15:45:00
id: 01M6E000000000000000000116
created: 2026-01-02T18:45:00
---
`rsync -av --exclude='*.log' --exclude='.git' src/ dest/` — skip matching files/dirs. Patterns use gitignore syntax: `dir/` matches only dirs, `**/name` matches in any subdir. Load patterns from file with `--exclude-from=file`.
