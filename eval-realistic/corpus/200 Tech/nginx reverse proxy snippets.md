---
updated: 2026-04-12T19:33:00
id: 01M6E00000000000000000000M
created: 2026-03-10T18:57:00
---
```
upstream backend { server 127.0.0.1:8080; }
server {
  listen 80;
  location / {
    proxy_pass http://backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```
Add `proxy_buffering off;` for streaming; `proxy_read_timeout 300s;` for slow backends. Test config with `nginx -t` before reload.
