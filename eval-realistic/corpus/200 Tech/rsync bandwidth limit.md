---
updated: 2026-01-03T14:28:00
id: 01M6E000000000000000000115
created: 2026-07-01T17:32:00
---
`rsync --bwlimit=1024 -av src/ dest/` — cap bandwidth to 1024 KB/s. Useful on slow links or to avoid saturating production networks. Combine with `--partial` to resume interrupted transfers.
