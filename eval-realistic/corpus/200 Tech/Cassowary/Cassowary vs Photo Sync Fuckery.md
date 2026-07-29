---
tags:
  - homelab
  - photos
updated: 2026-05-28T10:35:00
id: 01M6P000000000000000000006
created: 2026-05-26T09:55:00
---
> [!INFO]
> Cassowary's uploader uses a direct TCP socket to the daemon, avoiding the Photos library altogether.

The Photos app on iOS has a TCC (Transparency, Consent, and Control) sandbox that makes direct access to the library a nightmare — apps either get read-only access to a user-selected album or they have to prompt for every photo. Cassowary sidesteps this entirely by letting users pick photos within the app's own picker, then uploading them directly over the tailnet. No Photos library, no TCC prompt, no forwarding through Apple's servers. This also means I can upload photos in custom collections (by date, event, or person) without mirroring the phone's camera roll structure.
