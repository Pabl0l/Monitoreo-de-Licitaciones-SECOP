"""Extrae requisitos estructurados de un pliego usando el LLM local.

Salida JSON: {experiencia, financiero, personal, equipos}.
El texto se recorta para no exceder la ventana del modelo en 8GB.
"""
from config import LLM_ENGINE, OLLAMA_MODEL
from llm import engine
from utils.logging_conf import get_logger

log = get_logger(__name__)

MAX_CHARS = 12000  # recorte conservador para modelos pequenos

SYSTEM = (
    "Eres analista de pliegos de licitacion publica colombiana. "
    "Extraes requisitos del texto provisto. Responde SOLO con la informacion del texto; "
    "si un campo no aparece, deja string vacio. No inventes datos."
)

PROMPT_TMPL = """Del siguiente pliego, extrae los requisitos en estas categorias:
- experiencia: experiencia minima exigida (anios, contratos similares, valores).
- financiero: capacidad financiera (indices, patrimonio, capital de trabajo).
- personal: personal minimo requerido (perfiles, cantidad, dedicacion).
- equipos: equipos/maquinaria/infraestructura exigida.

Devuelve EXACTAMENTE este JSON:
{{"experiencia": "", "financiero": "", "personal": "", "equipos": ""}}

=== PLIEGO ===
{texto}
"""


def extraer_requisitos(texto: str) -> dict:
    """Devuelve dict con las 4 claves. {} si el LLM no esta disponible."""
    if not texto.strip():
        return {}
    if not engine.is_available():
        log.warning("Motor LLM no disponible; omito extraccion LLM")
        return {}

    recorte = texto[:MAX_CHARS]
    raw = engine.generate(
        PROMPT_TMPL.format(texto=recorte), system=SYSTEM, json_mode=True
    )
    data = engine.parse_json(raw)
    # Garantiza las 4 claves.
    result = {
        "experiencia": str(data.get("experiencia", "") or ""),
        "financiero": str(data.get("financiero", "") or ""),
        "personal": str(data.get("personal", "") or ""),
        "equipos": str(data.get("equipos", "") or ""),
        "modelo": LLM_ENGINE if LLM_ENGINE == "deepseek" else OLLAMA_MODEL,
    }
    return result
