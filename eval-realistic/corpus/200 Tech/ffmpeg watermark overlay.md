---
updated: 2026-06-24T11:47:00
id: 01M6E000000000000000000162
created: 2026-05-22T16:43:00
---
`ffmpeg -i input.mp4 -i logo.png -filter_complex "[0][1] overlay=10:10" output.mp4` overlays PNG at (10,10) offset. Use `overlay=W-w-10:H-h-10` for bottom-right; `-c:v libx264` for re-encode or `-c:v copy` if compatible.
