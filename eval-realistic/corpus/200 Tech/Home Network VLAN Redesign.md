---
updated: 2026-07-15T11:20:00
id: 01M6V000000000000000000001
created: 2026-06-15T10:40:00
---
# Home Network VLAN Redesign

Isolating IoT devices after a discount security camera started making unexpected outbound connections.

## What Triggered the Change
I noticed the camera was phoning home to a Chinese server every few seconds via DNS lookups. I could block the domain, but that defeated the point of owning the camera. Instead, I threw it onto a separate VLAN with limited routing rules. The main laptop, headscale controller, and storage boxes stay on the trusted network. Guest devices get a third VLAN with internet-only access.

## New Setup
Three VLANs on the managed switch now: trusted (10 devices), guest (ad-hoc), and isolated IoT (camera, smart plug, temperature sensor). The router logs traffic between VLANs so I can audit what's trying to talk to what. It's not Fort Knox, but it means a compromised lightbulb can't snoop on my backups or SSH into a NAS.
