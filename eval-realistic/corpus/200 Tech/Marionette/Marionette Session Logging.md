---
tags:
  - homelab
  - llm
updated: 2026-05-10T10:52:00
id: 01M6A000000000000000000009
created: 2026-05-07T09:44:00
---
Session transcripts log to `/mnt/marionette/sessions/` as gzipped JSONL files, one per conversation. Transcripts include prompts, tool calls, and all model responses but strip out binary data (file uploads, images). Rotation happens weekly; logs older than 90 days get moved to cold storage on the NAS (a separate RAID-6 shelf with slower spindles). I can restore a 6-month-old session in about 2 minutes, 6+ months takes a restore request to NAS management. The logging is asynchronous so it never blocks the agent, even if storage is slow.
