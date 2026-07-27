---
tags:
  - homelab
  - iot
updated: 2026-06-12T10:28:00
id: 01M6M000000000000000000002
created: 2026-02-09T09:56:00
---
## Pairing New Devices

Zigbee2MQTT runs on PuddleJumper with a USB CC2531 coordinator. To pair: permit join for 60 seconds via the web UI, then power-cycle the sensor. It finds the network and joins automatically. Most sensors — temperature, humidity, leak — pair instantly. Door sensors sometimes need a reset (hold the small button for 10 seconds).

The 2.4 GHz WiFi and Zigbee channels overlap. The microwave causes brief dropout during heating — the entire mesh stalls for ~3 seconds. Moving the coordinator antenna to the window helped a bit. I now exclude the microwave from automations and manually verify it's off before trusting sensor data during meal prep.

Pairing log is noisy; old failed attempts clutter the debug output. I've considered running a cleanup script to prune the database.
