---
tags:
  - homelab
  - photos
updated: 2026-04-25T10:51:00
id: 01M6P000000000000000000002
created: 2026-01-22T09:27:00
---
# Cassowary Face Grouping

The face detection model runs on import and clusters similar faces together automatically. It's surprisingly good at finding the same person across years of photos, but manual merges are still needed for twins, profile shots that fool the detector, and a handful of people the model just consistently splits across multiple clusters.

## Face Merge Backlog

Over 30 clusters still need manual review. The worst offender is a cluster pair for one friend whose photos span a decade — different glasses, lighting, and angles make the model treat them as distinct identities.

## Cluster Quality by Era

Photos from 2018-2019 get stuck more often than recent ones; the model improved with later training data. Full-body shots in group photos are worse than headshots in portraits.
