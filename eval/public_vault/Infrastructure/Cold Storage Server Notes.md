---
id: 01JEV000000000000000000106
title: Cold Storage Server Notes
aliases: []
type: note
created: 2024-07-25T09:00:00Z
updated: 2024-01-04T12:00:00Z
tags: [infrastructure]
---
# Cold Storage Server Notes

## Low-Power Archive Server Hardware

The cold storage server (system name: archive-01.atlas.local, IP address 10.60.1.55) is a low-power Intel Atom-based NAS appliance used exclusively for archival storage of historical telemetry data and sensor exports. The device is powered on continuously but operates in a low-duty state, consuming approximately 18 W during idle operation and 45 W during active data transfers.

**Hardware specifications:**
- Processor: Intel Atom C3338 dual-core (1.5 GHz, 10 W TDP)
- RAM: 8 GB ECC SDRAM
- Storage: 12 × 8 TB 3.5-inch SATA HDD (96 TB raw capacity; 84 TB usable with RAID-6 parity)
- Network: Single 1 GbE Ethernet (sufficient for archive duty; not a performance-critical link)
- Form factor: 4U rackmount appliance in the main equipment [[Equipment Rack Layout|cabinet]]

The appliance runs a Linux-based operating system (Debian-based distribution) with rsync and SSH services enabled for remote access.

## Data Retention and Archive Policy

The archive server is populated via weekly rsync transfers from the primary NAS (10.60.1.50). Historical data is organized by year-quarter and includes:

- **Sensor telemetry exports**: Complete raw sensor readings (1-minute and 10-minute aggregates)
- **Network event logs**: Router, switch, and firewall event records
- **Power system metrics**: Battery voltage, generator runtime, solar charging efficiency
- **System administration logs**: Change tickets, maintenance records, access logs

Data retention policy:
- Active (current year + 1 prior year): Primary NAS with daily snapshots
- Archive (2–7 years old): Cold storage server, quarterly snapshots only
- Purge threshold: Data older than 7 years is reviewed annually; most historical data is retained for long-term environmental trend analysis

## Access and Connectivity

The archive server is typically offline or in low-power sleep state. It can be activated via [[VPN Client Setup Guide|remote SSH access]] for archive queries, but bandwidth limitations (1 GbE) make bulk data recovery slow (typical throughput 80–100 Mbps).

Disaster recovery testing occurs annually: a mock data loss scenario triggers recovery of specific archived records to verify integrity and restoration procedures.

## Maintenance and Component Lifecycle

HDD replacement is performed proactively at 80% of manufacturer MTBF rating (approximately 3-year intervals). RAID-6 configuration tolerates simultaneous failure of up to 2 drives without data loss. No failures have occurred since installation in 2019; oldest drives are scheduled for replacement in Q3 2026.

Firmware updates for the storage controller are applied annually, typically in February after winter field season conclusion. The server restarts automatically after firmware updates (configured to start at 2 AM UTC when traffic is minimal).

## Integration with Infrastructure Documentation

Access to the archive server is controlled via SSH key pairs maintained by the infrastructure engineering team. Physical access to the storage device is restricted per [[Equipment Rack Layout]] security standards.

Related infrastructure notes including [[VPN Client Setup Guide|remote access procedures]], [[Cable Labeling Standard|equipment identification]], and [[Weatherproof Enclosure Standards|environmental protection]] define the operational and security context for archive-server stewardship.

---
**Usable storage (as of Jan 2025):** 68 TB active data (81% full; archival expansion planned)
**Last backup integrity check:** 2024-01-04 (all RAID-6 checksums verified)
