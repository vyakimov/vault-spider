---
id: 01JEV000000000000000000008
title: Service Port Registry
type: reference
created: 2024-02-03T09:00:00Z
updated: 2025-04-02T13:20:00Z
tags: [atlas, networking, ports]
---
# Service Port Registry

| Service | Port | Exposure |
|---|---:|---|
| Caddy HTTPS | 443 TCP | Public reverse proxy |
| Atlas API | 8080 TCP | Container network only |
| Atlas dashboard | 3000 TCP | Container network only |
| Metrics exporter | 9102 TCP | WireGuard network only |
| WireGuard | 51820 UDP | Gateway tunnel endpoint |
| SSH | 22 TCP | Bastion network only |

Only port 443 is intended for general client traffic. Application and metrics ports must not be
opened directly to the public network.

