---
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000002
created: 2025-12-01T11:08:53
---
A [[technote]] and [[code snippet]] for ffmpeg.

Trim without re-encoding (fast, keyframe-snapped):
```bash
ffmpeg -ss 00:01:30 -to 00:02:10 -i in.mp4 -c copy out.mp4
```
`-c copy` is the important part — drop it and you're re-encoding the whole clip.

Concat files of the same codec: make `list.txt` with `file 'a.mp4'` lines, then
```bash
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4
```
