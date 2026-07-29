---
id: 01JEV000000000000000000104
title: Remote Access Audit 2025
aliases: []
type: review
created: 2024-05-23T09:00:00Z
updated: 2025-08-02T12:00:00Z
tags: [infrastructure, security]
---
# Remote Access Audit 2025

## Annual Security Review Scope

This review assesses who holds active credentials for remote access to field-office infrastructure and validates that access privileges match current role assignments. The audit covers SSH keys, VPN tunnel credentials, SNMP community strings, and console port passwords across all critical systems.

## Access Credential Summary

**Active administrative SSH key holders:**
- J.Smith (Infrastructure Engineer, primary): RSA key 0x4a8b91c2, activated 2024-01-05
- K.Wong (Infrastructure Engineer, secondary): EdDSA key 0x7c3a4f88, activated 2024-01-12

Both engineers maintain individual SSH key pairs with passphrases stored in the facility password manager (encrypted 256-bit AES).

**VPN tunnel access:**
- 6 active VPN accounts for remote monitoring operations
- 1 reserved guest account (currently unassigned)
- All credentials rotated within the last 12 months per [[SSH Key Rotation Policy]]

**SNMP monitoring access:**
- Read-only community string deployed to 8 network devices
- No write-access community strings in use (configuration changes require direct console access)
- Community strings renewed annually; last rotation performed 2025-01-15

## Access Privilege Alignment and Segregation

All personnel with infrastructure access have documented need-to-know justification. No access credentials are shared between individuals or services. The facility maintains separate role-based accounts:

- **Tier-1 (Full administrative)**: 2 infrastructure engineers
- **Tier-2 (Monitoring-only)**: 4 research operations staff (VPN access, read-only)
- **Tier-3 (Guest/vendor)**: Temporary allocations for vendor support (expires 30 days)

No external contractors currently hold active credentials. The last contractor access (vendor security audit, March 2025) was terminated upon completion.

## Security Incident Status

No unauthorized access attempts, credential compromise, or security incidents related to remote access infrastructure have occurred in the 2024–2025 review period.

Audit log review found:
- 347 successful SSH sessions (all from known administrative devices)
- 12 failed SSH login attempts (all blocked by SSH key validation)
- 0 unauthorized VPN connection attempts

## Physical Access and Console Security

Physical access to equipment cabinets is restricted to infrastructure engineers and on-site maintenance personnel. Console port access is protected via password authentication (separate credentials from SSH keys); the console server rotates logs daily and retains 90 days of history.

Related procedural controls including [[Lightning Protection Notes|hardware safety]] and [[DNS and Hostnames|network identity management]] are validated as part of this annual review.

---
**Audit date:** 2025-08-02
**Next scheduled review:** 2026-08-01
**Compliance status:** Fully compliant with facility security policy
