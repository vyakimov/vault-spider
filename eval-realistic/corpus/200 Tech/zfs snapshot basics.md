---
updated: 2026-05-03T12:44:00
id: 01M6E000000000000000000063
created: 2026-04-01T13:16:00
---
`zfs snapshot tank/data@daily-$(date +%Y%m%d)` — create timestamped snapshot. `zfs list -t snapshot` shows all; `zfs rollback tank/data@snap` reverts to snapshot state.
