---
tags:
  - homelab
  - incident
updated: 2026-05-15T10:01:00
id: 01M6M000000000000000000005
created: 2026-05-12T09:17:00
---
The basement humidity sensor fired a "leak detected" alert at 3am one night after someone took a long shower upstairs. The sensor ceiling-mounted near old plumbing, so I set the threshold to 60% as a safety margin against false positives. One shower spiked it to 65% for about 4 minutes. Now the automation requires sustained elevation (>65% for 2+ minutes) before alerting, plus I added a manual bypass in Home Assistant so I can suppress alerts before planned maintenance. The actual leak-detection job is harder than I thought — humidity can spike from normal activities. I've considered adding a second sensor in a dry closet as a "control" to filter out whole-house moisture events, but haven't built that yet.
