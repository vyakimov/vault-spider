---
updated: 2026-03-21T18:56:00
id: 01M6E000000000000000000159
created: 2026-02-19T13:04:00
---
Create concat.txt: `file 'clip1.mp4'` / `file 'clip2.mp4'`. Run `ffmpeg -f concat -safe 0 -i concat.txt -c copy output.mp4`. Copy codec avoids re-encoding; audio/video must have matching properties or demux separately.
