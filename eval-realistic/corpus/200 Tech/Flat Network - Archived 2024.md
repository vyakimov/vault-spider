---
aliases: [Old Home Network]
tags: [networking, archived]
updated: 2026-06-02T08:52:17
id: 01M6B000000000000000000004
created: 2024-03-15T19:31:08
---
# Flat Network - Archived 2024

## Former setup

Everything lived on `192.168.0.0/24` and remote access meant **port forwarding on the ISP
router**: 22 to the server, 8443 to the NAS UI. Dynamic DNS kept a hostname pointed at whatever
the public IP was that week.

## Retirement

Retired in late 2024: the ISP moved us behind CGNAT, so inbound port forwarding stopped working
entirely. Replaced by the tailnet described in [[Tailscale]] — outbound-only, no exposed ports.
New notes must not copy the forwarded-port addresses.
