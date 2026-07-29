---
updated: 2026-04-06T10:08:00
id: 01M6Q000000000000000000002
created: 2026-01-03T09:16:00
tags:
  - homelab
  - hardware
---
Degraded drive swap using `zpool replace pool sda sdb && zpool status` to trigger resilver; watch SMART errors beforehand with `smartctl -a /dev/sda`. Resilver time ~14h on 8TB NAS drives, plan downtime around it.
