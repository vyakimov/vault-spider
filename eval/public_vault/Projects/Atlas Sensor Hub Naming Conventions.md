---
id: 01JEV000000000000000000173
title: Atlas Sensor Hub Naming Conventions
type: reference
created: 2025-03-12T09:00:00Z
updated: 2026-06-17T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub Naming Conventions

## Station Identifiers

Stations named by region abbreviation (N, W, C, S), phase number (1, 2, etc.), and sequence within phase (01-12). Example: N1-03 refers to North region, Phase 1, third station. Alias names mapped to geographic descriptors for human readability (e.g., "N1-03 Ridgeline Post").

## Sensor and Gateway References

Sensors within a station identified by sub-index: N1-03-T for temperature, N1-03-H for humidity, N1-03-P for pressure. Gateway hardware labeled by installation date and regional warehouse code: N1-03-GW-2025-02-001 indicates a gateway installed in North region Phase 1 station 3, February 2025, first unit from that batch.

## Alert and Log Naming

Alert rule identifiers prefixed with station name for traceability: ALERT-N1-03-TMP-HIGH for temperature exceeding configured threshold at North 1-03. Log files rotate using station prefix and timestamp: LOG-N1-03-2025-02-15.tar.gz.

## Stakeholder Coordination

[[Atlas Stakeholder List]] maintains contact information for regional coordinators and site managers referenced throughout project documentation using the standardized naming scheme.
