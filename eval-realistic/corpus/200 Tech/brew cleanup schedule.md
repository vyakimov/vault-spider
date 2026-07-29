---
updated: 2026-05-14T15:35:00
id: 01M6E000000000000000000126
created: 2026-04-12T16:55:00
---
`brew cleanup` removes old versions; `brew cleanup -s --prune-prefix` is more aggressive. Schedule it weekly via launchd to keep `/Library/Caches/Homebrew` from bloating. Run `brew cleanup -n` first to see what gets removed.
