---
id: 01JEV000000000000000000172
title: Atlas Sensor Hub Dashboard Wireframes
type: note
created: 2024-02-11T09:00:00Z
updated: 2025-05-16T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub Dashboard Wireframes

## Overview Panel

Left-side navigation showing region list with health indicators (green for all stations reporting, yellow for latency anomalies, red for offline stations). Center panel displays the selected region's station inventory with last-reading timestamp and current environmental summary. Right sidebar shows 7-day trend sparklines for primary metrics.

## Station Detail View

Tabbed interface with "Current Readings", "Historical Trends", and "Diagnostics" sections. Current readings show all sensor values with colorized thresholds (normal/warning/critical). Historical trends render as multi-series line charts with configurable time windows (last 24 hours, 7 days, 30 days, custom).

## Alert and Gap Visualization

Dedicated view showing all sensor readings gaps longer than 4 hours over the past 30 days. Color-coded by station and duration. Alert thresholds configurable per station; notification delivery tested with both email and webhook endpoints.

## Context and Refinements

[[Atlas Sensor Hub Retrospective 2024]] informed the design decisions around which metrics to prioritize in the summary view and how to surface operational alerts to field teams.
