import io
import os
import shutil
from typing import Optional
from PIL import Image, ImageEnhance, ImageOps

try:
    import pytesseract
except ImportError:
    pytesseract = None

_HAS_TESSERACT = bool(pytesseract is not None and shutil.which("tesseract"))
_IS_RENDER = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"))

_rapidocr = None
_rapidocr_checked = False


def _get_rapidocr():
    """Lazy-load RapidOCR only when needed (skipped on low-memory Render free tier when Tesseract is installed)."""
    global _rapidocr, _rapidocr_checked
    if _rapidocr_checked:
        return _rapidocr
    _rapidocr_checked = True

    if _IS_RENDER and _HAS_TESSERACT:
        return None

    try:
        from rapidocr_onnxruntime import RapidOCR
        _rapidocr = RapidOCR()
    except Exception as e:
        _rapidocr = None
        print(f"[OCR] RapidOCR not available: {e}")
    return _rapidocr


def preprocess_image(image_bytes: bytes) -> Image.Image:
    """Enhance bill image for higher OCR character recognition accuracy while keeping memory bounded."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "L":
        img = ImageOps.grayscale(img)

    # Scale small images up for better OCR, cap large photos to stay memory-safe
    if img.width < 800:
        scale = 2.0
    elif img.width < 1200:
        scale = 1.5
    else:
        scale = 1.0

    if scale != 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.BILINEAR)

    if max(img.size) > 2000:
        img.thumbnail((2000, 2000))

    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    return img


def run_ocr(image_bytes: bytes, lang: str = "eng+hin+tel") -> str:
    """Run OCR using Tesseract on Linux/Docker (low RAM) or RapidOCR locally when Tesseract is absent."""
    # On Render/Docker where Tesseract + Hindi/Telugu packs are installed, use Tesseract first to stay well under 512MB RAM
    if _HAS_TESSERACT and _IS_RENDER:
        try:
            img = preprocess_image(image_bytes)
            try:
                text = pytesseract.image_to_string(img, lang=lang)
            except Exception:
                text = pytesseract.image_to_string(img, lang="eng")
            if text and text.strip():
                return text.strip()
        except Exception as e:
            print(f"[OCR] Tesseract Error: {e}")

    # Primary local engine (or fallback): RapidOCR (lazy-loaded)
    rapidocr = _get_rapidocr()
    if rapidocr is not None:
        try:
            import numpy as np
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            if max(img.size) > 2000:
                img.thumbnail((2000, 2000))
            img_np = np.array(img)
            result, _ = rapidocr(img_np)
            if result:
                lines = [r[1] for r in result if r and len(r) > 1 and r[1]]
                text = "\n".join(lines).strip()
                if text:
                    return text
        except Exception as e:
            print(f"[OCR] RapidOCR execution note: {e}")

    # Secondary fallback: Tesseract
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
