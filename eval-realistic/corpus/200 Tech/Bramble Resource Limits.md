---
updated: 2026-06-28T10:10:00
id: 01M6B00000000000000000000B
created: 2026-02-25T09:50:00
tags:
  - homelab
---
Set cgroup limits on Bramble (gateway VPS) via `systemctl set-property gateway.service MemoryLimit=2G CPUQuota=50%` to prevent runaway Python processes consuming host. Check via `systemctl show gateway.service | grep Memory` and `systemctl show gateway.service | grep CPU`. Graceful exit on memory hit prevents OOM killer from affecting other services.
