---
id: 01JEV000000000000000000141
title: Atlas SSL Certificate Renewal
type: procedure
created: 2024-06-15T09:00:00Z
updated: 2025-09-20T12:00:00Z
tags: [atlas, operations]
---
# Atlas SSL Certificate Renewal

## Certificate Details

The Atlas dashboard uses a single wildcard TLS certificate for HTTPS connections.

- **Domain:** *.atlas-monitoring.internal
- **Issuer:** Let's Encrypt (free, 90-day validity)
- **Current Expiry:** October 12, 2025
- **Renewal Date:** September 12, 2025 (30 days before expiry; automatic via certbot)

## Automatic Renewal Process

Let's Encrypt certificates are auto-renewed by a weekly cron job (`/etc/cron.d/certbot-renewal`) that:
1. Checks certificate expiry status
2. Initiates renewal 30 days prior to expiry
3. Validates domain ownership via DNS ACME challenge
4. Reloads the dashboard application to use the new certificate

No manual intervention is required for routine renewals.

## Manual Renewal (If Automatic Fails)

If automatic renewal fails (check `/var/log/certbot.log`):

1. SSH to the dashboard server
2. Run: `certbot renew --force-renewal`
3. Verify successful renewal: `certbot certificates`
4. Manually reload the dashboard if the application does not restart automatically
5. Test HTTPS connection: `curl -I https://atlas-monitoring.internal`

## Expiry Alerts

Alerts are sent to operations@atlas-monitoring if the certificate is within 7 days of expiry. These are low-priority reminders; if automatic renewal succeeded, the certificate will already be updated.

Certificate chains and private keys are stored in `/etc/letsencrypt/live/atlas-monitoring.internal/` with read permissions restricted to the dashboard process user.

## Related Documentation

See the dashboard deployment configuration in `/opt/atlas/config/nginx.conf` for certificate path references.
