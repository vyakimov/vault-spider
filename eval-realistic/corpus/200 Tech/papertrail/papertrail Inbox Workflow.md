---
updated: 2026-06-02T09:05:20
id: 01M6H000000000000000000009
created: 2026-03-11T09:33:52
---
# papertrail Inbox Workflow

A [[papertrail]] note — how paper gets from the doormat into search.

1. Everything lands in the physical inbox tray. Nothing is filed on paper.
2. Batch scan on Sundays: flatbed for anything that lies flat, phone photos for the rest.
3. Files drop into the hot folder `~/papertrail/inbox/`; the watcher picks them up, routes
   flatbed scans and phone photos to the right engine (see [[Tesseract vs PaddleOCR]]), and
   writes text + original into `~/papertrail/archive/YYYY/MM/`.
4. Anything the OCR flags as low-confidence goes to `needs-review/` instead of the archive.
5. The paper itself goes in one dated box per year. Finding things again is the search index's
   job, not the box's.
