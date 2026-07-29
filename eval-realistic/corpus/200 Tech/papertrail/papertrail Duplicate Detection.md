---
tags:
  - homelab
updated: 2026-01-22T10:04:00
id: 01M6D000000000000000000007
created: 2026-03-19T09:08:00
---
Implements SHA-256 hashing of scanned page images to catch duplicates before filing. The hash is computed on the raw image bytes, not the OCR text, so even if a bank sends the same statement with slightly different letterhead, the hash catches it. A few false negatives on statements that genuinely repeat (monthly statements with the same format) but that's rare. When a duplicate is detected, the system alerts me instead of filing it silently, so I can decide whether to keep both or delete the new one.
