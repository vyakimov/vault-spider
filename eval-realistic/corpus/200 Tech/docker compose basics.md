---
updated: 2026-01-09T16:42:00
id: 01M6E00000000000000000000H
created: 2026-07-07T15:18:00
---
`docker compose up -d` starts services in background; `docker compose logs -f web` streams web service logs. `docker compose exec db psql` runs commands inside container. Override environment via `.env` file; compose loads it automatically. Use `docker compose down -v` to remove volumes on teardown; add `restart: unless-stopped` in service config for persistence.
