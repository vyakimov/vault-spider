---
updated: 2026-04-04T11:37:00
id: 01M6V000000000000000000068
created: 2026-03-04T10:29:00
---
# Vault Backup via Git

Using a private git remote to back up this vault, separate from Obsidian Sync, for version control and off-site redundancy.

## Why Not Just Obsidian Sync
Obsidian Sync is convenient but adds a dependency on Obsidian's servers. I wanted the vault backed up to a location under my control. Git provides version history, which is valuable if I accidentally delete a note or want to review how something was written months ago. Obsidian Sync is more of a sync service than a true backup.

## Implementation
The vault is a git repository with a private remote hosted on a self-managed Bramble instance. I commit new notes and edits once a week—frequent enough to capture progress but not so often that every keystroke is versioned. This provides both backup and audit trail. If a note is accidentally deleted, I can recover it from git history. The commits also document when I worked on which projects based on what was modified. Regular commits keep the repository manageable in size.
