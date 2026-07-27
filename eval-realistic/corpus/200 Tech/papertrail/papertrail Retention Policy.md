---
tags:
  - homelab
updated: 2026-03-23T10:15:00
id: 01M6D000000000000000000008
created: 2026-04-20T09:15:00
---
I keep original scans (the raw TIFF files) for 24 months after filing, then shred the paper and keep only the OCR'd and filed documents. The 24-month window covers most IRS retention periods and gives me time to resolve tax questions. After 24 months, I have no need for the original scan anymore — the OCR text is searchable, and the PDF is archived on the NAS. The retention metadata is stored in the database so the archival process is fully automated; an overnight cron job identifies files older than 24 months and moves them to cold storage, with a log entry for audit purposes.
