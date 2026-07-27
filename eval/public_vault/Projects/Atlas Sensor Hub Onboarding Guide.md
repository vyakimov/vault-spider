---
id: 01JEV000000000000000000179
title: Atlas Sensor Hub Onboarding Guide
type: guide
created: 2025-09-18T09:00:00Z
updated: 2026-03-23T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub Onboarding Guide

## Site Preparation

Before deploying a new Cedar gateway to a field location, prepare the installation site with standard environmental controls. Ensure network connectivity via cellular backup; verify power stability with 120V service or verify UPS capacity for 8 hours minimum runtime. Site survey should confirm LoRaWAN radio line-of-sight to at least 60% of planned sensor placements.

## Initial Deployment Checklist

Bring the gateway online using the following steps:

- Unbox Cedar and verify all components (antenna, Ethernet cable, power supply, SIM card)
- Flash current firmware image to internal storage
- Insert SIM card and power on; wait for cellular registration indicator (green LED)
- Access the Cedar web console on local network and configure:
  - Site ID and geographic coordinates
  - Harbor ingestion endpoint and API credentials
  - LoRaWAN join channel and frequency plan for region
- Run radio self-test to confirm antenna tuning
- Deploy test sensors within 500 meters and observe batch transmission logs

## Operational Handoff

Once readings flow consistently for five full days, coordinate with Harbor operations to enable the dashboard view. Confirm the site appears in the station list within 2 hours of first submission. Escalate to Harbor team if batches fail validation or HTTP 40x responses appear in Cedar logs. Document any local network constraints (e.g., firewall proxy rules) in the site notes for the technician on-call.

## Related References

See [[Atlas Sensor Hub Test Plan]] for validation procedures after deployment.
