---
tags:
  - homelab
  - photos
updated: 2026-01-27T10:13:00
id: 01M6P000000000000000000004
created: 2026-03-24T09:41:00
---
The mobile app queues uploads over the tailnet when photos are taken but batches them to reduce wakeups. Battery complaints stopped after I switched from immediate upload to a 30-second-debounce window — enough time for a burst of photos, but the daemon only spins up the NAS connection once per batch. The app also stops draining battery during video playback now that I moved H.264 decode to a GPU thread pool instead of letting the main thread spin.
