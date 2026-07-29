---
updated: 2026-05-27T14:48:00
id: 01M6E000000000000000000035
created: 2026-04-25T09:12:00
---
`defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false` enables key repeat; `defaults write com.apple.dock autohide -bool true` hides dock. `defaults write com.apple.finder ShowHiddenFiles -bool true` shows hidden files. Apply changes: `killall -9 Finder` (or restart app). Backup: `defaults read > defaults_backup.plist` before bulk changes.
