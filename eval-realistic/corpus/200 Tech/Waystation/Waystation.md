---
updated: 2026-01-21T11:40:00
id: 01M6R000000000000000000001
created: 2026-07-21T10:20:00
---
# Waystation

Hub note for Waystation, a personal link-shortener and click-tracker I built to consolidate shared links.

## Architecture
Waystation is a simple web service that maps short codes to target URLs and logs clicks. I run it on Bramble behind Caddy. The short domain is `go.youyesyou.me` for internal links and projects. Every click gets logged with timestamp, referrer, and user agent so I can see which links are actually used.

## Use Cases
I use Waystation to shorten long documentation URLs, track which team members open shared resources, and generate QR codes for printed materials. The analytics are minimal but sufficient for my needs.
