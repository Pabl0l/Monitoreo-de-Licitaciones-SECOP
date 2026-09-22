"""Normaliza filas Socrata SECOP -> dict de proceso.

Los nombres de campo varian segun version del dataset; se prueban candidatos.
"""
from typing import Any


def _first(row: dict, keys: list[str]) -> Any | None:
    for k in keys:
        v = row.get(k)
        if v not in (None, "", "No Definido"):
            return v
    return None


def _to_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except (ValueError, TypeError):
        return None


def normalize(row: dict) -> dict | None:
    secop_id = _first(row, ["id_del_proceso", "referencia_del_proceso", "constancia"])
    if not secop_id:
        return None

    url = _first(row, ["urlproceso", "url_del_proceso", "url"])
    if isinstance(url, dict):  # Socrata URL field
        url = url.get("url")

    return {
        "secop_id": str(secop_id),
        "entidad": _first(row, ["entidad", "nombre_de_la_entidad", "nombre_entidad"]),
        "objeto": _first(
            row, ["objeto_del_contrato", "objeto_a_contratar", "nombre_del_procedimiento"]
        ),
        "valor": _to_float(
            _first(row, ["precio_base", "valor_total_adjudicacion", "presupuesto_general"])
        ),
        "fecha_publicacion": _first(
            row, ["fecha_de_publicacion_del", "fecha_de_publicacion", "fecha_de_apertura"]
        ),
        "estado": _first(row, ["estado_del_procedimiento", "estado_de_apertura_del", "fase"]),
        "departamento": _first(row, ["departamento_entidad", "departamento"]),
        "ciudad": _first(
            row, ["ciudad_entidad", "ciudad", "ciudad_de_la_unidad_de", "municipio"]
        ),
        "url": url,
        "raw": row,
    }
