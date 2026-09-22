"""Metricas heuristicas simples sobre los requisitos extraidos.

Sin scoring complejo (por diseno): solo conteos y heuristicas transparentes.
"""
import re

CATEGORIAS = ("experiencia", "financiero", "personal", "equipos")

# Palabras que sugieren requisito ambiguo / poco estructurado.
AMBIGUO_HINTS = re.compile(
    r"\b(podr[ai]a?|eventualmente|aproximad|seg[uú]n|deseable|preferible|entre otros|etc)\b",
    re.IGNORECASE,
)
# Senales de requisito estructurado (numeros, montos, unidades).
ESTRUCT_HINTS = re.compile(
    r"(\d|\$|smmlv|smlmv|a[nñ]os?|%|salarios m[ií]nimos)", re.IGNORECASE
)


def _contar_items(texto: str) -> int:
    """Cuenta items por saltos de linea, bullets o ';'."""
    if not texto.strip():
        return 0
    pedazos = re.split(r"[\n;•\-]+", texto)
    return len([p for p in pedazos if len(p.strip()) > 3])


def calcular_metricas(requisitos: dict) -> dict:
    """Devuelve n_requisitos, complejidad (baja|media|alta), pct_estructurado."""
    total = 0
    estruct = 0
    ambiguos = 0
    for cat in CATEGORIAS:
        texto = requisitos.get(cat, "") or ""
        n = _contar_items(texto)
        total += n
        if ESTRUCT_HINTS.search(texto):
            estruct += n
        if AMBIGUO_HINTS.search(texto):
            ambiguos += n

    pct = round(100 * estruct / total, 1) if total else 0.0

    if total <= 3:
        complejidad = "baja"
    elif total <= 8:
        complejidad = "media"
    else:
        complejidad = "alta"

    return {
        "n_requisitos": total,
        "complejidad": complejidad,
        "pct_estructurado": pct,
    }
