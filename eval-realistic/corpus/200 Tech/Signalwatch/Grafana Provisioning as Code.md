---
tags:
  - homelab
updated: 2026-01-09T10:55:00
id: 01M6K000000000000000000006
created: 2026-06-06T09:35:00
---
Dashboards live in a git repo and are provisioned on container startup. I had manually created dashboards in the web UI once; when I rebuilt the host, they vanished. Now the compose file mounts a dashboard folder, Grafana loads them on init, and any changes I make via YAML are version-controlled. The provisioning format is finicky (nested JSON objects with specific key names), so I mostly copy-paste existing dashboards and tweak values. No fancy schema validation; I just restart the container and check for errors in the logs. Alerting channels (Slack, email) are also provisioned, which is cleaner than manual webhook setup. The datasource (Prometheus) is provisioned too, so a fresh deployment has everything connected without UI clicks.
