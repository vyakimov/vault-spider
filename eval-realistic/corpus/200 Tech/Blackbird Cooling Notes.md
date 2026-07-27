---
updated: 2026-05-18T11:07:00
id: 01M6Q000000000000000000006
created: 2026-04-18T10:59:00
---
# Blackbird Cooling Notes

Added a case fan after Blackbird (one of my NAS units) ran hotter than expected during a resilver operation.

## Problem
During a disk resilver, the drive bay temperatures hit 48°C, which is approaching the throttle threshold. The case only had intake air from the PSU, so hot air was pooling around the drives. The resilver was taking longer than expected because thermal throttling was kicking in.

## Solution
I added a 140mm exhaust fan to the rear of the case. Post-installation, peak temperatures during resilver dropped to 38°C and resilver times returned to normal (4 hours vs 5.5 hours previously). The added noise is minimal since the fan idles at low RPM most of the time.
