---
updated: 2026-06-02T09:10:31
id: 01M6J000000000000000000005
created: 2026-05-19T09:41:03
---
A [[papertrail]] note on routing by OCR confidence.

Per-page mean confidence decides where output lands: above 0.90 goes straight to the archive,
0.75–0.90 goes to the archive but keeps the raw image alongside, below 0.75 goes to
`needs-review/` (see [[papertrail Inbox Workflow]]).

The thresholds came from eyeballing a hundred pages, not science. Lowering the review threshold
below 0.75 mostly surfaces handwriting, which no amount of re-OCRing fixes anyway.
