---
id: 01JEV000000000000000000194
title: Atlas Open Questions
type: note
created: 2024-06-07T09:00:00Z
updated: 2025-09-12T12:00:00Z
tags: [atlas, project]
---
# Atlas Open Questions

## Hardware and Deployment

**Q: Which battery pack vendor will we finalize for Phase 3?**
Our evaluation (see [[Atlas Sensor Hub Vendor Shortlist]]) is narrowed to two candidates. Cost difference is 18% but cycle-life impact is unclear. Need field validation under real conditions before June 2026 decision gate.

**Q: Can we deploy to marine environments without enclosure modifications?**
Saltwater sites require stainless steel enclosures; IsoBox polycarbonate units may suffer UV/salt degradation faster than current estimates suggest. Referenced in [[Mercury Data Migration Vendor Notes]] as a parallel concern for coastal observation infrastructure.

## Data Architecture

**Q: How will we handle schema evolution for new sensor types?**
Current [[Atlas Sensor Hub Data Model]] schema is optimized for temperature/humidity/pressure. Adding soil moisture or water-quality sensors requires JSONB flexibility without performance regression. See [[Mercury Data Migration Schema Diff]] for comparison with other large-scale data systems.

**Q: What's the long-term cost of 90-day raw data retention?**
PostgreSQL storage costs grow linearly with station count. Need analysis at 500-station scale to justify indefinite retention of hourly/daily summaries.

## Operational and External

**Q: Should we adopt a public API for third-party data access?**
Several academic partners (noted in [[Atlas Project Glossary]]) have requested programmatic access. Open API increases visibility but requires API versioning and SLA commitments. Trade-offs under discussion.

**Q: How do we correlate Atlas readings with other observatories?**
[[Mercury Observation Notes - March 2025]] documents atmospheric conditions that overlap with Atlas measurement windows. Integrated cross-platform queries would require metadata normalization and schema alignment work.

**Q: What vendor SLAs apply to field hardware replacement?**
Cedar and sensor modules sometimes fail in the field. Replacement turnaround time currently 3–4 weeks. Need contractual SLA commitments or in-region spare depot strategy for [[Mercury Data Migration Retrospective]] scale operations.
