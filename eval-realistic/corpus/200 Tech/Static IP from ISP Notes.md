---
updated: 2026-02-12T11:33:00
id: 01M6V00000000000000000000R
created: 2026-01-12T10:21:00
---
# Static IP from ISP Notes

Notes from asking the ISP about a static IP versus using the tailnet instead.

## The Question
I called to ask about getting a static IP for running services from home. The ISP offered one for $5/month extra, but mentioned that most home users don't actually need it anymore. They suggested IPv6 (which I'd have automatically) or a VPN. That conversation made me reconsider the whole approach.

## Why Tailnet Won
I already have a headscale controller set up, so getting a static IP felt redundant. Anyone accessing my home services already goes through the tailnet (encrypted, behind my NAT, no port forwarding). Adding a static IP would mean opening ports to the public internet just to save the trouble of VPN setup. The ISP was right: it's not 2005 anymore. I declined the static IP and documented this decision so I don't second-guess it next year.
