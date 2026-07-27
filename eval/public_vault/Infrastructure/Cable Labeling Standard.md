---
id: 01JEV000000000000000000100
title: Cable Labeling Standard
aliases: []
type: reference
created: 2024-01-19T09:00:00Z
updated: 2024-04-24T12:00:00Z
tags: [infrastructure]
---
# Cable Labeling Standard

## Label Format and Content Specification

All network and power cables in the equipment cabinet and field installations must be labeled at both endpoints using a standardized format. Labels are created using a laminated polyester label maker (Brady TLS 2200 or equivalent) with UV-resistant ink to survive outdoor sun exposure.

**Label format:**

```
[CABLE-ID] | [SOURCE] → [DEST]
[DATE-INSTALLED] | [GAUGE/TYPE]
```

**Example labels:**
```
MAIN-01 | SW-GE-0/0/0 → Fiber ISP
2024-01-10 | CAT6a-Armored
```

```
POE-TOWER-A | PoE-Inj-1 → Antenna-Array-North
2023-06-15 | CAT5e-PoE
```

## Cable Identification System

Cable IDs follow the naming convention `[PREFIX]-[NUMBER]`:
- **MAIN-** (01–12): Primary backbone connections within the cabinet
- **POE-** (01–20): Power-over-Ethernet feeds to remote sites
- **PWR-** (01–08): AC mains and DC power distribution cables
- **SPARE-** (01–16): Pre-installed spare runs for future expansion
- **SERIAL-** (01–04): Console and out-of-band management connections

Length notation (optional): Append `_[LENGTH-FT]` for cables >30 feet (e.g., `MAIN-03_2800FT` for the 2.8 km tower site backbone run).

## Label Placement and Maintenance

- Primary label: attached at the source port/device connector using a cable sleeve or heat-shrink tubing
- Secondary label: attached 6 inches from the destination end for quick identification during troubleshooting
- Redundancy: if a single label becomes unreadable due to UV fading or abrasion, the cable is replaced rather than relabeled

Labels are inspected during quarterly maintenance cycles and replaced if text becomes illegible or if adhesive begins to degrade. A permanent record of all cable changes is maintained in the [[Ethernet Cable Runs Map]].

## Cross-References and Documentation

The canonical map of all cable runs and their port assignments is stored in the facility's centralized infrastructure database and also documented in the [[Ethernet Cable Runs Map]] reference guide. This guide must be updated whenever a cable is added, removed, or rerouted.

---
**Standard adoption date:** 2024-01-19
**Last audit:** 2024-04-24 (all labels verified and current)
