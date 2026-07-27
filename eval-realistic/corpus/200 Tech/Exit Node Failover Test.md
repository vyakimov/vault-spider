---
updated: 2026-03-04T10:32:00
id: 01M6B00000000000000000000D
created: 2026-04-01T09:04:00
tags:
  - homelab
  - networking
---
Test by `sudo pkill tailscale` on exit node; routed clients drop packets for ~3-5s, then failover to secondary exit node (configured via `tailscale up --exit-node=secondary.tailnet`). Monitor with `ping -D 8.8.8.8 | tee failover.log` and parse for ICMP timestamp gaps. Recovery is automatic if secondary is healthy.
