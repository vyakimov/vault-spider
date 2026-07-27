---
updated: 2026-06-17T14:48:00
id: 01M6E000000000000000000155
created: 2026-05-15T09:12:00
---
Pipe CSV to markdown: `column -t -s, | sed 's/^/| /' | sed 's/$/ |/' | sed '1s/^/| /' | sed '2i|---|' `. Or use a web tool like Markdown Table Generator to paste CSV and export as Markdown rows.
