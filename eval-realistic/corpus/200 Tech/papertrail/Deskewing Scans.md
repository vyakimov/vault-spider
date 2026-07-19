---
updated: 2026-06-02T08:58:44
id: 01M6D000000000000000000004
created: 2026-03-04T09:55:21
---

A [[papertrail]] [[technote]] on straightening photographed pages before OCR.

The cheap version that works: threshold, find the text mass, take the angle of the minimum-area
rectangle around it (cv2.mineAreaRect), rotate by the negative of that angle.

```python
import cv2
import numpy as np

def deskew(gray):
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)
```

Good enough for ±15°. Beyond that, the angle classifier inside PaddleOCR does better — see
[[Tesseract vs PaddleOCR]].
