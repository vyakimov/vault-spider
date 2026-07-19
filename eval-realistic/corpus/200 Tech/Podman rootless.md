---
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000009
created: 2026-03-30T19:52:31
---

A [[technote]] on rootless Podman, used for [[Larder]].


Compose mostly works with `podman-compose`. This example runs the app plus a valkey cache:

```yaml
services:
  larder:
    image: localhost/larder:latest
    ports:
      - "8123:8123"
    environment:
      - LARDER_SECRET=devsecret123
    volumes:
      - ./data:/data
  cache:
    image: valkey/valkey:7
```

Rootless quirks: published ports below 1024 need `sysctl net.ipv4.ip_unprivileged_port_start`,
and volumes get user-namespace ownership — `podman unshare chown` fixes the weird UIDs.
