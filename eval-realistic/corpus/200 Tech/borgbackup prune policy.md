---
updated: 2026-04-28T11:27:00
id: 01M6E000000000000000000062
created: 2026-03-26T12:03:00
---
`borg prune repo --keep-daily=7 --keep-weekly=4 --keep-yearly=2` — keep retention tiers; use `borg list` first to verify archives. Compact repo after pruning with `borg compact repo`.
