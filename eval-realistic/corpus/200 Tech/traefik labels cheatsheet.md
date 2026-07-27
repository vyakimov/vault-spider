---
updated: 2026-02-22T15:35:00
id: 01M6E000000000000000000186
created: 2026-01-20T16:55:00
---
`traefik.http.routers.web.rule=Host(example.local)` + `traefik.http.services.web.loadbalancer.server.port=8080` in Docker labels. Middleware: `traefik.http.middlewares.strip.stripprefix.prefixes=/api`. TOML static config + dynamic container labels = no restart on service changes.
