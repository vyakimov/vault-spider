---
id: 01JEV000000000000000000083
title: Solar Charge Controller Settings
aliases: []
type: configuration
created: 2025-02-02T09:00:00Z
updated: 2026-05-07T12:00:00Z
tags: [infrastructure, power]
---
# Solar Charge Controller Settings

## MPPT Configuration at Primary Site

The Victron MPPT 150/100 charge controller at the primary observation tower is configured for a nominal 48 V lithium battery bank. Operating parameters have been tuned to maximize harvest during the short winter daylight hours characteristic of the site's high latitude.

**Active settings:**
- Battery voltage: 48 V (LiFePO₄ chemistry, 100 Ah capacity)
- PV array: 6.4 kW nominal (four strings of 8 × 200 W modules, 40 V nominal open-circuit)
- Bulk charge voltage: 55.2 V
- Float voltage: 51.5 V
- Temperature compensation: -0.04 V/K (integrated PT100 sensor)
- PV voltage limit: 140 V DC

Charging efficiency in bright daylight reaches 98.2%; winter seasonal efficiency averages 87% due to suboptimal solar angles and cloud cover cycles. The controller logs instantaneous and cumulative energy statistics to the internal SD card at 5-minute intervals.

## Secondary Site Configuration and Monitoring

The secondary station (located at the 340-meter ridge site) uses an identical MPPT 100/50 variant rated for lower PV input due to space constraints. Both controllers synchronize time via [[Time Synchronization Notes|site NTP servers]] to ensure coherent logging across distributed monitoring assets.

Firmware versions are maintained on a 12-month cycle coinciding with Victron's release schedule. Critical security patches are applied immediately; firmware testing occurs on a bench-mounted identical controller before field deployment.

## Related Notes

- [[Time Synchronization Notes]]
