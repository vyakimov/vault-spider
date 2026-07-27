---
updated: 2026-02-17T11:42:00
id: 01M6V000000000000000000003
created: 2026-01-17T10:54:00
---
# Local DNS Split Horizon Notes

Serving different answers for the same hostname on LAN versus tailnet so things work correctly from either side.

## The Problem
My home server runs at an internal address. Machines on the LAN can reach it directly, but the tailnet sees a different IP. If I use just one answer, machines on the tailnet get slow DNS-over-VPN lookups, or machines on the LAN get routed through the tailnet unnecessarily. Split horizon DNS fixes this by returning the LAN IP for LAN clients and the tailnet IP for remote clients.

## Implementation
The headscale controller and the home DNS server are both aware of the split. I configure the home server's DNS to return the internal IP for my domain, and the headscale DNS resolver to return the tailnet IP. Machines check which network they're on and query the appropriate resolver. A bit of extra bookkeeping, but it makes everything feel responsive from anywhere.
