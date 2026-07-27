---
id: 01JEV000000000000000000101
title: Antenna Alignment Notes
aliases: []
type: note
created: 2025-02-20T09:00:00Z
updated: 2026-05-25T12:00:00Z
tags: [infrastructure, networking]
---
# Antenna Alignment Notes

## Point-to-Point Radio Link Configuration

The primary long-distance radio link connects the main field-office site to the secondary ridge observation station, approximately 4.1 km distant. Both ends of the link use identical Ubiquiti airMAX AC 5 GHz directional antennas (23 dBi gain, 10° horizontal beamwidth).

**Link geometry:**
- Primary site antenna bearing: 028° magnetic (northeast)
- Primary site antenna tilt: 2.1° depression angle (target distance 4.1 km)
- Secondary site antenna bearing: 208° magnetic (southwest)
- Secondary site antenna tilt: 1.8° depression angle (reciprocal path)

Antenna centers are mounted on the primary site at 12.5 m above local ground level; the secondary site antenna is mounted at 8.2 m above local grade. These heights were chosen to clear foreground vegetation and ensure line-of-sight clearance with 1.2× Fresnel zone margin (Fresnel radius = 18 m at 5 GHz).

## Signal Strength Baseline and Monitoring

**Expected performance baseline (clear sky conditions):**
- RSSI (Received Signal Strength Indicator): −42 to −48 dBm (excellent range)
- SNR (Signal-to-Noise Ratio): >28 dB (very strong signal margin)
- Throughput: 180–220 Mbps aggregate (limited by backhaul capacity, not RF)

**Seasonal performance variation:**
- Spring (April–May): Signal occasionally drops 3–5 dB during peak vegetation growth; recovers in June once trees reach full leaf-out
- Summer (June–September): Stable baseline; occasional rain fade (2–4 dB) during thunderstorms
- Fall (October–November): Slight improvement as foliage dies back (2 dB gain)
- Winter (December–March): Best performance; signal typically 3–4 dB stronger than baseline

Real-time signal monitoring is displayed on the facility management dashboard. Automated alerts trigger if RSSI drops below −65 dBm (marginal threshold) or SNR falls below 15 dB.

## Realignment Procedure and Calibration

Annual realignment is performed in February after winter weather potentially shifts antennas. The alignment procedure involves:

1. Transmit a known CW (continuous wave) test signal from the primary site
2. Use an RF power meter and directional coupler at the secondary site to measure incident power
3. Perform azimuth and elevation sweeps in 0.2° increments
4. Record the bearing and tilt at peak power point
5. Compare to historical baseline and note any drift >0.3°

Physical alignment is performed using a Leica Theodolite (±0.1° accuracy) surveyed against the facility's permanent survey benchmark. Antenna mounting bolts are checked for tightness and re-torqued to 15 N⋅m specification if drift is detected.

No field maintenance has been required since 2024 initial commissioning.

---
**Last verified:** 2026-05-25 (alignment within spec; no adjustments needed)
