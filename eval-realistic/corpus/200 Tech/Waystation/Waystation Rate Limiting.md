---
updated: 2026-05-25T11:24:00
id: 01M6R000000000000000000005
created: 2026-04-25T10:48:00
---
# Waystation Rate Limiting

Adding basic rate limiting after a crawler hammered the redirect endpoint.

## Problem
A bot started scanning the Waystation domain and hammering `/go/<code>` endpoints with sequential codes. This created a flood of fake click events and wasted bandwidth.

## Solution
I added a simple rate limiter: per IP, 50 requests per minute to redirect endpoints. Limit exceeded returns 429 Too Many Requests. I also added jitter (1-5 second delays) to the IP counter to prevent precisely-timed bursts from bypassing the limit. Crawlers are blocked, real users never notice.
