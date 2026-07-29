---
updated: 2026-06-16T10:20:00
id: 01M6E000000000000000000284
created: 2026-06-15T13:40:00
---
`find . -exec cmd {} \;` runs cmd per file. `find . -print0 | xargs -0 cmd` batches via null-delimited names (safer with spaces). For bulk ops, xargs is faster; for single actions, exec simpler.
