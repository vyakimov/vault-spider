---
id: 01JEV000000000000000000012
title: WireGuard Network - Current
aliases: [Current Field Tunnel]
type: configuration
created: 2024-02-10T12:00:00Z
updated: 2025-04-02T14:00:00Z
tags: [networking, wireguard, current]
---
# WireGuard Network - Current

## Addressing

The current field tunnel uses subnet `10.44.0.0/24`. The central gateway is `10.44.0.1`, and Cedar
receives a stable address from the lower half of the subnet. WireGuard listens on UDP port 51820.

## Routing

This is a split tunnel. Peers route only `10.44.0.0/24` through WireGuard; ordinary internet
traffic continues through the local connection. Internal DNS resolves `cedar.atlas.internal` only
for connected peers.

## Status

This configuration replaced [[WireGuard Network - Archived 2023]] in February 2024. New runbooks
must use the current subnet and must not copy the archived full-tunnel route.

