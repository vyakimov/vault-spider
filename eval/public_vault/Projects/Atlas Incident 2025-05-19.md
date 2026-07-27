---
id: 01JEV000000000000000000184
title: Atlas Incident 2025-05-19
type: incident
created: 2024-05-23T09:00:00Z
updated: 2025-08-02T12:00:00Z
tags: [atlas, project]
---
# Atlas Incident 2025-05-19

## Incident Summary

A major cellular service outage affecting three regional carriers (12:07 to 13:41 UTC on May 19, 2025) triggered automatic failover to secondary SIM cards across eight Cedar gateways. No data loss occurred; Cedar queued 324 batches locally while cellular was degraded, then replayed them in order once connectivity restored.

## Timeline

- 12:07 UTC: Harbor stops receiving batches from eight stations; primary carrier shows network unreachable
- 12:09 UTC: Cedar firmware on affected gateways detects HTTPS timeout and activates secondary SIM profiles
- 12:11 UTC: Harbor metrics show zero ingestion rate; on-call notified
- 12:18 UTC: Traffic resumes on failover carriers at reduced rate (backup network congested)
- 13:41 UTC: Primary carrier network restored; Cedar automatically re-prioritizes primary SIM
- 14:15 UTC: All queued batches processed; Harbor confirms 100% batch acceptance

## Impact

Eight field stations operated blind for ~90 minutes (no telemetry available to dashboard). No sensor data was lost. Queue replay revealed no out-of-order readings because Cedar's internal buffer maintains strict timestamp ordering.

## Follow-up Analysis

This incident validated the Cedar failover logic (see [[Atlas Incident 2024-11-03]] for earlier lessons on robustness). Identified carrier-specific DNS timeouts as a minor inefficiency in secondary SIM activation; improved DNS resolution timeout from 30s to 8s to accelerate failover. Added jitter to batch resubmission to prevent simultaneous replay storms when many gateways reconnect.
