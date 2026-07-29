---
updated: 2026-01-08T10:30:00
id: 01M6Q000000000000000000004
created: 2026-03-05T09:30:00
tags:
  - homelab
  - networking
---
Blackbird on storage VLAN (10.9.0.0/24) bridged through pfSense to avoid SMB broadcast storms. Inbound pull-only via rsync over SSH; configured via `interface vlan.storage { address 10.9.0.5; }` on the switch, isolating backup traffic from general LAN.
