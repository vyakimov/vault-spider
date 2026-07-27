---
id: 01JEV000000000000000000090
title: Network Switch Inventory
aliases: []
type: reference
created: 2024-09-09T09:00:00Z
updated: 2025-03-14T12:00:00Z
tags: [infrastructure, networking]
---
# Network Switch Inventory

## Main Site Equipment

| Device | Model | Ports | PoE? | Firmware Ver. | Installed | Location |
|--------|-------|-------|------|---------------|-----------|----|
| Main aggregation | Juniper EX2300-48P | 48x GE + 4x QSFP+ | Yes (720W) | 20.2 R1 | 2022-04 | Primary cabinet rack position 2U |
| Secondary field office | Arista 7050SX3-48YC12 | 48x 25G + 12x QSFP28 | No | 4.32.1F | 2023-11 | Backup cabinet (online, standby config) |
| Tower site unmanaged | Netgear MS510TXUP | 5x GE SFP | Yes (90W) | N/A (L2 only) | 2021-08 | Observation tower shelter, PoE-powered |
| Ridge remote (PoE aggregation) | Ubiquiti EdgeSwitch Pro | 24x GE + 2x SFP | Yes (500W) | 2.8.3 | 2023-06 | Secondary ridge site shelter |
| Diagnostics/test bench | HP J9149A ProCurve 2910al-48G | 48x GE | No | Y.16A45.19 | 2019-02 | Office break room (for offline testing) |

## Firmware Versioning and Update Strategy

All production switches are on a 12-month firmware update cycle aligned with vendor patch release schedules. Critical security patches (CVE CVSS ≥ 7.0) are applied within 14 days of publication; lower-severity updates are batched on the annual cycle.

Testing occurs on bench-mounted identical hardware before field deployment. The secondary Arista switch is maintained in sync with the Juniper production device to allow rapid failover migration if the primary switch experiences hardware failure.

## Lifecycle and Support Status

**End of Support dates:**
- Juniper EX2300: December 2027 (purchase new 4-port QSFP+ model by Q4 2027)
- Arista 7050SX3: June 2028 (already evaluated as replacement; cost estimate USD 18,400)
- Netgear MS510TXUP: Discontinued (no spare available; replacement with Ubiquiti-branded unit approved for 2026)

Warranty service is provided by vendor direct; replacement parts are stocked for high-failure-rate items (SFP transceivers, power supplies).

## Integration with Field Operations

Switch performance is monitored continuously via SNMP polled every 300 seconds. Uptime, CPU load, memory utilization, and port status are aggregated in the facility [[Generator Maintenance Log|SCADA dashboard]]. Critical alerts (power supply failure, memory exhaustion) trigger out-of-band notification via SMS.

Cross-site connectivity is maintained via [[VPN Client Setup Guide|redundant tunnel configuration]] and [[Solar Charge Controller Settings|synchronization]] across the remote sites.

---
**Last inventory verification:** 2025-03-14
