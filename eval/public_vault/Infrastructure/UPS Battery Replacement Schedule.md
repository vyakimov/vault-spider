---
id: 01JEV000000000000000000094
title: UPS Battery Replacement Schedule
aliases: []
type: schedule
created: 2024-04-13T09:00:00Z
updated: 2024-07-18T12:00:00Z
tags: [infrastructure, power]
---
# UPS Battery Replacement Schedule

## Replacement Interval and Battery Lifecycle

The office UPS system (Eaton 93PM 10 kVA) uses replaceable lead-acid battery modules with a nominal 5-year service life under standard operating conditions. Battery capacity degrades approximately 5% per year; replacement is scheduled when measured capacity falls below 80% of nameplate rating or when installed age exceeds 4.5 years, whichever occurs first.

**Replacement interval:** Every 48 months (January 1 target date for synchronization with facility budget cycles)

Battery modules are tested annually via electronic load bank verification. Test results are logged and trend analysis is performed quarterly to predict end-of-life and schedule replacement procurement in advance.

## Current Installation and Maintenance History

| Module Pair | Installed | Last Tested | Capacity | Scheduled Replacement |
|-------------|-----------|------------|----------|----------------------|
| Module A (primary) | 2020-01-15 | 2024-06-10 | 91% | 2024-01-15 → 2025-01-15 (pending budget approval) |
| Module B (secondary) | 2020-02-03 | 2024-06-18 | 88% | 2024-02-03 → 2025-02-03 (pending budget approval) |

Both modules are within acceptable operating range as of mid-2024. The secondary module shows slightly higher capacity degradation (4% faster than Module A), possibly due to elevated ambient temperature in the cabinet during summer months.

## Procurement and Installation Procedure

Replacement batteries must be Eaton OEM (part number 66999 or current equivalent) to maintain UPS warranty coverage. Bulk purchase orders are submitted 90 days before the scheduled replacement date to allow vendor lead time (typically 4–6 weeks) and to qualify for volume discount pricing.

Installation requires a 2-person team and 4 hours of downtime. The procedure involves:
1. Disconnect UPS from AC mains and discharge any residual charge (via safe discharge circuit)
2. Remove old modules from the battery cabinet
3. Install new modules and verify terminal torque (12 N⋅m per stud)
4. Perform no-load startup and verify charger operation
5. Perform 1-hour load bank test before returning to service

## Related Renewable Energy Systems

The UPS operates in parallel with the [[Solar Charge Controller Settings|solar battery bank]] during peak load periods (winter months when solar output is minimal). Coordination logic ensures the UPS does not discharge below 30% state-of-charge during operation to maximize lifespan.

---
**Budget allocation:** USD 8,400 per module pair (2024 quoted cost, pending 2025 renewal)
