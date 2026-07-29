---
updated: 2026-02-11T12:44:00
id: 01M6E000000000000000000123
created: 2026-01-09T13:16:00
---
`tmutil addexclusion -p /path/to/exclude` persists across backups. Exclude `/Volumes/cache`, `~/.*` dotdirs, and any large rebuild dirs (node_modules, .venv) to speed up backups. Check exclusions with `tmutil isexcluded /path`.
