---
updated: 2026-04-23T12:24:00
id: 01M6E000000000000000000083
created: 2026-03-21T09:36:00
---
Create `/etc/udev/rules.d/99-custom.rules`: `SUBSYSTEM=="usb", ATTRS{idVendor}=="1234", SYMLINK+="mydevice"`. Reload with `udevadm control --reload`. Test matches via `udevadm test <devpath>`.
