---
id: 01JEV000000000000000000001
title: Atlas Sensor Hub Overview
aliases: [Atlas Hub]
type: project
created: 2024-01-12T09:00:00Z
updated: 2025-03-10T15:30:00Z
tags: [atlas, sensors, overview]
---
# Atlas Sensor Hub Overview

Atlas is a fictional environmental-monitoring system used at a small field station. Battery-powered
sensors report air temperature, relative humidity, rainfall, and soil moisture every five minutes.
The system is a public demonstration corpus: it contains operational details but no people, customer
records, or personal data.

## Objectives

- Continue collecting readings for at least 48 hours when the internet connection is unavailable.
- Make gaps, delayed batches, and calibration status visible to an operator.
- Keep deployment and recovery simple enough for one small team to maintain.

## System outline

Sensors send readings to the [[Atlas Sensor Hub Architecture|Cedar gateway]]. The gateway buffers
them locally and forwards batches to the Harbor API when connectivity is available. A dashboard
shows the latest observations and a daily summary called the Beacon report.

## Related notes

- [[Atlas Sensor Hub Architecture]]
- [[Atlas Sensor Hub Deployment]]
- [[Atlas Project Glossary]]
- [[Atlas Telemetry Runbook]]

