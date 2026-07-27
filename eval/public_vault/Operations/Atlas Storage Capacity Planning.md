---
id: 01JEV000000000000000000142
title: Atlas Storage Capacity Planning
type: note
created: 2025-07-16T09:00:00Z
updated: 2025-01-21T12:00:00Z
tags: [atlas, operations]
---
# Atlas Storage Capacity Planning

## Current Capacity Status

**PostgreSQL Data Volume**
- Current usage: 340 GB (as of 2026-07-20)
- Allocated volume size: 500 GB
- Available headroom: 160 GB (~32%)
- Growth rate: ~8–10 GB per month

**Cedar Gateway Local Queue**
- Capacity: ~5000 batches per Cedar unit
- Average batch size: 48 KB (compressed)
- Current typical queue depth: 5–20 batches during normal operations

## Growth Projection

At current sensor deployment (5 active stations, 4 readings per hour per station), Atlas produces approximately 480 readings per day. Combined with historical metadata and quality logs, this translates to ~2.4 GB of new data monthly.

**Estimated expansion timeline:**
- August 2026: Projected usage ~350 GB (87% capacity)
- September 2026: Projected usage ~360 GB (72% headroom)
- October 2026: Projected usage ~370 GB (66% headroom)
- **Action trigger: When >80% capacity (400 GB), evaluate expansion options**

## Expansion Options

1. **Cloud Volume Expansion** (recommended)
   - Resize current 500 GB volume to 1 TB via cloud provider console
   - Requires <2 minutes downtime; PostgreSQL is paused during extension
   - Cost: ~$50/month for additional 500 GB of SSD storage

2. **Database Optimization** (medium priority)
   - Compress older historical data (>1 year old) to cold storage tier
   - Implement read-only archival tables for sensor readings older than 6 months
   - Estimated storage savings: ~30–40%

3. **Retention Policy Adjustment** (lower priority)
   - Reduce raw sensor reading retention from 24 months to 12 months
   - Aggregate older data into daily/weekly summaries
   - Risk: Loss of audit trail for historical analysis

## Related Planning

Capacity discussions inform the on-call rotation discussions (see [[Atlas On-call Rotation]]) regarding when escalations trigger during peak load. The vendor contact process (see [[Atlas Sensor Calibration Log 2024]]) is also coordinated with capacity planning for new station deployments.

Next review date: August 2026.
