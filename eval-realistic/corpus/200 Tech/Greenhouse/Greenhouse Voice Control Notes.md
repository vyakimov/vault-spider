---
updated: 2026-05-04T11:33:00
id: 01M6M000000000000000000009
created: 2026-04-04T10:21:00
---
# Greenhouse Voice Control Notes

I evaluated running a local voice assistant (Mycroft) against my existing Home Assistant automations to see if voice commands would actually replace the app or just add friction.

## Test Setup
I set up Mycroft on a Raspberry Pi on the tailnet and exposed it to 3 common commands: turn lights on/off, check the thermostat, and toggle the guest wifi. I used it for a week to see if the voice path was faster than opening the HA app.

## Results
Voice commands saved maybe 5 seconds over the app 60% of the time, but required more setup (wake word tuning, network latency). I decided not to ship this—the app is already fast enough. The voice commands felt gimmicky for a home with just one occupant.
