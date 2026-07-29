---
updated: 2026-01-06T11:13:00
id: 01M6V000000000000000000044
created: 2026-07-06T10:41:00
---
# Server Rack Fan Curve Notes

Tuning the server rack's intake and exhaust fan curves to keep drive temperatures down without the noise becoming a distraction.

## Initial Issues
The drives on LordByron were idling at 42°C under the factory fan curve, which felt too warm for long-term reliability. Pushing the fans to max brought it down to 28°C but made the rack sound like a small jet engine. The goal was finding a balance—acceptable noise at a reasonable operating temperature.

## New Curve Configuration
I set a stepped curve: fans at 30% speed for temps below 35°C, ramping to 50% between 35–42°C, and 70% above 42°C. During normal workload the drives sit around 38°C with minimal fan noise. During backups when the drives are under sustained load, temps climb to 44°C and the fans ramp up, but it's brief enough that neighbors don't complain. I monitor drive SMART data weekly to make sure temps are not causing premature wear.
