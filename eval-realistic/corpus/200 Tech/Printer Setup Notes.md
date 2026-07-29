---
updated: 2026-06-02T11:43:00
id: 01M6V00000000000000000000E
created: 2026-05-02T10:11:00
---
# Printer Setup Notes

Getting an old printer working reliably over the LAN again.

## The Revival
I pulled a HP LaserJet from the basement that hadn't been used in three years. No network drivers existed online for it—too old. Instead of replacing it, I assigned it a static IP on the guest VLAN, configured it via web interface, and tested printing from the laptop. It worked, but only on the first try; subsequent jobs hung. The print queue was full of stalled jobs from god knows when.

## The Fix
I cleared the queue by power-cycling the printer and disabling the old Bonjour configuration. Then I set up the print queue on the laptop to explicitly target the IP address instead of the advertised name. I also reduced the timeout from 30 seconds to 5 seconds so jobs fail fast if the printer is unreachable. Now it's been running reliably for two months. I print maybe twice a month, so it still feels like a win compared to buying a new printer.
