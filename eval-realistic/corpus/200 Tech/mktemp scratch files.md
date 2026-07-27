---
updated: 2026-04-11T17:39:00
id: 01M6E000000000000000000331
created: 2026-04-10T12:51:00
---
`mktemp` creates a unique temp file in /tmp, prints the path. Use `mktemp -d` for temp dir, `mktemp -p /custom/path` for custom location. Safer than `$RANDOM` for unique names.
