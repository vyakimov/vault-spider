---
id: 01JEV000000000000000000028
title: Atlas Sensor Vendor Evaluation
type: evaluation
created: 2024-08-14T10:30:00Z
updated: 2024-09-02T16:00:00Z
tags: [atlas, sensors, hardware]
---
# Atlas Sensor Vendor Evaluation

## Requirements

LoRaWAN uplink, field-replaceable batteries, an IP67 enclosure, and a vendor that publishes its
payload format instead of locking it behind a portal.

## Candidates

- **Meadowlark ML-30** — open payload docs, standard connectors, dull in the best way.
- **Vantora Edge** — nicer enclosure, but payloads decode only through the vendor cloud.
- **PulseField P2** — cheapest, weakest battery story, firmware updates require a bench cable.

## Decision

Meadowlark ML-30 for all new deployments. The open payload format matters more than enclosure
polish: [[Atlas Sensor Hub Architecture|Cedar]] can decode uplinks without any vendor dependency.
Existing sensors stay in service until they fail.
