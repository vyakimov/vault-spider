---
id: 01JEV000000000000000000092
title: VPN Client Setup Guide
aliases: []
type: guide
created: 2024-02-11T09:00:00Z
updated: 2025-05-16T12:00:00Z
tags: [infrastructure, networking]
---
# VPN Client Setup Guide

## Prerequisites and System Requirements

Before configuring a new laptop or field device for remote access to station infrastructure, ensure the following prerequisites are met:

- Hardware: x86-64 processor with virtualization support (Intel VT-x or AMD-V), 2+ GB RAM, 500 MB free disk space
- OS support: Windows 10/11, macOS 10.14+, Ubuntu 20.04 LTS or later
- Network connectivity: Any IPv4 or IPv6 internet connection (dual-stack preferred)
- Firewall rule: the client software's outbound UDP port must not be blocked by local network policy (see the client's own documentation for its default port)

Software prerequisites:
- Client VPN software package (version 1.0.21 or later, distributed via facility secure dropbox)
- Optional: DNS override tool for split-DNS configuration

## Configuration Procedure

### Step 1: Generate or Obtain Client Credentials

Contact the infrastructure administrator to request new tunnel credentials. A unique cryptographic key pair and client subnet assignment will be generated and delivered via out-of-band secure channel (encrypted USB drive or secured email). Credentials are valid for 12 months from issuance; renewal follows the facility [[SSH Key Rotation Policy]].

### Step 2: Install and Configure Client Software

Extract the client package and run the installer for your operating system. During installation, specify:
- Client identity: your user name or device hostname
- Default route handling: select "split routing" to maintain local network access while connected
- DNS mode: enable split-DNS to avoid leaking queries to external resolvers

### Step 3: Activate and Verify Connectivity

Execute the client software and load your credentials file (*.conf format). The connection should establish within 5–10 seconds. Verify connectivity by:
```
ping -c 4 10.60.1.2  # Management interface of primary switch
nslookup mgmt-sw-primary.local  # Should resolve to 10.60.1.2
```

If resolution fails, check that the split-DNS configuration is active and the facility's authoritative nameserver is reachable.

### Step 4: Network Access and Best Practices

Once connected, you have read-only access to the facility inventory, monitoring dashboards, and remote device consoles. Do not attempt to modify configuration on any infrastructure device without explicit authorization and documented change ticket approval.

**Access restrictions:**
- No bandwidth-intensive transfers without prior coordination
- Session idle timeout: 120 minutes (disconnect and reconnect if longer operation needed)
- Simultaneous session limit: one active connection per user identity

## Troubleshooting and Support

If the connection fails to establish within 30 seconds, check the client log file (typically `~/.config/vpnclient.log`) for error messages. Common issues include:

- **"No route to host"**: Local firewall is blocking the client's outbound UDP port; check policy or contact network administrator
- **"Connection timeout"**: Facility gateway may be temporarily unavailable; retry after 5 minutes
- **"Authentication failed"**: Credentials file is corrupted or expired; obtain a new credential set from infrastructure admin

---
**Support contact:** infra-ops@fieldstation.local
