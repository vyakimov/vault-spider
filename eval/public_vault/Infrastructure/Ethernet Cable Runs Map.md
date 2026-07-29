---
id: 01JEV000000000000000000087
title: Ethernet Cable Runs Map
aliases: []
type: reference
created: 2025-06-06T09:00:00Z
updated: 2026-09-11T12:00:00Z
tags: [infrastructure, networking]
---
# Ethernet Cable Runs Map

## Main Backbone Topology

The equipment cabinet contains a Juniper EX2300-48P managed switch serving as the layer-2 aggregation point. The following CAT6a cable runs feed primary infrastructure:

| Cable ID | Source Port | Destination | Distance | Notes |
|----------|-------------|-------------|----------|-------|
| MAIN-01 | GE-0/0/0 | Field office uplink (primary ISP) | 620 m | Armored, buried conduit, 2 splice points |
| MAIN-02 | GE-0/0/1 | Cellular modem WAN | 3.2 m | Within cabinet, shielded twisted pair |
| MAIN-03 | GE-0/0/2 | Primary observation tower (PoE injector) | 2.8 km | Aerial run on utility poles, lightning arrestors at both ends |
| MAIN-04 | GE-0/0/3 | Secondary ridge site (outdoor switch, PoE) | 4.1 km | Split: 2.2 km underground, 1.9 km aerial, single pole-mounted splice box |
| MAIN-05 | GE-0/0/4 | Field office gateway/NAS device | 12 m | Indoor, wall-mounted conduit |

## Secondary and Diagnostic Connections

**Management console connections:**
- Port GE-1/0/1: Console/diagnostics laptop dock (daisy-chain three 1 GbE interfaces via unmanaged switch for A/B testing)
- Port GE-1/0/2: Out-of-band admin laptop (isolated VLAN 250, 10.60.1.0/28 documentation subnet)

**PoE-powered field devices:**
- Ports GE-1/0/5–GE-1/0/8: Reserved for future environmental sensors (4× available PoE feeds at 65 W per port)
- Ports GE-1/0/9–GE-1/0/12: Secondary wireless access point (provisioned but offline)

## Cable Routing and Physical Plant

All runs are identified by adhesive color-coded labels at both endpoints (see [[Cable Labeling Standard]] for label format). Backbone runs are segregated from AC mains circuits by a minimum 30 cm horizontal clearance within the cabinet. Vertical runs in the cabinet use cable trays with drip-proof design to prevent condensation pooling.

Splices are implemented only at designated junction boxes; inline crimped connectors are not permitted. All outdoor connectors are weatherproofed with silicone end caps.

---
**Last updated:** 2026-09-11 (MAIN-04 secondary site conversion completed)
