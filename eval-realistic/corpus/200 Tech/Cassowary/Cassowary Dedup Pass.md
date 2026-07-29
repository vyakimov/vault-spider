---
tags:
  - homelab
  - photos
updated: 2026-03-28T10:24:00
id: 01M6P000000000000000000005
created: 2026-04-25T09:48:00
---
After importing years of phone backups from three old devices, I ran a one-time dedup pass using SHA-256 hashes of the raw image files. Found about 8,000 exact duplicates — mostly the same vacation photos synced across multiple phones, plus a few camera roll imports that got captured twice by automated backup services. Removed the duplicates but kept the original import metadata for one copy of each unique image to preserve the earliest timestamp. The dedup log is buried in `/mnt/logs/cassowary/dedup_2026-04-25.jsonl`.
