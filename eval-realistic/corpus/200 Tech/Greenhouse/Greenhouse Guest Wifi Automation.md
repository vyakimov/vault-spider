---
updated: 2026-07-06T11:55:00
id: 01M6M00000000000000000000B
created: 2026-06-06T10:35:00
---
# Greenhouse Guest Wifi Automation

I built an automation in Home Assistant that only arms the security cameras when the guest wifi has zero active clients. Keeps me from recording guests while they're here without having to remember to disarm manually.

## Logic
Every 5 minutes, the automation checks the active client count on the guest SSID. If it's zero for 10 minutes, arm all camera automations. If a client connects, disarm immediately and wait 20 minutes after the last disconnect before re-arming.

## Integration
This hooks into the Unifi controller API via a custom integration. I tested it with simulated client connections and confirmed there's no false-positive arming during brief network flickers. The 20-minute grace period prevents thrashing if someone dips in and out of the house.
