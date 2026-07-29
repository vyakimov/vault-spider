---
id: 01JEV000000000000000000091
title: Static IP Assignment Sheet
aliases: []
type: reference
created: 2025-01-10T09:00:00Z
updated: 2025-04-15T12:00:00Z
tags: [infrastructure, networking]
---
# Static IP Assignment Sheet

## Internal Addressing Scheme

All field infrastructure devices are assigned addresses from a dedicated 10.60.0.0/24 private range reserved for documentation and management isolation. This allocation is separate from any production network tunnel infrastructure.

| Device | Hostname | IPv4 Address | MAC Address | Assignment Type | Interface |
|--------|----------|-------------|------------|-----------------|-----------|
| Main switch management | mgmt-sw-primary.local | 10.60.1.2 | 00:1a:8f:b2:4c:09 | Static (VLAN 100) | GE-0/0/0 |
| Cellular modem | modem-backup.local | 10.60.1.3 | 44:4c:a8:92:3f:18 | Static (VLAN 100) | Ethernet WAN |
| Generator monitor | pdu-gen.local | 10.60.1.4 | 52:54:00:ab:2e:44 | Static (VLAN 100) | RS-485 gateway |
| Tower PoE injector | poe-inj-tower.local | 10.60.1.5 | 00:0b:85:cc:1d:7f | Static (VLAN 100) | GE port 1 |
| Ridge PoE aggregator | poe-ridge.local | 10.60.1.6 | 08:00:27:a1:5e:b3 | Static (VLAN 100) | Eth0 |
| DHCP server (backup) | dhcp.local | 10.60.1.1 | 52:54:00:12:34:56 | Static (VLAN 100) | GE port 2 |
| Office laptop dock (temporary) | workstation.local | 10.60.1.50 | *varies by device* | DHCP lease (reserved) | GE port 3 |

## DHCP Reservation and Dynamic Allocation

The primary DHCP server allocates addresses from the 10.60.2.0–10.60.2.254 range to temporary devices (laptops, test equipment, visiting tech nodes). Reservations are made by MAC address for devices requiring consistent addressing across multiple field seasons.

**Reserved DHCP leases:**
- Service tech laptop: 10.60.2.100 (lease time 30 days)
- Test bench sensor simulator: 10.60.2.101 (persistent reservation)
- Field meter and probe interfaces: 10.60.2.102–10.60.2.110 (pool, 24-hour leases)

## Documentation and Audit

This sheet is the canonical reference for device addressing and is updated whenever a new asset is commissioned. All device removals are logged with date and reason (decommissioned, relocated, replaced). The list is compared quarterly against actual running devices detected via ICMP sweep and ARP table inspection to catch inadvertent duplicates or rogue devices.

DNS resolution for all addresses is maintained in a local zone file; external DNS queries are not performed for 10.60.0.0/24 addresses.

---
**Last verified:** 2025-04-15 (13 active devices, 2 reserved leases)
