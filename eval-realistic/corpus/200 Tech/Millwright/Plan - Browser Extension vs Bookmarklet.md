---
tags:
  - homelab
  - project
updated: 2026-01-20T10:56:00
id: 01M6N000000000000000000002
created: 2026-03-17T09:52:00
---
## Capture Mechanism: Extension vs Bookmarklet

A full browser extension (Chrome/Firefox) can capture page metadata (title, URL, excerpt, metadata) and batch-send to Millwright. Permissions required: read page content, access clipboard, network calls. More work to build and maintain across browsers.

A bookmarklet (JavaScript snippet in browser bookmarks bar) is simpler: one click, POST request, done. No permissions prompt, no extension review process. Bookmarklets are more portable (any browser, any device) and I've had decent results with them for quick capture. Downside: no automatic page-parsing, so I'd need to manually add title/excerpt or rely on server-side extraction via Open Graph tags.

**Current decision:** Start with bookmarklet for MVP, add a full extension later if usage justifies the complexity. The bookmarklet approach keeps friction low and lets me validate the idea without over-engineering.
