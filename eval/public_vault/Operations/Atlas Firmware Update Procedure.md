---
id: 01JEV000000000000000000029
title: Atlas Firmware Update Procedure
type: runbook
created: 2025-03-12T11:00:00Z
updated: 2025-06-18T09:30:00Z
tags: [atlas, operations, firmware]
---
# Atlas Firmware Update Procedure

## Staged rollout

1. **Bench unit first.** Flash the spare sensor on the bench and let it run for 48 hours.
2. **One field sensor.** Update the most accessible field sensor and watch it for a week.
3. **Fleet.** Update the rest one at a time, never more than two in a single day.

## Before each update

Confirm the sensor's recent readings look normal in the dashboard, and note the currently
installed version so the rollback target is written down before anything changes.

## Rollback

Every sensor keeps the previous image in its second slot; a failed boot falls back
automatically. A sensor that comes back with garbled readings is reflashed from the bench image
rather than debugged in the field.

## What this procedure does not cover

Gateway software on Cedar and API deployments on Harbor follow the ordinary release process,
not this procedure. Alert thresholds live in [[Atlas Telemetry Runbook]].
