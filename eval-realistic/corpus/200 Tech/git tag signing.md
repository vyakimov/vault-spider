---
updated: 2026-04-21T14:28:00
id: 01M6E000000000000000000055
created: 2026-03-19T17:32:00
---
`git tag -s v1.0.0 -m "Release v1.0.0"` — create signed tag with GPG key. `git verify-tag v1.0.0` checks signature; store pubkey on server for CI validation.
