---
tags:
  - homelab
  - iot
updated: 2026-03-14T10:50:00
id: 01M6M000000000000000000004
created: 2026-04-11T09:10:00
---
The porch camera is a Wyze v3, flashed with open-source RTSP firmware to kill the cloud dependency. It streams to a local NVR appliance (generic Ubuntu box with ffmpeg and a 2TB drive). Recording is 24/7 at 1080p, about 200 GB per month. No cloud backup; I manually export footage if there's an incident to investigate. The NVR keeps 3 months of rolling history, then deletes old segments. Motion detection runs locally via ffmpeg filters (background-subtraction), not cloud-side. The camera POE-powered, so no batteries to babysit. No integration with Home Assistant automations yet — alerts would need to run a separate detection service, which I haven't prioritized.
