---
updated: 2026-02-26T10:48:00
id: 01M6B000000000000000000009
created: 2026-07-23T09:36:00
tags:
  - homelab
  - networking
---
Evaluated Tailscale Funnel (HTTP/HTTPS egress to internet) for guest-accessible docs site. Trade-off: public ingress via tailnet subdomain but adds latency and cost; decided to keep Caddy + tailnet-only instead. Notes: Funnel requires device to be online and is not port-specific like traditional port-forwarding.
