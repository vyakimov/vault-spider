---
updated: 2026-03-13T16:12:00
id: 01M6E000000000000000000047
created: 2026-02-11T09:48:00
---
`docker volume create mydata && docker run -v mydata:/data myimage` — create named volume and mount it. Use `docker volume inspect mydata` to see mount path on host.
