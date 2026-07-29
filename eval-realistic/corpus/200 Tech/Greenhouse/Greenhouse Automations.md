---
tags:
  - homelab
  - iot
updated: 2026-01-13T10:39:00
id: 01M6M000000000000000000003
created: 2026-03-10T09:03:00
---
## Active Automations

I've spent way less time on automations than I expected. Three are actually running:

1. **Porch Light** — turns on at sunset, off at midnight. Overridden by manual switch (motion-triggered variant in the backlog).
2. **Leak Sensor Alert** — when the basement moisture sensor exceeds 65% humidity for 2+ minutes, send a Slack notification. Tuned threshold after the shower incident (see [[Leak Sensor False Alarm]]).
3. **Morning Blinds** — at 7am on weekdays, raise the upstairs blinds. Uses a schedule trigger, not a sensor.

Planned but dormant: motion-triggered porch light (added motion sensor, but the automation logic seemed over-engineered), temperature-based HVAC override, and a "bedtime" scene. I've realized that automations I don't use clutter the config, so I delete rather than leave them commented out.
