---
id: 01JEV000000000000000000196
title: Atlas Design Review - Gateway Firmware
type: review
created: 2024-08-09T09:00:00Z
updated: 2025-02-14T12:00:00Z
tags: [atlas, project]
---
# Atlas Design Review - Gateway Firmware

## Scope and Objectives

This design review examines the firmware architecture for Cedar, the field gateway that collects and queues sensor readings. The review covers the LoRaWAN reception stack, SQLite queue management, and batch transmission logic to Harbor.

## Current Implementation Assessment

Cedar's firmware revision 3.2 implements interrupt-driven LoRaWAN reception with DMA transfers to the on-board radio module. The SQLite queue stores incoming readings with metadata: sender ID, signal strength, timestamp, and payload. Transmission batches are triggered either by queue depth (200+ readings) or elapsed time (10 minutes), whichever comes first.

## Firmware Update Rationale

The proposed update refines the transmission retry logic and improves error handling during network outages. Current retry behavior uses fixed backoff; the update introduces adaptive retry intervals based on network conditions and adds telemetry to track failed transmission attempts.

## Testing Requirements

Before deployment, validate that queue integrity is maintained during power cycles, batch transmission succeeds under cellular degradation scenarios, and memory utilization remains stable over 30-day operation periods.
