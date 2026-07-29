---
id: 01JEV000000000000000000089
title: Generator Maintenance Log
aliases: []
type: log
created: 2025-08-08T09:00:00Z
updated: 2026-02-13T12:00:00Z
tags: [infrastructure, power]
---
# Generator Maintenance Log

## Oil Change and Service Intervals

The Generac 150 kW diesel standby generator (installed 2019, ~3,200 runtime hours as of 2026-02) undergoes oil and filter replacement every 500 runtime hours or annually, whichever occurs first. Synthetic 15W-40 diesel engine oil is used to extend drain intervals in the field's high-altitude environment (elevated air density effects).

**Recent service history:**
- 2025-11-04: Oil change (2,890 hours), new Cummins OEM fuel filter, no abnormalities noted
- 2025-06-22: Fuel system flush and injector cleaning (2,650 hours), diesel fuel treatment additive added
- 2025-02-14: Winter seasonal inspection, glow plug functionality verified, fuel heater tested

All service work is logged with technician name, duration, and detailed observations in the facility's maintenance database. Fuel polishing (standalone system) is performed annually before the high-load season (winter months) to remove any microbial growth or water ingress from long storage periods.

## Load Test and Failover Exercise

Quarterly load tests are performed under controlled conditions to verify generator response and load-sharing with the primary battery bank. The test sequence operates the generator at 25%, 50%, and 75% rated load for 15 minutes each, then shuts down in sequence.

**February 2026 test results:**
- Startup time to full-load readiness: 8.2 seconds (spec: <10 s)
- Voltage stability: ±2.1% THD (spec: <5%)
- Fuel consumption: 28.6 L/hour at 75% load (within manufacturer tolerance)

Failover from mains power to generator is triggered automatically when utility voltage drops below 180 V AC; the transfer switch includes a 10-second utility retry timer to prevent nuisance switching during brief brownouts.

## Related Facilities Infrastructure

Generator status is monitored remotely via a Modbus connection to the [[DNS Record Change Log|facility SCADA system]]. Fuel level is tracked via a capacitive sensor (0–275 gallons dynamic range) and linked to automatic purchase orders when inventory falls below the 30-day consumption threshold.

---
**Fuel on hand (as of 2026-02-13):** 1,840 gallons (approximately 64 days operating reserve at 25% average load)
