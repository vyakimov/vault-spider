---
id: 01JEV000000000000000000014
title: DNS and Hostnames
type: configuration
created: 2024-02-11T09:00:00Z
updated: 2025-04-02T14:15:00Z
tags: [networking, dns, atlas]
---
# DNS and Hostnames

## Public names

`api.atlas.example` and `dashboard.atlas.example` resolve to the public reverse proxy. Both records
use a five-minute TTL. The `.example` domain is reserved documentation space and does not identify
a real deployment.

## Internal names

`cedar.atlas.internal` resolves only on the WireGuard network. It points to Cedar's current
`10.44.0.0/24` address and must never be published in public DNS.

## Certificate boundary

Caddy manages certificates for the two public names. Internal names use the tunnel's authenticated
network boundary and are not included in the public certificate.

