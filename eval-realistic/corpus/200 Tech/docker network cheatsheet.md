---
updated: 2026-04-14T17:29:00
id: 01M6E000000000000000000048
created: 2026-03-12T10:01:00
---
`docker network create mynet && docker run --network mynet --name web myimage` — create custom bridge network and attach containers by name (DNS resolution works).
