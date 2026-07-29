---
id: 01JEV000000000000000000102
title: Time Synchronization Notes
aliases: []
type: note
created: 2024-03-21T09:00:00Z
updated: 2025-06-26T12:00:00Z
tags: [infrastructure]
---
# Time Synchronization Notes

## NTP Server Configuration

All field devices synchronize their system clocks to a stratum-2 NTP server hosted on the primary office NAS device (10.60.1.50). The NAS receives time from multiple stratum-1 sources:

- **GPS receiver** (Garmin 18x LVC): Most authoritative source; 1 PPS (pulse-per-second) input to the NAS serial console
- **NIST internet time server** (nist1.lcs.nist.gov and backup nist2.lcs.nist.gov): Cloud-based stratum-1 reference, used if GPS loses lock
- **Local pool.ntp.org** (region-specific servers): Fallback if both primary sources fail

The NAS runs NTP daemon version 4.2.8p15 with strict authentication (MD5 signatures) to prevent time injection attacks from untrusted network segments.

## Timing Accuracy Requirements

Field sensor data (atmospheric measurements, network telemetry, event logs) are timestamped to 1-millisecond precision. This accuracy is required for:
- **Event correlation**: Matching coincident sensor readings across multiple remote stations
- **Data provenance**: Establishing causality relationships between observed phenomena
- **Audit logging**: Creating non-repudiable event records for security compliance

Clock drift exceeding ±100 ms on any field device triggers automatic alert and manual investigation. The NAS logs clock skew for all connected clients via SNMP monitoring.

## Remote Site Synchronization and Failover

The secondary ridge site operates an identical stratum-2 NTP server (10.60.1.6) that references the primary site's NAS via point-to-point radio link connectivity. If the radio link fails, the secondary site falls back to NIST internet NTP servers (via the cellular modem if primary internet is down).

Measured synchronization accuracy across sites is typically 8–12 ms during normal operations. The design accepts this level of skew as each site's absolute accuracy (±50 ms RMS to true UTC) is maintained independently via GPS receiver discipline.

## Hardware Time Sources and Maintenance

**GPS receiver maintenance:**
- Antenna position: Mounted on the office roof (9 m above ground)
- Cable length: 60 meters (includes low-loss LMR-400 coax to minimize signal loss)
- Lock verification: LED indicator and syslog messages confirm active lock every 300 seconds
- Annual calibration: No active maintenance required; GPS timing is inherently self-correcting

**Cellular modem NTP:**
- The Cradlepoint modem includes a low-stability crystal oscillator (±1 ppm)
- Used only as tertiary time source during GPS/internet failure
- Maximum acceptable drift: ±500 ms during extended GPS outages

---
**Current offset (primary site to UTC):** ±12 ms (measured 2025-06-26)
**Stratum level:** 2 (primary NAS), 3 (secondary sites)
