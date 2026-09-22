"""Relevancia de licitaciones segun el perfil de la empresa.

No filtra de forma dura: calcula un puntaje por palabra clave / sector / ubicacion
para *priorizar* lo afin a la empresa sin ocultar el resto del mercado.
"""
from __future__ import annotations

import unicodedata


def _norm(texto: str | None) -> str:
    """Minusculas sin tildes, para comparar de forma robusta."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(texto))
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_tildes.lower()


# Puntaje minimo para considerar una licitacion "muy acertada" (match en objeto).
SCORE_ACERTADA = 3


def keywords_de_perfil(perfil: dict | None) -> list[str]:
    """Lista normalizada de palabras clave.

    Incluye el sector, las palabras del usuario y, si existen, las palabras
    expandidas por IA (`palabras_clave_ia`).
    """
    if not perfil:
        return []
    crudas = (perfil.get("palabras_clave") or "").split(",")
    crudas += (perfil.get("palabras_clave_ia") or "").split(",")
    if perfil.get("sector"):
        crudas.append(perfil["sector"])
    vistos: list[str] = []
    for k in crudas:
        kn = _norm(k).strip()
        if kn and kn not in vistos:
            vistos.append(kn)
    return vistos


def terminos_scrape(perfil: dict | None, max_terms: int = 12) -> list[str]:
    """Terminos (grafia original, con tildes) para filtrar el scrape en SECOP.

    A diferencia de `keywords_de_perfil` (normaliza sin tildes para comparar en
    memoria), aqui se preserva el texto tal cual porque el `like` de Socrata
    compara contra el objeto acentuado. Prioriza palabras del usuario, luego IA,
    luego sector; se acota a `max_terms` para no exceder el largo del query.
    """
    if not perfil:
        return []
    out: list[str] = []
    vistos: set[str] = set()
    fuentes = (
        perfil.get("palabras_clave") or "",
        perfil.get("palabras_clave_ia") or "",
        perfil.get("sector") or "",
    )
    for fuente in fuentes:
        for t in fuente.split(","):
            t = t.strip()
            n = _norm(t)
            if t and n not in vistos:
                vistos.add(n)
                out.append(t)
            if len(out) >= max_terms:
                return out
    return out


def score_proceso(proc: dict, keywords: list[str], perfil: dict | None = None) -> int:
    """Puntaje de afinidad. 0 = sin relacion con el perfil."""
    if not keywords:
        return 0
    objeto = _norm(proc.get("objeto"))
    entidad = _norm(proc.get("entidad"))
    score = 0
    for kw in keywords:
        if kw in objeto:
            score += 3          # match en el objeto pesa mas
        elif kw in entidad:
            score += 1
    # Bono leve por coincidencia de ubicacion (no excluye otras ciudades).
    if perfil:
        if perfil.get("ciudad") and _norm(perfil["ciudad"]) == _norm(proc.get("ciudad")):
            score += 1
        if perfil.get("departamento") and _norm(perfil["departamento"]) == _norm(
            proc.get("departamento")
        ):
            score += 1
    return score


def anotar_relevancia(
    procesos: list[dict], perfil: dict | None
) -> tuple[list[dict], int]:
    """Agrega `_relevancia` y `_relevante` a cada proceso. Devuelve (lista, n_relevantes)."""
    keywords = keywords_de_perfil(perfil)
    n_rel = 0
    salida = []
    for p in procesos:
        s = score_proceso(p, keywords, perfil)
        q = {
            **p,
            "_relevancia": s,
            "_relevante": s > 0,
            "_acertada": s >= SCORE_ACERTADA,  # match fuerte (en el objeto)
        }
        if s > 0:
            n_rel += 1
        salida.append(q)
    return salida, n_rel


def ordenar_por_relevancia(procesos: list[dict]) -> list[dict]:
    """Mas afines primero; mantiene el orden original (por fecha) en empates."""
    return sorted(procesos, key=lambda p: p.get("_relevancia", 0), reverse=True)
