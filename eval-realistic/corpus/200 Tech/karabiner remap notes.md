---
updated: 2026-03-25T12:14:00
id: 01M6E000000000000000000033
created: 2026-02-23T19:46:00
---
Edit `~/.config/karabiner/karabiner.json` to remap keys. Example: `"from": {"key_code": "caps_lock"}` → `"to": {"key_code": "left_control"}` remaps Caps Lock to Ctrl. Use `"conditions"` for app-specific rules. Reload with Karabiner app or `launchctl load ~/Library/LaunchAgents/org.pqrs.Karabiner-Elements.karabiner_console_user_server.plist`. Complex rules → use web UI for easier editing.
