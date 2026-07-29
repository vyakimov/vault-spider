---
updated: 2026-07-19T11:36:00
id: 01M6V000000000000000000057
created: 2026-06-19T10:12:00
---
# Smart Plug Firmware Notes

A record of flashing open-source firmware onto a couple of smart plugs to keep them local-only and prevent cloud phone-home behavior.

## Original Problem
The stock firmware in the plugs connected to a cloud service to verify commands, which meant controlling them required internet and the company could theoretically eavesdrop on usage patterns. I wanted smart plugs for automation but without external dependencies. After researching, I found an open-source firmware that supports the same hardware.

## Flashing Process
The process required opening the plugs and connecting a serial adapter to the flash pins—fiddly but doable with patience. I backed up the stock firmware first just in case. The open-source firmware installed cleanly and the plugs now connect only to the local home automation controller over the tailnet. No cloud dependencies, no manufacturer tracking, full control. The plug also doesn't lose power when the internet is down. I've since flashed a second unit with the same firmware so the automation is redundant.
