---
updated: 2026-05-03T11:40:00
id: 01M6V000000000000000000041
created: 2026-04-03T10:20:00
---
# Second Tailnet Client Notes

Notes on adding a work laptop to the tailnet with a restricted ACL tag to prevent it from reaching home machines.

## Enrollment and ACL Setup
I generated an auth key with the `work-device` tag, gave it a 24-hour expiry, and paired it with the work machine. Once enrolled, I created an ACL rule that permits the work laptop to reach only the Bramble exit node and a shared docs server. The work device cannot initiate connections to anything else on the tailnet—this keeps stray background processes from accidentally tunneling corporate traffic through home machines.

## Testing the Isolation
I verified the firewall rules by attempting SSH to the main NAS and getting a timeout as expected. DNS queries to internal services return answers but subsequent connection attempts are blocked. Reverse isolation works too—the work laptop is unreachable from other tailnet machines, so home automation can't accidentally discover it. This setup lets me use the tailnet's convenience without blurring work and personal network boundaries.
