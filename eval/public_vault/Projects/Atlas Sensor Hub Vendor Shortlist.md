---
id: 01JEV000000000000000000169
title: Atlas Sensor Hub Vendor Shortlist
type: evaluation
created: 2025-08-08T09:00:00Z
updated: 2026-02-13T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub Vendor Shortlist

## Gateway Hardware Candidates

Three vendors competed in final evaluation: Nordic Systems (industrial-grade gateways, $2,800/unit, 12-week lead time), Zenith Networks (mid-market focus, $2,300/unit, 8-week lead time), and VersaTech Solutions (low-cost, $1,600/unit, 20-week lead time). Nordic Systems selected based on firmware flexibility, community documentation, and historical reliability in similar deployments. VersaTech considered but deferred due to lead time constraints and limited support infrastructure.

## Sensor Module Options

Temperature and humidity: Senstech (integrated, $180/unit) vs. EnvironGuard Pro (discrete, $250 but separable). Pressure: Barometric Instruments (high precision, $120) vs. generic pressure sensors ($45). Selected Senstech integration for cost efficiency with EnvironGuard backup sensors for redundancy at critical stations.

## Network Connectivity

Evaluated cellular backup from three carriers; selected provider offering highest uptime SLA (99.2%) in regional footprint. LoRaWAN backhauling via existing municipal network infrastructure preferred where available to reduce recurring costs.

## Performance Validation Results

See [[Atlas Sensor Hub Load Test Results]] for detailed throughput and latency characteristics of the selected gateway under operational load profiles.
