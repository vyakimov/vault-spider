---
tags:
  - homelab
updated: 2026-05-24T10:26:00
id: 01M6D000000000000000000009
created: 2026-05-21T09:22:00
---
Full-text search over 10,000+ scanned documents needed tuning to avoid spam results. Started by lowering the IDF threshold for common finance words (e.g., "account", "statement") so they don't dominate rankings. Then boosted relevance for exact phrase matches and proximity scoring — if two query terms appear close together in the OCR text, it ranks higher. The biggest win was filtering out low-confidence OCR results (where the confidence score is below 0.7) from the search index entirely. That alone cut out 80% of the noise from mangled documents with poor scans. Search latency is still sub-second on the local NAS.
