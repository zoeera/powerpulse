import io
import os
import shutil
import subprocess
import tempfile
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
    """Lazy-load RapidOCR only locally when Tesseract is absent."""
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


def _pdf_to_image_bytes(pdf_bytes: bytes) -> Optional[bytes]:
    """Convert page 1 of a PDF bill into PNG bytes using pdftoppm when available."""
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "bill.pdf")
        out_prefix = os.path.join(tmpdir, "page")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        try:
            subprocess.run(
                [pdftoppm, "-png", "-f", "1", "-l", "1", "-r", "150", pdf_path, out_prefix],
                check=True,
                timeout=20,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for fname in sorted(os.listdir(tmpdir)):
                if fname.startswith("page") and fname.endswith(".png"):
                    with open(os.path.join(tmpdir, fname), "rb") as img_f:
                        return img_f.read()
        except Exception as e:
            print(f"[OCR] PDF conversion failed: {e}")
    return None


def _ensure_image_bytes(raw_bytes: bytes) -> Optional[bytes]:
    """Normalize PDFs into image bytes so PIL can open them."""
    if raw_bytes.lstrip().startswith(b"%PDF"):
        return _pdf_to_image_bytes(raw_bytes)
    return raw_bytes


def preprocess_image(image_bytes: bytes) -> Image.Image:
    """Enhance bill image for fast, reliable OCR while bounding size and memory."""
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    if img.mode != "L":
        img = ImageOps.grayscale(img)

    # Upscale only tiny thumbnails; keep Render <= 960px so 0.1 vCPU Tesseract finishes in a few seconds
    max_dim = 960 if _IS_RENDER else 1600
    if img.width < 500:
        scale = 1.6
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.BILINEAR)

    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.BILINEAR)

    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.25)
    return img


def _run_tesseract(img: Image.Image, lang: str = "hin+eng") -> str:
    """Run fast single-pass English Tesseract first; only run hin+eng fallback if needed."""
    if pytesseract is None or not _HAS_TESSERACT:
        return ""

    config = "--oem 1 --psm 6"
    text = ""
    try:
        text = pytesseract.image_to_string(img, lang="eng", config=config, timeout=15) or ""
    except Exception as e:
        print(f"[OCR] Tesseract eng pass error: {e}")

    # Only load Hindi+English if English extraction yielded almost no readable text
    if len(text.strip()) < 45 and lang != "eng":
        try:
            multi_text = pytesseract.image_to_string(img, lang="hin+eng", config=config, timeout=18) or ""
            if len(multi_text.strip()) > len(text.strip()):
                text = multi_text
        except Exception as e:
            print(f"[OCR] Tesseract hin+eng pass note: {e}")

    return text.strip()


def run_ocr(image_bytes: bytes, lang: str = "hin+eng") -> str:
    """Run OCR using fast Tesseract on Render/Docker or RapidOCR locally."""
    normalized_bytes = _ensure_image_bytes(image_bytes)
    if not normalized_bytes:
        return ""

    if _HAS_TESSERACT and _IS_RENDER:
        try:
            img = preprocess_image(normalized_bytes)
            text = _run_tesseract(img, lang=lang)
            if text:
                return text
        except Exception as e:
            print(f"[OCR] Tesseract Error: {e}")

    rapidocr = _get_rapidocr()
    if rapidocr is not None:
        try:
            import numpy as np
            img = Image.open(io.BytesIO(normalized_bytes)).convert("RGB")
            if max(img.size) > 1600:
                img.thumbnail((1600, 1600))
            img_np = np.array(img)
            result, _ = rapidocr(img_np)
            if result:
                lines = [r[1] for r in result if r and len(r) > 1 and r[1]]
                text = "\n".join(lines).strip()
                if text:
                    return text
        except Exception as e:
            print(f"[OCR] RapidOCR execution note: {e}")

    if _HAS_TESSERACT:
        try:
            img = preprocess_image(normalized_bytes)
            return _run_tesseract(img, lang=lang)
        except Exception as e:
            print(f"[OCR] Tesseract Error: {e}")

    return ""
