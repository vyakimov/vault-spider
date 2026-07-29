---
id: 01JEV000000000000000000188
title: Atlas Roadmap 2027 Draft
type: project
created: 2024-09-01T09:00:00Z
updated: 2025-03-06T12:00:00Z
tags: [atlas, project]
---
# Atlas Roadmap 2027 Draft

## Strategic Goals (Draft)

This roadmap reflects early brainstorming for 2027 capabilities. Final approval pending Q4 2026 strategic review.

- Expand sensor network to 500 stations (from current 120)
- Add multi-protocol gateway support (Sigfox, NB-IoT alongside LoRaWAN)
- Integrate real-time anomaly detection using edge ML models
- Automate sensor calibration verification workflows

## Proposed Architecture Changes

Harbor API would support pluggable ingestion adapters for each radio protocol. Cedar would gain optional edge-compute capability via container runtime for light models. Dashboard would show AI-flagged anomalies in real time.

## Resource Constraints

Estimated engineering effort: 18 person-months across firmware, backend, and ops. Hardware cost for 380 additional gateways: $285K. Staffing and timeline under review.

## Risk Assessment

Multi-protocol support increases testing complexity and vendor coordination surface area. Edge ML requires careful power budgeting on Cedar (current power envelope already tight in polar deployments). Recommend parallel prototyping of Sigfox and NB-IoT adapters in Q1 2026 to validate effort estimates.

## Status

**DRAFT ONLY** — not approved for planning or procurement. Intended for stakeholder discussion.
