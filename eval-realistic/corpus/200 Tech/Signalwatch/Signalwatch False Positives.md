---
tags:
  - homelab
  - incident
updated: 2026-03-07T10:33:00
id: 01M6K000000000000000000004
created: 2026-04-04T09:21:00
---
Alerts that fire during maintenance windows keep waking me up. Added `maintenance=true` labels to suppress alerts during scheduled reboots; need to remember to label the nodes before restarts. The Raspberry Pi running Tailscale consistently flaps at 2am (power brownout?); adjusted the link-down threshold to 3 minutes to ignore brief dropouts. CPU threshold on PuddleJumper was firing during automated backups; switched that rule to only alert if sustained above 75% for 5+ minutes rather than any spike. Disk alerts on Bramble were noisy because `/var/log` fills up before rotation kicks in; now using a separate volume and smaller retention window. One false alarm was the Grafana query itself timing out, which looked like missing data — switched to a slower scrape interval instead of trying to read 30 days instantly. The pattern: test alerting on a non-prod machine first. I've disabled email notifications for anything below `critical` severity; Slack is noisy enough.
