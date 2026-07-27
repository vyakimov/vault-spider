---
updated: 2026-01-07T11:06:00
id: 01M6N000000000000000000006
created: 2026-07-07T10:42:00
---
# Millwright Full Text Search

I added SQLite FTS5 full-text search over saved article text, so I can find passages I vaguely remember without scrolling through hundreds of articles manually.

## Implementation
When I save an article, the Millwright worker extracts plain text from the HTML (stripping ads and boilerplate), then inserts it into the FTS5 virtual table. Queries are blazing fast because the index is local on the NAS.

## Quality
The text extraction isn't perfect—PDFs need Tesseract preprocessing, and some sites encode text in images. For 95% of articles, though, search works great. I exclude common words like "the" and "a" from the index to reduce noise.
