---
id: 01JEV000000000000000000088
title: Lightning Protection Notes
aliases: []
type: reference
created: 2024-07-07T09:00:00Z
updated: 2024-01-12T12:00:00Z
tags: [infrastructure, safety]
---
# Lightning Protection Notes

## Grounding System Architecture

All exposed metal structures and antenna masts are bonded to a common ground grid installed at a nominal 1.2 m depth below grade. The primary ground rod array consists of eight copper-bonded steel rods (5/8 inch diameter, 10 feet length, spaced 10 feet apart) arranged in a radial pattern beneath the observation tower base.

**Grounding path specification:**
- Main mast-to-ground bond: 0 AWG copper cable, direct solder joint (ultrasonic tested for continuity)
- Secondary equipment frame bonds: 4 AWG copper jumpers with listed mechanical lugs (M10 stainless bolts)
- Measured loop resistance: 1.8 ohm (target <2.0 ohm per NFPA 780)
- Verification testing: annually via fall-of-potential method per IEEE 81 standard

The secondary ridge site uses an identical architecture scaled to the smaller mast (50-foot vs. 80-foot height).

## Surge Arrestor Placement and Coordination

Two-stage surge protection is deployed at all network infrastructure entry points:
- Primary protector (MOV-based 120 kVA silicon carbide) installed at the cabinet input where coaxial cables and Ethernet feeds enter from outdoor runs
- Secondary protector (hybrid GDT + crowbar type) deployed inside the cabinet at the equipment ports

Arrestor selection follows ITU-T K.20 recommendation for category 3 indoor installation with a 20 kA nominal discharge current rating. All arrestors are regularly inspected for thermal indicators and replacement is mandatory when indicator discoloration appears (indicating prior surge event).

## Related Safety and Maintenance

The grounding system is visually inspected quarterly for corrosion and soil subsidence. The observation tower's antenna element is re-tensioned every 18 months as wind loading and temperature cycles induce cable slack—improper tension reduces the lightning ground strike efficiency below the design 95% figure.

Maintenance personnel are required to disable all network equipment at least 30 minutes before severe thunderstorm events per site safety policy; this allows arrestors to fully discharge any residual charge.

---
**Certification:** NFPA 780 Class 1, IEEE 62-1991 verified
