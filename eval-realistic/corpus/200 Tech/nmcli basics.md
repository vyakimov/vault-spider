---
updated: 2026-06-25T14:58:00
id: 01M6E000000000000000000085
created: 2026-05-23T11:02:00
---
`nmcli connection show` — list all connections; `nmcli device wifi list` to scan. Create WiFi: `nmcli connection add type wifi ifname wlan0 con-name mynet ssid MySSID`. Use `nmcli connection up mynet` to activate.
