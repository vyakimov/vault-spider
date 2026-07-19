---
updated: 2026-06-02T08:44:03
id: 01M6A000000000000000000005
created: 2026-05-11T21:48:37
---
⏺ Summary: launchd jobs can't read the Photos library on macOS

> [!SUMMARY] TL;DR
> **The nightly backup job can't read `~/Pictures/Photos Library.photoslibrary`** when run from
> launchd, even though the exact same rsync works from an interactive terminal. macOS TCC:
> reading the Photos library needs **Full Disk Access**, which the terminal has and the
> launchd-spawned `rsync` does not. Affects the [[PuddleJumper]] backup pipeline.

In the context of [[Marionette]] scheduled jobs:

  The problem

  The nightly `net.marionette.photobackup` job exits 23 with "Operation not permitted" on every
  file inside the Photos library. Running the identical command in a terminal works.

  What works from launchd

  - rsync of ~/Documents — works
  - rsync of ~/Pictures/*.jpg loose files — works
  - Reading the Photos library from an interactive terminal — works

  What doesn't work from launchd

  - Anything inside Photos Library.photoslibrary — "Operation not permitted"
  - Tested with a bare `cat` on one asset file, same result

  Root cause

  macOS TCC. The Photos library is privacy-protected; a process needs Full Disk Access (or the
  Photos entitlement) to read it. Terminal.app has FDA on this machine, so interactive runs
  inherit it. launchd-spawned processes get nothing implicitly, and `rsync` has no bundle ID to
  grant it to through the UI.

  What we've ruled out

  - File permissions/ownership — identical either way
  - APFS snapshots interfering — no; reading the live library fails the same way
  - SIP weirdness — csrutil reports the default configuration

  Remaining options

  1. Grant FDA to the exact binary launchd runs (wrap rsync in a signed helper app)
  2. Export photos to a plain folder first via osxphotos, back that up instead
  3. Back up the whole user folder from the [[LordByron]] side over SMB, where the NAS user
     already has the right scope
