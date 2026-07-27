---
id: 01JEV000000000000000000085
title: Weatherproof Enclosure Standards
aliases: []
type: reference
created: 2025-04-04T09:00:00Z
updated: 2025-07-09T12:00:00Z
tags: [infrastructure]
---
# Weatherproof Enclosure Standards

## IP Rating Requirements by Equipment Class

All outdoor-mounted equipment must be housed in enclosures rated **IP67 minimum** (dust-tight, immersion to 1 meter for 30 minutes). High-altitude sites subject to sustained wind and salt spray require IP69K certification. The facility standardizes on Rittal and Schneider Electric stainless-steel (304/316 grade) enclosure frames to ensure longevity in the coastal environment.

**Equipment-specific standards:**
- Access point antennas and transceivers: IP67 sealed polycarb domes with polycarbonate RF-transparent windows
- Battery disconnect switches and DC fuses: IP67 stainless terminal boxes
- Sensor data loggers and telemetry modems: IP66 minimum with drip-proof cable entry design
- Power distribution (solar combiner boxes, charge controller enclosures): IP54 minimum with weatherstrip gaskets rated to −40 °C to +60 °C

Internal humidity is monitored passively via silica-gel indicator cartridges in each enclosure; cartridges are inspected during quarterly maintenance and replaced when saturation exceeds 60% RH.

## Cable Gland and Entry Specifications

All penetrations use spiral-wrapped cable glands with elastomer compression seals rated to IP68. Gland sizing follows the IEC 61076-2-109 specification: single-entry glands accommodate up to three individual conductors (14 AWG equivalent); larger bundles require multi-entry manifolds.

UV-resistant cable jacket is mandatory for exterior runs. Metallic armoring is used for underground and overhead runs exposed to abrasion. Cable slack is maintained inside each enclosure to allow for thermal contraction without tension-induced seal degradation.

## Installation and Field Deployment

Enclosures are mounted on stainless-steel stands with rubber isolation feet (0.5 inch deflection at rated load) to prevent vibration-driven corrosion and salt spray pooling. South-facing surfaces receive white powder-coat touch-up annually to maintain solar reflectivity and corrosion resistance.

All connections to [[Backup Internet Failover Test|backup systems]] and the [[WireGuard Network - Current|primary network infrastructure]] maintain identical environmental sealing standards; no exceptions are granted for emergency or temporary installations.

---
**Standards references:**
- IEC 60529 (IP rating definition)
- NEMA 4X (stainless-steel corrosion resistance, US equivalent)
- IEC 61076-2-109 (cable gland sizing and derating)
