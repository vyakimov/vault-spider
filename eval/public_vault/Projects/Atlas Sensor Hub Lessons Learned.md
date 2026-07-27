---
id: 01JEV000000000000000000180
title: Atlas Sensor Hub Lessons Learned
type: note
created: 2024-01-19T09:00:00Z
updated: 2024-04-24T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub Lessons Learned

## Deployment Sequencing

The 2024 rollout revealed that deploying Cedar gateways ahead of Harbor readiness created confusion about which component owned network troubleshooting. Future phases must stage infrastructure in order: Harbor and PostgreSQL first, then field gateways. This prevents technicians from debugging phantom connection errors on Cedar when the ingestion API is not yet accepting traffic.

## Team Communication

Splitting sensor procurement from firmware development created repeated miscommunications about chip availability and driver support. Establish a single vendor coordination point and weekly sync between hardware and software leads. Use the [[Atlas Dependency Map]] to track component sourcing alongside development milestones.

## Training and Documentation

The initial cohort of field technicians required 4 weeks of on-site shadowing before they could troubleshoot log patterns independently. Document common failure modes (timeouts, malformed batches, certificate mismatches) and expected behavior in the first 24 hours of operation. Reduce this timeline for future rollouts.

## Vendor Commitments

Request explicit SLAs from cellular carriers for failover latency and uptime guarantees. One vendor's undefined backup network caused a 3-hour outage in late 2024 that could have been flagged in the contract phase.
