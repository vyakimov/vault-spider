---
id: 01JEV000000000000000000176
title: Atlas Sensor Hub Alerting Design
type: note
created: 2024-06-15T09:00:00Z
updated: 2025-09-20T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub Alerting Design

## Threshold Definition and Tuning

Alert thresholds defined per station based on regional climate norms and sensor-specific measurement ranges. Initial thresholds derived from historical data and field expertise; refined quarterly based on false positive rates. Temperature alerts fire if readings exceed mean ± 2.5 standard deviations; humidity alerts if below 20% or above 95%.

## Alert Propagation

Alerts generated in-stream by the ingestion system and queued for asynchronous delivery. Three severity levels: INFO (anomalies for trend monitoring), WARNING (actionable items like sensor drift), and CRITICAL (station offline or data loss detected). Delivery channels include email, webhook, and in-application notification badge.

## Suppression and Correlation

Repeated identical alerts for the same station suppressed for 4 hours to avoid operator fatigue. Correlated alerts (e.g., all sensors in a station offline simultaneously) grouped into single incident record. Incident closed automatically after 30 minutes of normal operation resumed.

## Integration with Operations Runbook

Alert rules codified in runbooks that operations teams reference when responding to notifications. Example: "CRITICAL-STATION-OFFLINE triggers network connectivity check, gateway reboot validation, and escalation to regional technician if issue persists beyond 15 minutes."
