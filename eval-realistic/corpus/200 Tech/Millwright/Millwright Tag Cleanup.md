---
tags:
  - homelab
updated: 2026-05-22T10:18:00
id: 01M6N000000000000000000004
created: 2026-05-19T09:06:00
---
After 6 months of capturing links, I'd accumulated near-duplicate tags: "reading", "read-later", "to-read" all meant the same thing. Wrote a one-off Python script to:

1. List all tags and their usage counts.
2. Manually merge: "reading" + "to-read" -> "reading", delete the others.
3. Update all rows in link_tags to point to the canonical tag.
4. Verify no orphaned tags remain.

Takes ~30 seconds. Did this once, no plans to automate it further. The lesson: tag discipline upfront saves cleanup work. I now have a mental taxonomy (reading, reference, project-notes, tutorial, archive) and stick to it. Running the cleanup script again would be easy if needed; didn't bother with a fancy migration framework.
