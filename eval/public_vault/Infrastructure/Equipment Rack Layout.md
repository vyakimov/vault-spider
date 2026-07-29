---
id: 01JEV000000000000000000105
title: Equipment Rack Layout
aliases: []
type: reference
created: 2025-06-24T09:00:00Z
updated: 2026-09-03T12:00:00Z
tags: [infrastructure]
---
# Equipment Rack Layout

## Rack Physical Dimensions and Environmental Specs

The equipment rack is a 42U standard 19-inch enclosed cabinet (Rittal TS 8 frame, stainless steel 304 grade) located in the field-office equipment room. The cabinet dimensions are 600 mm (W) × 800 mm (D) × 2,000 mm (H) with active climate control (Rittal cooling unit maintaining 18–24 °C ± 2 °C).

**Cabinet specifications:**
- Power capacity: 32 A at 208 V AC (6.6 kVA total, dual breaker circuit)
- Cooling capacity: 8 kW active air conditioning (maintains max inlet temp <30 °C)
- Security: Electronic lock with key override; access log maintains last 10,000 entries
- Grounding: Dedicated star-point ground connection to facility ground grid (measured <1 Ω resistance)

## Current Equipment Layout (as of 2026-09)

| Rack Units | Equipment | Model | Ports | Power | Notes |
|-------------|-----------|-------|-------|-------|-------|
| 1U–2U | Main network switch | Juniper EX2300-48P | 48x GE + 4x QSFP+ | 400 W | Redundant dual PSU installed |
| 3U | Secondary switch (standby) | Arista 7050SX3-48YC12 | 48x 25G + 12x QSFP28 | 300 W | Online, not actively forwarding traffic |
| 4U–5U | Border router | Juniper MX204 | 8x QSFP+ | 250 W | Primary internet gateway; dual routing engines |
| 6U | Cellular modem (failover) | Cradlepoint IBR900 | 2x GE | 35 W | Shielded RF enclosure to reduce interference |
| 7U–9U | Storage/NAS | QNAP TS-432PX | 4x GE (10G optional) | 200 W | 8 TB usable storage; runs BIND DNS service |
| 10U | Console/IPMI aggregation | Serial console server (Lantronix) | 8x serial ports | 45 W | Out-of-band management; redundant network paths |
| 11U | PDU distribution (primary) | Eaton 93PM 10 kVA | 32x outlets | N/A (monitored input) | Dual input feeds from separate utility circuits |
| 12U | Battery backup (UPS) | Eaton 93PM batteries | – | Charger 500 W | 10 kVA rated; battery modules in 13U below |
| 13U–14U | UPS battery modules | Eaton OEM modules | – | 500 W (charging) | Module A and B; total 15 kWh energy storage |
| 15U | PDU distribution (secondary) | Vertiv PDU (rackmounted) | 24x outlets | N/A | Secondary circuit distribution; not currently populated |
| 16U–20U | **Spare rack space** | – | – | – | Reserved for expansion; adequate cooling airflow maintained |
| 21U–24U | Generator control interface | Generac Smart Transfer Switch | – | 50 W (monitoring) | Monitors generator status and coordinates failover |
| 25U–42U | **Open ventilation/airflow** | – | – | – | Critical for cable management and cooling circulation |

## Airflow and Thermal Management

Equipment is arranged following a "hot aisle / cold aisle" configuration:
- **Cold aisle** (front): Intake air from room air conditioning (18–24 °C)
- **Hot aisle** (rear): Exhaust air returned to room circulation and re-cooled
- Blanking panels are used in all unused rack spaces to prevent bypass airflow

Annual thermal imaging is performed to verify that no equipment is operating above design temperature limits. No hot spots have been identified since rack commissioning in 2023.

## Cable Management and Routing

Cables are segregated by type:
- **Network**: CAT6a backbone runs in overhead tray (separate from AC mains)
- **AC mains**: Separate conduit to minimize EMI coupling
- **Serial/console**: Shielded twisted pair in dedicated wire loom
- **Fiber**: Protected runs in blue PVC conduit with stress relief

All cables are labeled per the [[Cable Labeling Standard]] specification and documented in the [[Ethernet Cable Runs Map]].

## Expansion Planning and Lifecycle

Current equipment loading is approximately 60% of available power and 40% of available rack space. Projected growth analysis estimates full capacity will be reached in approximately 36 months (2029 planning horizon).

Planned upgrades include:
- Secondary site switch refresh (Q4 2027)
- Router capacity upgrade to Juniper MX480 (Q2 2028, coincides with current MX204 end-of-support)

Related maintenance including [[Generator Maintenance Log|power system testing]] is coordinated to avoid concurrent work in the equipment room.

---
**Last physical audit:** 2026-09-03 (all equipment verified in rack; no changes needed)
