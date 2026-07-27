---
updated: 2026-03-12T13:01:00
id: 01M6E000000000000000000124
created: 2026-02-10T14:29:00
---
`mdutil -i off /path && mdutil -i on /path` disables and re-enables indexing for that volume. For Macintosh HD: `mdutil -i off /` then `-i on /`. If Spotlight misbehaves, nuke the index: `rm -rf /.Spotlight-V100`.
