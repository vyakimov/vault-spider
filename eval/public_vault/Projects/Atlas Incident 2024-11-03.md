---
id: 01JEV000000000000000000183
title: Atlas Incident 2024-11-03
type: incident
created: 2025-04-22T09:00:00Z
updated: 2025-07-01T12:00:00Z
tags: [atlas, project]
---
# Atlas Incident 2024-11-03

## Incident Summary

On November 3, 2024 at 14:23 UTC, one Cedar gateway (station ID 7, Riverside East) stopped accepting sensor join requests, causing 47 wireless sensors to remain silent for 18 minutes. Root cause: a stale RF certificate cached in Cedar's firmware prevented valid LoRaWAN join responses from being transmitted.

## Timeline

- 14:23 UTC: Monitoring alert triggered on Harbor ingestion timeout for station 7
- 14:28 UTC: On-call technician accessed Cedar web console; join response counter stuck at previous value
- 14:32 UTC: Restarted Cedar process; radio module re-initialized, certificates reloaded
- 14:41 UTC: Sensors reestablished connections; readings resumed flowing

## Root Cause

A code path in firmware v3.1.2 failed to reload the LoRaWAN security material after cryptographic key rotation in Harbor. The certificate mismatch was silently ignored rather than logged, making the root cause invisible until the restart forced a fresh load.

## Resolution and Follow-up

Updated firmware to v3.1.3 with explicit certificate validation on startup and error logging. Deployed to all Cedar instances by November 5. Added automated certificate expiry monitoring to Harbor dashboard. Referenced [[Atlas Sensor Hub Decommission Plan - Old Loggers]] to verify older logger firmware was not affected (devices using pre-2024 protocol were safely isolated).

## Prevention

Implemented unit tests for certificate lifecycle in the CI/CD pipeline.
