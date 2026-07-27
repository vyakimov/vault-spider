---
id: 01JEV000000000000000000103
title: Firewall Rule Change Log
aliases: []
type: log
created: 2025-04-22T09:00:00Z
updated: 2025-07-01T12:00:00Z
tags: [infrastructure, security]
---
# Firewall Rule Change Log

## Firewall Architecture and Rule Policy

The Juniper MX204 border router implements stateful packet filtering and connection-based access control. Firewall rules are applied bidirectionally at the WAN interface (primary fiber) and at the point-to-point radio link to the secondary site. All rules follow a default-deny posture: traffic is blocked unless explicitly permitted.

**Rule categories:**
- **Critical infrastructure**: Management console access, NTP, DNS, emergency backup systems
- **Data collection**: Sensor data ingest, telemetry exports, monitoring heartbeat traffic
- **Administrative**: SSH key-based login, SNMP monitoring, syslog forwarding
- **Temporary**: Vendor support access, contractor bandwidth allocations (always time-bounded)

## Recent Rule Modifications

| Date | Change | Direction | Ports | Protocol | Technician | Reason |
|------|--------|-----------|-------|----------|-----------|--------|
| 2025-06-14 | Added | Inbound | 8443 | TCP | J.Smith | Temporary diagnostics console for a visiting research team (30-day expiration) |
| 2025-05-22 | Removed | Inbound | 12345 | TCP | K.Wong | Legacy sensor interface decommissioned; old device replaced |
| 2025-04-29 | Modified | Inbound | 443 | TCP | J.Smith | Increased rate limit from 100 pps to 200 pps during sensor upgrade window |
| 2025-03-15 | Added | Outbound | 53 | UDP | K.Wong | Secondary DNS server pool added (Quad9 DNS service) |
| 2025-02-28 | Removed | Inbound | 22 | TCP | J.Smith | Emergency SSH access for vendor support; support case closed and port closed |

## Rule Audit and Expiration Tracking

All temporary firewall rules include automatic expiration timestamps. Expiration checks are performed on the 1st and 15th of each month; expired rules are logged as "to be reviewed" and remain in place only if explicitly renewed by an authorized administrator within 7 days.

Documentation requirements:
- **Justification**: Every rule must reference a change ticket or written authorization
- **Owner**: Clear assignment of responsibility for rule maintenance
- **Expiration policy**: Permanent rules explicitly marked "no expiration"; temporary rules must include a target end date

## Incident Response and Emergency Rules

During security incidents or operational emergencies, temporary rules can be activated by authorized personnel (currently 2 infrastructure engineers) without full change control process. Emergency rules must be documented within 24 hours and reviewed for necessity at the next scheduled change window.

## Related Security Procedures

Access to firewall rule configuration is limited to authorized administrators. Changes are monitored via [[VPN Client Setup Guide|audit logging]] and correlated with user SSH key access logs to ensure complete traceability.

---
**Active rule count:** 47 permanent rules, 1 temporary rule (expires 2025-07-14)
**Last audit:** 2025-07-01
