---
updated: 2026-06-02T08:58:44
id: 01M6D000000000000000000002
created: 2026-03-02T13:40:10
---
A [[papertrail]] note. See also [[Deskewing Scans]]


## **Tesseract** (the incumbent)

**Pros:**

- Tiny, fast, packaged everywhere
- Excellent on clean 300dpi flatbed scans
- Simple CLI, no model management

**Cons:**

- Falls apart on photographed pages: skew, shadows, curved text
- Layout analysis is basic

## **PaddleOCR**

**Pros:**

- Much better on skewed/photographed documents
- Detection + recognition + angle classification in one pipeline

**Cons:**

- Heavy: the server models are **around 2GB** and want a GPU
- Python dependency sprawl

## **The rule I settled on:**

Flatbed scans from the printer go straight to Tesseract. Anything shot with a phone goes through
[[Deskewing Scans]] and then PaddleOCR. Don't run Paddle on the whole backlog — the electricity
isn't worth it for clean pages.
