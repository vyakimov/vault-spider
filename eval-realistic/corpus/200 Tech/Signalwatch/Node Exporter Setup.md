---
tags:
  - homelab
updated: 2026-02-10T10:06:00
id: 01M6K000000000000000000007
created: 2026-07-07T09:42:00
---
Install node_exporter on each machine as a static binary in `/usr/local/bin`, then use a systemd unit to run it with `--collector.filesystem.fs-types-exclude=tmpfs,fuse.lofs`. The unit file is identical across all hosts; I template it in ansible or just copy-paste.

```
[Unit]
Description=Prometheus Node Exporter
After=network.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/local/bin/node_exporter --collector.filesystem.fs-types-exclude=tmpfs,fuse.lofs
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Run `systemctl enable node_exporter` and `systemctl start node_exporter` on each host. Prometheus scrapes port 9100 on each. The `--collector.filesystem.fs-types-exclude` flag skips tmpfs (reduces noise). Firewalling: node_exporter only listens on localhost by default, so I rely on the Tailscale tunnel for remote access.
