"""Orquesta el flujo completo. Cada paso es independiente y se puede correr solo.

scrape -> download -> process(ocr+llm+metrics)
"""
from analysis.metrics import calcular_metricas
from db import repository as repo
from db.database import init_db
from downloader.downloader import download_docs_for_proceso
from llm.extractor import extraer_requisitos
from ocr.extract import extract_text
from scraper.doc_links import discover_docs
from scraper.secop_api import fetch_procesos, where_por_keywords
from utils.logging_conf import get_logger

log = get_logger(__name__)


def step_scrape(max_rows: int | None = None, keywords: list[str] | None = None) -> int:
    """Trae procesos SECOP y los guarda. Devuelve cuantos.

    Si `keywords` viene, filtra en el API por el sector de la empresa (objeto),
    para no llenar la base de licitaciones sin relacion con el perfil.
    """
    init_db()
    where = where_por_keywords(keywords) if keywords else None
    procesos = fetch_procesos(max_rows=max_rows, where=where)
    n = 0
    for p in procesos:
        repo.upsert_proceso(p)
        n += 1
    log.info("step_scrape guardados=%d", n)
    return n


def step_download(limit_procesos: int = 20) -> int:
    """Descubre y descarga documentos para procesos que tengan URL."""
    procesos = repo.list_procesos(limit=limit_procesos)
    total_docs = 0
    for p in procesos:
        if not p.get("url"):
            continue
        docs = discover_docs(p["url"])
        total_docs += download_docs_for_proceso(p["id"], docs)
    log.info("step_download docs=%d", total_docs)
    return total_docs


def step_process(limit_docs: int = 30) -> int:
    """OCR + LLM + metricas para documentos sin procesar."""
    docs = repo.docs_sin_procesar(limit=limit_docs)
    n = 0
    for d in docs:
        texto, ocr_usado = extract_text(d["ruta_local"], d.get("mime"))
        repo.set_documento_texto(d["id"], texto, ocr_usado)
        if not texto.strip():
            continue

        requisitos = extraer_requisitos(texto)
        if not requisitos:
            continue
        metricas = calcular_metricas(requisitos)
        repo.insert_requisitos(
            {
                "proceso_id": d["proceso_id"],
                "documento_id": d["id"],
                "experiencia": requisitos.get("experiencia"),
                "financiero": requisitos.get("financiero"),
                "personal": requisitos.get("personal"),
                "equipos": requisitos.get("equipos"),
                "n_requisitos": metricas["n_requisitos"],
                "complejidad": metricas["complejidad"],
                "pct_estructurado": metricas["pct_estructurado"],
                "modelo": requisitos.get("modelo"),
            }
        )
        n += 1
    log.info("step_process procesados=%d", n)
    return n


def run_all(max_rows: int | None = None) -> dict:
    """Pipeline completo de punta a punta."""
    s = step_scrape(max_rows)
    d = step_download()
    p = step_process()
    return {"procesos": s, "documentos": d, "procesados": p}
