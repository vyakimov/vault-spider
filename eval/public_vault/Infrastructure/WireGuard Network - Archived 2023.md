---
id: 01JEV000000000000000000013
title: WireGuard Network - Archived 2023
aliases: [Old Field Tunnel]
type: configuration
created: 2023-03-04T12:00:00Z
updated: 2024-02-10T11:30:00Z
tags: [networking, wireguard, archived]
---
# WireGuard Network - Archived 2023

> [!WARNING]
> Retired configuration. See [[WireGuard Network - Current]] for the active tunnel.

## Former addressing

The 2023 tunnel used subnet `10.31.0.0/24`, central gateway `10.31.0.1`, and UDP port 51821.

## Former routing

Peers used a full-tunnel route, sending all IPv4 traffic through the central gateway. This was
retired because routine field internet traffic did not need to cross the project network.

## Retirement

The configuration was decommissioned in February 2024 after all peers moved to the split-tunnel
network. It remains documented solely for interpreting historical incident records.

