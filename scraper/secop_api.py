"""Fetch de procesos SECOP via API Socrata (datos abiertos, gratis).

Reliable y sin Playwright. Reintentos con backoff. Maneja 429/5xx.
"""
import time

import requests

from config import (
    SECOP_APP_TOKEN,
    SECOP_DATASET,
    SECOP_DOMAIN,
    SECOP_MAX_ROWS,
    USER_AGENT,
)
from scraper.normalizer import normalize
from utils.logging_conf import get_logger

log = get_logger(__name__)

MAX_RETRIES = 4

# Campo de texto del objeto en el dataset SECOP II (p6dx-8zbt).
OBJETO_FIELD = "nombre_del_procedimiento"


def where_por_keywords(keywords: list[str], campo: str = OBJETO_FIELD) -> str | None:
    """Construye un `$where` Socrata que filtra el objeto por las palabras del perfil.

    OR de `upper(campo) like '%KW%'`: trae del API solo procesos afines al sector,
    en vez de las ultimas licitaciones sin relacion con la empresa.
    """
    terms: list[str] = []
    vistos: set[str] = set()
    for k in keywords or []:
        kw = (k or "").strip().upper().replace("'", "''")  # escapa comillas (Socrata)
        if kw and kw not in vistos:
            vistos.add(kw)
            terms.append(f"upper({campo}) like '%{kw}%'")
    return " OR ".join(terms) if terms else None


def _headers() -> dict:
    h = {"User-Agent": USER_AGENT}
    if SECOP_APP_TOKEN:
        h["X-App-Token"] = SECOP_APP_TOKEN
    return h


def fetch_procesos(max_rows: int | None = None, where: str | None = None) -> list[dict]:
    """Descarga procesos normalizados ordenados por fecha desc."""
    max_rows = max_rows or SECOP_MAX_ROWS
    url = f"https://{SECOP_DOMAIN}/resource/{SECOP_DATASET}.json"
    params = {"$limit": max_rows, "$order": ":id"}
    if where:
        params["$where"] = where

    rows = _get_with_retries(url, params)
    out: list[dict] = []
    for r in rows:
        norm = normalize(r)
        if norm:
            out.append(norm)
    log.info("socrata_fetch ok rows=%d normalizados=%d", len(rows), len(out))
    return out


def _get_with_retries(url: str, params: dict) -> list[dict]:
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, params=params, headers=_headers(), timeout=30)
            if resp.status_code == 429 or resp.status_code >= 500:
                raise requests.HTTPError(f"status {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            wait = 1.5 * (2**attempt)
            log.warning("socrata_retry attempt=%d wait=%.1f err=%s", attempt, wait, exc)
            time.sleep(wait)
    log.error("socrata_fetch fallo tras %d intentos", MAX_RETRIES)
    return []
