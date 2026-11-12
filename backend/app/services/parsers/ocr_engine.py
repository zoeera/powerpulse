import io
import re
import os
import hashlib
from typing import Optional, Tuple
from PIL import Image, ImageEnhance, ImageOps

try:
    from rapidocr_onnxruntime import RapidOCR
    import numpy as np
    _rapidocr = RapidOCR()
except Exception as e:
    _rapidocr = None
    print(f"[OCR] RapidOCR not available: {e}")

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from indic_transliteration.sanscript import transliterate as _sanscript
except ImportError:
    _sanscript = None

def preprocess_image(image_bytes: bytes) -> Image.Image:
    """Enhance bill image for higher OCR character recognition accuracy."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "L":
        img = ImageOps.grayscale(img)
    
    # Scale small images up for better OCR
    if img.width < 800:
        scale = 2.0
    elif img.width < 1200:
        scale = 1.5
    else:
        scale = 1.0
        
    if scale != 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.BILINEAR)
        
    if max(img.size) > 3200:
        img.thumbnail((3200, 3200))
        
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    return img

def run_ocr(image_bytes: bytes, lang: str = "eng+hin+tel") -> str:
    """Run OCR with RapidOCR (primary ONNX engine) or Tesseract fallback."""
    # 1. Primary: RapidOCR (high accuracy ONNX runtime)
    if _rapidocr is not None:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_np = np.array(img)
            result, _ = _rapidocr(img_np)
            if result:
                lines = [r[1] for r in result if r and len(r) > 1 and r[1]]
                text = "\n".join(lines).strip()
                if text:
                    return text
        except Exception as e:
            print(f"[OCR] RapidOCR execution note: {e}")

    # 2. Secondary: Tesseract
    if pytesseract is not None:
        try:
            img = preprocess_image(image_bytes)
            try:
                text = pytesseract.image_to_string(img, lang=lang)
            except Exception:
                text = pytesseract.image_to_string(img, lang="eng")
            return text
        except Exception as e:
            print(f"[OCR] Tesseract Error: {e}")

    return ""

