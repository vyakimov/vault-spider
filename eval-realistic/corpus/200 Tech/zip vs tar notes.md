---
updated: 2026-04-06T17:19:00
id: 01M6E000000000000000000118
created: 2026-03-04T20:11:00
---
`tar` preserves Unix permissions, hardlinks, and xattrs; `zip` is more portable but bulkier on Unix metadata. For homelab backups, `tar` + gzip is more efficient; zip for cross-platform hand-offs only.
