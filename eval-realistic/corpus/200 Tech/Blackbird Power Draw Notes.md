---
updated: 2026-03-09T10:41:00
id: 01M6Q000000000000000000005
created: 2026-04-06T09:37:00
tags:
  - homelab
  - hardware
---
Idle ~25W, resilver peaks 80W (full spindle activity). Measured via PDU `snmp walk` queries to net-snmp daemon; UPS budget is 500VA, covers 4h outage. Monitor via `nut-monitor` and alert at 25% battery remaining to trigger graceful shutdown.
