---
updated: 2026-05-05T11:57:00
id: 01M6E000000000000000000325
created: 2026-05-04T18:33:00
---
`file myfile` detects file type via magic bytes, not extension. Use `-i` for MIME type, `-b` to omit filename. Reliable for determining if file is ELF, gzip, image, etc.
