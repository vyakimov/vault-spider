---
id: 01JEV000000000000000000097
title: DNS Record Change Log
aliases: []
type: log
created: 2025-07-16T09:00:00Z
updated: 2025-01-21T12:00:00Z
tags: [infrastructure, networking]
---
# DNS Record Change Log

## Internal DNS Authority and Record Management

All DNS records for the field station internal domain (atlas.local) are managed by a BIND 9.16 authoritative nameserver running on the facility NAS device (10.60.1.50). Changes to DNS records are logged with timestamp, technician identity, and brief rationale. The zone file is backed up to offsite storage daily.

## Record Change History

| Date | Record Type | FQDN | Change | Technician | Reason |
|------|-------------|------|--------|-----------|--------|
| 2025-06-22 | A | sensor-tower-01.atlas.local | 10.60.1.42 (new) | J.Smith | Installed new sensor node at tower site |
| 2025-05-18 | AAAA | mgmt.atlas.local | Added IPv6 entry 2001:db8::1 | K.Wong | Dual-stack enablement for management console |
| 2025-04-11 | CNAME | ntp-backup.atlas.local | → ntp-primary.atlas.local | J.Smith | Consolidated redundant NTP services |
| 2025-03-03 | A | modem.atlas.local | 10.60.1.3 (updated, was 10.60.1.25) | K.Wong | Cellular modem relocated to new cabinet position |
| 2025-01-28 | TXT | atlas.local | Added "v=spf1 -all" record | J.Smith | Email security hardening (SPF policy) |
| 2024-12-15 | MX | atlas.local | Priority 10 → mail.fieldops.external (new) | K.Wong | Outbound mail routing via external relay |
| 2024-11-02 | A | poe-injector.atlas.local | 10.60.1.45 (new) | J.Smith | PoE injector for remote site power management |

## Split-DNS Configuration

Internal clients resolve atlas.local queries to 10.60.1.1 (BIND server). External clients and public internet queries receive NXDOMAIN responses to prevent information leakage. Clients connected via the site VPN tunnel automatically receive the internal nameserver configuration via DHCP Option 6.

## Cache Invalidation and TTL Tuning

DNS records for frequently changed entries (e.g., temporary DHCP-assigned devices) use short TTL values (300 seconds). Static infrastructure entries use 3,600-second TTL to reduce query load on the authoritative server.

Full zone cache invalidation is performed only after major infrastructure changes (e.g., network segment reconfiguration). Incremental updates via dynamic DNS (TSIG-authenticated) are permitted only for authorized services.

---
**Zone serial:** 2025012101 (January 21, 2025 version)
**Authoritative nameserver:** ns1.atlas.local (10.60.1.1)
