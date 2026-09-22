"""Descarga PDFs/documentos y registra la ruta local en la base de datos."""
import hashlib
import mimetypes
import re
from pathlib import Path

import requests

from config import DOCS_DIR, DOWNLOAD_TIMEOUT, USER_AGENT
from db import repository as repo
from utils.logging_conf import get_logger

log = get_logger(__name__)


def _safe_name(name: str) -> str:
    name = re.sub(r"[^\w.\-]+", "_", name).strip("_")
    return name[:120] or "documento"


def download_doc(proceso_id: int, doc: dict) -> int | None:
    """Descarga un documento y lo registra. Devuelve documento_id o None."""
    url = doc["url"]
    try:
        resp = requests.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=DOWNLOAD_TIMEOUT, stream=True
        )
        resp.raise_for_status()
        content = resp.content
    except requests.RequestException as exc:
        log.warning("download fallo url=%s err=%s", url, exc)
        return None

    mime = resp.headers.get("Content-Type", "").split(";")[0] or mimetypes.guess_type(url)[0]
    ext = Path(url.split("?")[0]).suffix or (mimetypes.guess_extension(mime or "") or ".bin")
    sha = hashlib.sha256(content).hexdigest()[:16]
    fname = f"{proceso_id}_{sha}_{_safe_name(doc.get('nombre', 'doc'))}{ext if ext.startswith('.') else ''}"
    dest = DOCS_DIR / fname
    dest.write_bytes(content)

    doc_id = repo.insert_documento(
        {
            "proceso_id": proceso_id,
            "nombre": doc.get("nombre"),
            "url": url,
            "ruta_local": str(dest),
            "mime": mime,
            "bytes": len(content),
        }
    )
    log.info("download ok proceso=%d doc_id=%s bytes=%d", proceso_id, doc_id, len(content))
    return doc_id


def download_docs_for_proceso(proceso_id: int, docs: list[dict]) -> int:
    n = 0
    for d in docs:
        if download_doc(proceso_id, d):
            n += 1
    return n
