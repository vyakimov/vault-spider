---
updated: 2026-03-06T19:13:00
id: 01M6E000000000000000000040
created: 2026-02-04T14:17:00
---
`find . -type f -name "*.jpg" | xargs -P 4 -I {} convert {} {}.png` — process 4 files in parallel, replacing {} with each filename. -P sets concurrency.
