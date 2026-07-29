---
updated: 2026-03-27T10:10:00
id: 01M6E000000000000000000061
created: 2026-02-25T11:50:00
---
`restic forget --keep-daily=7 --keep-weekly=4 --prune` — keep 7 daily + 4 weekly backups, delete rest. Run in cron weekly; monitor with `restic check` afterward.
