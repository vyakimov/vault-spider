---
updated: 2026-04-22T19:13:00
id: 01M6E000000000000000000160
created: 2026-03-20T14:17:00
---
`ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3` extracts highest-quality audio. `-q:a 0` selects codec default (no re-encoding loss); use `-codec:a libmp3lame -b:a 192k` to force bitrate.
