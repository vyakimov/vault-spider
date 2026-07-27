---
updated: 2026-03-18T11:53:00
id: 01M6V000000000000000000004
created: 2026-02-18T10:01:00
---
# Backup Strategy Overview

The 3-2-1 shape of backups across LordByron, Blackbird, and offline USB disks.

## Current Layout
LordByron (primary storage) has two internal drives: one for active data, one for a local incremental backup. Blackbird (secondary NAS) holds a full copy of everything, updated nightly via rsync. One offline USB disk lives in a drawer and gets rotated in monthly with a fresh snapshot. That's the 3-2-1: three copies (active + LordByron backup + Blackbird), on two media types (spinning + USB), with one offsite (not really offsite, but physically disconnected).

## What Actually Gets Backed Up
User files, configuration, database dumps of anything that has state—everything except installed packages (those are in dotfiles). The full LordByron+Blackbird backup takes about 2.8TB. The monthly USB snapshot is selective: just the stuff that would hurt to lose (photos, financial records, project archives). If LordByron dies, I can spin up Blackbird. If both die, the USB gets me back most of what matters.
