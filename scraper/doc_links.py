"""Descubre enlaces a documentos (PDF) de un proceso.

Estrategia:
1. requests + BeautifulSoup sobre la pagina del proceso (rapido).
2. Playwright como fallback si la pagina es dinamica (JS).

Best-effort: si nada funciona, devuelve []. La pagina SECOP II es dinamica,
asi que Playwright suele ser necesario; requests sirve para enlaces directos.
"""
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import USER_AGENT
from utils.logging_conf import get_logger

log = get_logger(__name__)

PDF_HINTS = (".pdf", ".docx", ".doc", ".xlsx", ".xls")


def _from_html(html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    found: list[dict] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(h in href.lower() for h in PDF_HINTS):
            full = urljoin(base_url, href)
            if full in seen:
                continue
            seen.add(full)
            found.append({"nombre": a.get_text(strip=True) or full.split("/")[-1], "url": full})
    return found


def discover_requests(process_url: str) -> list[dict]:
    """Intento rapido con requests + BS4."""
    try:
        resp = requests.get(process_url, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()
        return _from_html(resp.text, process_url)
    except requests.RequestException as exc:
        log.warning("doc_links requests fallo url=%s err=%s", process_url, exc)
        return []


def discover_playwright(process_url: str) -> list[dict]:
    """Fallback con Playwright (paginas dinamicas). Import perezoso."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.warning("playwright no instalado; omitiendo fallback dinamico")
        return []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            page.goto(process_url, timeout=45000, wait_until="networkidle")
            html = page.content()
            browser.close()
        return _from_html(html, process_url)
    except Exception as exc:  # noqa: BLE001
        log.warning("doc_links playwright fallo url=%s err=%s", process_url, exc)
        return []


def discover_docs(process_url: str | None) -> list[dict]:
    """Combina estrategias. Devuelve lista de {nombre, url}."""
    if not process_url:
        return []
    docs = discover_requests(process_url)
    if not docs:
        docs = discover_playwright(process_url)
    log.info("doc_links url=%s encontrados=%d", process_url, len(docs))
    return docs
