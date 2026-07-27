---
updated: 2026-05-23T10:30:00
id: 01M6E000000000000000000161
created: 2026-04-21T15:30:00
---
`ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" -f image2 output.gif` converts 30s clip to GIF at 10 fps. Reduce scale or fps for smaller file; GIF palette is limited, so preview on actual device.
