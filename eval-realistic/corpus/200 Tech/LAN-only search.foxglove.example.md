---
updated: 2026-06-02T09:10:31
id: 01M6J000000000000000000007
created: 2026-05-21T18:09:32
---
a [[technote]] — the [[papertrail]] search UI, exposed the same way as the pantry app

Same pattern as [[LAN-only larder.foxglove.example]]: a headscale `extra_records` entry points
`search.foxglove.example` at PuddleJumper's tailnet address, and the existing nginx gets a
second server block for it.

```nginx
server {
    listen 100.64.0.9:80;
    server_name search.foxglove.example;
    location / { proxy_pass http://127.0.0.1:8321; }
}
```

The papertrail indexer serves on `localhost:8321`; nothing new to verify beyond the usual
`ss -ltnp` check that nginx still binds only the tailnet address.
