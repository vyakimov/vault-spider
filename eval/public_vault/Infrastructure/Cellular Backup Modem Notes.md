---
id: 01JEV000000000000000000086
title: Cellular Backup Modem Notes
aliases: []
type: reference
created: 2024-05-05T09:00:00Z
updated: 2025-08-10T12:00:00Z
tags: [infrastructure, networking]
---
# Cellular Backup Modem Notes

## Hardware Configuration

The Cradlepoint IBR900 industrial LTE router serves as the primary failover device when the primary internet feed (fiber optic line) becomes unavailable. The modem is dual-SIM capable, with active connectivity on a commercial wide-area LTE carrier (Band 4 and Band 7 coverage) and a secondary SIM on a different network operator held in reserve.

**Hardware specifications:**
- LTE-A release 13, Category 12 (600 Mbps theoretical, 50 Mbps typical upload)
- Dual Ethernet ports (1 GbE, 1 x 10/100)
- Integrated WiFi 5 (disabled in operational mode to reduce RF interference)
- Serial console access via RJ-45 jack for out-of-band diagnostics
- Battery-backed real-time clock with GPS disciplined oscillator

The modem is positioned in a shielded RF box adjacent to the main equipment rack to minimize coupling with the site's satellite dish and directional radio systems.

## Service Configuration and Failover Behavior

The primary internet connection is monitored via continuous ICMP echo requests to multiple targets (Google DNS, Cloudflare, facility DNS authoritative server). Loss of all three targets triggers automatic WAN failover to LTE within 45 seconds. A manual override is available via SSH access to the router's management interface.

SIM connectivity is monitored on a 24-hour rolling basis; the modem logs signal strength (RSSI) and connection time metrics to syslog. SIM cards are renewed 30 days before contractual expiration to avoid mid-campaign service loss during field seasons.

## Cost Control and Deployment Context

Monthly data usage averages 2.8 GB during normal operations (primarily remote monitoring heartbeat and log uploads). Cost is approximately USD 85/month per active SIM. The secondary SIM is maintained on a minimal data plan (5 GB annual cap) for emergency use only. Activation occurs only after primary failover confirms link loss for >60 seconds.

No field staff are authorized to use the backup modem for personal internet access; bandwidth is reserved exclusively for facility management and sensor data continuity.
