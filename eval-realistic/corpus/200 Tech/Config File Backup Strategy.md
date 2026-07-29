---
updated: 2026-04-16T11:03:00
id: 01M6V000000000000000000054
created: 2026-03-16T10:51:00
---
# Config File Backup Strategy

An approach to backing up dotfiles and application configurations separately from personal data, keeping system state recoverable without mixing.

## Dotfiles Repository
I maintain a private git repository of dotfiles, ssh keys, and application configs. It lives on Bramble and gets pulled to new machines during setup. This repo is much smaller than the full data backup and changes frequently—git makes tracking changes easy. If I modify the nginx config or update my shell profile, it gets committed immediately. This serves as both backup and version control for my system state.

## Personal Data Backups
The big encrypted backups to LordByron and the offsite disks contain user files, photos, and documents—the data that's irreplaceable. They don't include the configs repo since that's tracked in git. If a machine fails, I can restore the OS, pull the latest configs from git, and be up and running quickly. This separation means my config changes aren't buried in months of incremental backups, making it easier to audit or rollback a bad configuration change.
