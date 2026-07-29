---
updated: 2026-06-07T10:19:00
id: 01M6Q000000000000000000003
created: 2026-02-04T09:23:00
tags:
  - homelab
---
Hourly snapshots via `zfs set io.github.openzfs:auto_snapshot:frequent=true pool/data` plus monthly archive snapshots; different from LordByron's 4-hour retention to avoid correlation if one system's backup is compromised. Cron triggers pruning via `zfs destroy pool@snapshot-name`.
