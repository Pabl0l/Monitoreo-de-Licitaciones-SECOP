"""Extraccion de texto de documentos.

Flujo:
1. PDF -> intenta texto embebido con PyMuPDF (rapido, sin OCR).
2. Si una pagina tiene poco texto (escaneada) -> OCR de esa pagina.
3. DOCX/XLSX -> extraccion directa (sin OCR).

OCR: PaddleOCR preferido, Tesseract fallback. Imports perezosos (pesados).
"""
import io

from config import OCR_ENGINE, OCR_LANG, OCR_MIN_CHARS_PER_PAGE
from utils.logging_conf import get_logger

log = get_logger(__name__)

# Singletons de motores OCR (cargar una vez; clave en 8GB RAM).
_paddle = None
_paddle_failed = False


def _get_paddle():
    global _paddle, _paddle_failed
    if _paddle is None and not _paddle_failed:
        try:
            from paddleocr import PaddleOCR

            _paddle = PaddleOCR(use_angle_cls=True, lang=OCR_LANG, show_log=False)
        except Exception as exc:  # noqa: BLE001
            log.warning("PaddleOCR no disponible: %s", exc)
            _paddle_failed = True
    return _paddle


def _ocr_image_bytes(img_bytes: bytes) -> str:
    """OCR sobre una imagen (bytes PNG). Paddle -> Tesseract."""
    if OCR_ENGINE == "paddle":
        engine = _get_paddle()
        if engine is not None:
            try:
                import numpy as np
                from PIL import Image

                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                result = engine.ocr(np.array(img), cls=True)
                lines = []
                for block in result or []:
                    for line in block or []:
                        lines.append(line[1][0])
                return "\n".join(lines)
            except Exception as exc:  # noqa: BLE001
                log.warning("paddle ocr fallo, uso tesseract: %s", exc)
    # Fallback: Tesseract
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(img_bytes))
        return pytesseract.image_to_string(img, lang="spa")
    except Exception as exc:  # noqa: BLE001
        log.warning("tesseract ocr fallo: %s", exc)
        return ""


def extract_pdf(path: str) -> tuple[str, bool]:
    """Devuelve (texto, ocr_usado)."""
    import fitz  # pymupdf

    partes: list[str] = []
    ocr_usado = False
    with fitz.open(path) as doc:
        for page in doc:
            txt = page.get_text("text")
            if len(txt.strip()) >= OCR_MIN_CHARS_PER_PAGE:
                partes.append(txt)
            else:
                # Pagina probablemente escaneada -> render a imagen + OCR.
                pix = page.get_pixmap(dpi=200)
                ocr_txt = _ocr_image_bytes(pix.tobytes("png"))
                if ocr_txt.strip():
                    ocr_usado = True
                    partes.append(ocr_txt)
    return "\n".join(partes), ocr_usado


def extract_docx(path: str) -> str:
    try:
        from docx import Document  # python-docx (opcional)

        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as exc:  # noqa: BLE001
        log.warning("docx extract fallo: %s", exc)
        return ""


def extract_text(path: str, mime: str | None) -> tuple[str, bool]:
    """Dispatch por tipo. Devuelve (texto, ocr_usado)."""
    p = path.lower()
    try:
        if p.endswith(".pdf") or (mime and "pdf" in mime):
            return extract_pdf(path)
        if p.endswith((".docx", ".doc")):
            return extract_docx(path), False
    except Exception as exc:  # noqa: BLE001
        log.warning("extract_text fallo path=%s err=%s", path, exc)
    return "", False
