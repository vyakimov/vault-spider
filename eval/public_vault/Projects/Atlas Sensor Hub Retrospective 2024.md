---
id: 01JEV000000000000000000163
title: Atlas Sensor Hub Retrospective 2024
type: review
created: 2025-02-02T09:00:00Z
updated: 2026-05-07T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub Retrospective 2024

## What Went Well

The initial prototype exceeded power consumption targets, achieving 14-day autonomy on standard lithium batteries under continuous operation. Vendor selection process proved sound; the chosen gateway hardware remained stable through three firmware iterations without hardware regressions. Training program for field technicians completed ahead of schedule with 95% certification pass rate on first attempt.

## Challenges and Lessons

Early firmware releases had edge cases in batch retry logic during high-latency conditions. Resolved through pinning retry backoff to device clock state. Site preparation timelines slipped by three weeks in two locations due to infrastructure access constraints that were not initially surfaced in site surveys. Updated survey template to include electrical access verification checklist.

## Technical Adjustments

Modified LoRaWAN spreading factor tuning based on trial site terrain analysis. Documented that lower spreading factors were viable at three of five planned station locations, enabling reduced power draw by approximately 12% at those sites.
