---
updated: 2026-03-25T11:10:00
id: 01M6V00000000000000000000B
created: 2026-02-25T10:50:00
---
# Second Monitor Calibration

Color-matching a secondary monitor to the laptop's built-in display.

## The Problem
I added an external monitor to the desk setup, but the colors looked slightly warmer and the blacks seemed grayer compared to the laptop screen. It made photo editing impossible. I grabbed a calibration tool (a simple sensor that measures actual color output) and ran through the primary display's color profile.

## The Fix
After profiling, I created a separate color profile for the external monitor in the OS settings. Brightness got bumped to match, color temperature was adjusted down by 200K, and gamma was tweaked slightly. Now they look nearly identical—close enough that I can't tell the difference at arm's length. The calibration file lives in git-tracked dotfiles so the setup carries over if I rebuild the desktop. It needs recalibration maybe every 6 months as the external monitor drifts slightly.
