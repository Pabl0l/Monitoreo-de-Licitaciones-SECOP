"""Mejora del perfil de empresa con IA (DeepSeek) para afinar el match.

Toma el perfil que escribio el usuario (sector, descripcion, palabras clave) y
pide al motor LLM que lo enriquezca con vocabulario real de licitacion publica
colombiana (SECOP): sinonimos, terminos tecnicos y objetos de contrato afines.
El resultado alimenta `analysis/relevancia.py`, que prioriza/filtra las
licitaciones mas acertadas para la empresa.
"""
from __future__ import annotations

from llm import engine
from utils.logging_conf import get_logger

log = get_logger(__name__)

_SYS = (
    "Eres experto en contratacion publica colombiana (SECOP). Conoces como se "
    "redactan los objetos de los procesos y que palabras usan las entidades. "
    "Tu tarea es enriquecer el perfil de una empresa para encontrar las "
    "licitaciones mas afines. Usa solo terminos realistas del mercado colombiano."
)

_TMPL = """Con base en este perfil de empresa, genera datos para mejorar la
busqueda de licitaciones afines en SECOP.

=== PERFIL ACTUAL ===
Nombre: {nombre}
Sector: {sector}
Palabras clave actuales: {palabras_clave}
Ciudad: {ciudad}
Departamento: {departamento}
Descripcion: {descripcion}

Devuelve EXACTAMENTE este JSON (sin texto adicional):
{{
  "palabras_clave": "lista de 15-25 terminos separados por coma: incluye las
actuales, sinonimos, terminos tecnicos del sector y tipos de objeto de contrato
que esta empresa podria ganar. Solo terminos, en minuscula, sin numerar.",
  "descripcion": "2-3 frases que describan con precision a que licitaciones
deberia aplicar esta empresa y por que (capacidades, sector, alcance)."
}}
"""


def _ctx(perfil: dict) -> dict:
    return {
        "nombre": perfil.get("nombre") or "No definido",
        "sector": perfil.get("sector") or "No definido",
        "palabras_clave": perfil.get("palabras_clave") or "No definidas",
        "ciudad": perfil.get("ciudad") or "No definida",
        "departamento": perfil.get("departamento") or "No definido",
        "descripcion": perfil.get("descripcion") or "No definida",
    }


def mejorar_perfil(perfil: dict) -> dict:
    """Devuelve {palabras_clave_ia, descripcion_ia}. {} si el motor no responde."""
    if not perfil:
        return {}
    if not engine.is_available():
        log.warning("Motor LLM no disponible; omito mejora de perfil")
        return {}

    raw = engine.generate(_TMPL.format(**_ctx(perfil)), system=_SYS, json_mode=True)
    data = engine.parse_json(raw)
    kw = str(data.get("palabras_clave", "") or "").strip()
    desc = str(data.get("descripcion", "") or "").strip()
    if not kw and not desc:
        log.warning("mejora de perfil: respuesta vacia o no parseable")
        return {}
    return {"palabras_clave_ia": kw, "descripcion_ia": desc}
