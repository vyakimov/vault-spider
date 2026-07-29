---
id: 01JEV000000000000000000098
title: SSH Key Rotation Policy
aliases: []
type: policy
created: 2024-08-17T09:00:00Z
updated: 2025-02-22T12:00:00Z
tags: [infrastructure, security]
---
# SSH Key Rotation Policy

## Key Lifecycle and Rotation Intervals

All administrative SSH keys used to access infrastructure devices are rotated on a 12-month cycle. Key pairs are generated using RSA-4096 algorithm or EdDSA (preferred for new keys). Legacy DSA and ECDSA keys are phased out and replaced during the rotation cycle.

**Rotation schedule:**
- Personal administrative keys: January 1 each year (synchronized with budget planning cycle)
- Service account keys: April 1 each year (offsets personal schedule to reduce operational load)
- Emergency/break-glass keys: Stored offline; rotated only upon compromise or every 18 months, whichever occurs first

## Key Generation and Secure Storage

New key pairs are generated on an air-gapped laptop running OpenSSH 9.0+ under controlled conditions. Private keys are encrypted with AES-256 passphrases and stored in a password manager accessible only to authorized personnel (currently 2 administrators).

Public keys are deployed to all infrastructure devices (primary office router, remote site switches, NAS server, console access server) via SSH agent automation with full audit logging enabled.

## Revocation and Incident Response

Upon compromise of any private key, the corresponding public key is immediately revoked from all infrastructure devices. Revocation is performed via:
1. Emergency SSH root access to remove the key from authorized_keys files
2. Syslog alert to facility monitoring system
3. Post-incident audit of all access logs for the 30 days preceding discovery
4. Emergency key rotation for all affected accounts

**Revocation timeline target:** <15 minutes from discovery to complete removal

## Access Control and Delegation

[[VPN Client Setup Guide|Tunnel-based remote access]] is the standard method for field staff; SSH key access is limited to infrastructure engineers and authorized operations personnel. No SSH key credentials are distributed to external contractors; temporary access is provisioned via guest VPN accounts with 30-day expiration.

Related security procedures including [[Equipment Rack Layout|physical access restrictions]], [[Lightning Protection Notes|infrastructure integrity]], and [[Remote Access Audit 2025|credential audit procedures]] are coordinated to ensure comprehensive identity management.

## Supporting Documentation

- [[Weatherproof Enclosure Standards|Hardware security baseline requirements]]
- [[Router Firmware Log|Firmware update coordination and audit logging]]

---
**Current rotation cycle:** January 2025 rotation in progress (deadline February 28, 2025)
**Next rotation date:** January 1, 2026
