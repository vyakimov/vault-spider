---
updated: 2026-01-21T14:18:00
id: 01M6E000000000000000000185
created: 2026-07-19T15:42:00
---
```
example.local {
  reverse_proxy localhost:8080
}
```
Caddy auto-renews TLS (even for .local if internal PKI). `handle_path /api/* { reverse_proxy backend:5000 }` strips path prefix. Simpler syntax than nginx; native http.server module for file serving.
