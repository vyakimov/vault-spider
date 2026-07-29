---
updated: 2026-01-23T11:48:00
id: 01M6V000000000000000000009
created: 2026-07-23T10:36:00
---
# Dotfiles Repo Structure

How dotfiles are organized and symlinked across two machines.

## Layout
The repo has a `bash/`, `vim/`, `ssh/`, and `git/` folder. Each contains config files that get symlinked into `~` on boot. A setup script checks which machine I'm on and only symlinks what applies—the laptop gets a different SSH config than the desktop. Secrets (API keys for git hooks, SSH key paths) live in environment variables, not in the repo.

## Two-Machine Split
The desktop and laptop share most dotfiles but differ in terminal emulator, font size, and workspace layout preferences. I use a machine-specific `~/.bashrc.local` that gets sourced at the end of the shared bashrc. That way, 90% of my shell setup is identical, but the last 10% (idle-check timeout, workspace commands) is per-machine. The dotfiles repo is public—it contains no secrets, just environment and tool setup.
