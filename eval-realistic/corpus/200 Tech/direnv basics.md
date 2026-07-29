---
updated: 2026-06-09T12:04:00
id: 01M6E000000000000000000043
created: 2026-05-07T17:56:00
---
`echo 'export PATH_add ./bin' > .envrc && direnv allow` — load .envrc file in shell on cd, auto-unloads on exit. Essential for per-project env vars without polluting globals.
