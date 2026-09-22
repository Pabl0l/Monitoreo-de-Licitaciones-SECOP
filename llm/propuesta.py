"""Resumen de licitacion y generacion de propuesta profesional con LLM local.

Usa el proceso (objeto, entidad, valor, etc.) y, si existen, los requisitos
extraidos del pliego. Todo corre en Ollama local; sin servicios pagos.
"""
from llm import engine
from utils.logging_conf import get_logger

log = get_logger(__name__)

_SYS_RESUMEN = (
    "Eres analista de licitacion publica colombiana (SECOP). "
    "Resumes procesos de forma clara y util para un empresario que decide si participar. "
    "Responde solo con datos del contexto; no inventes cifras."
)

_TMPL_RESUMEN = """Resume esta licitacion en espanol, formato markdown breve:

**De que se trata** (1-2 frases).
**Puntos clave** (3-4 vinetas: alcance, valor, plazo si aparece).
**Para quien aplica** (perfil de empresa ideal, 1 frase).

=== DATOS DEL PROCESO ===
Entidad: {entidad}
Objeto: {objeto}
Valor: {valor}
Departamento: {departamento}
Ciudad: {ciudad}
Estado: {estado}
Fecha publicacion: {fecha}
{requisitos}
"""

_SYS_PROPUESTA = (
    "Eres consultor experto en propuestas para licitacion publica colombiana. "
    "Redactas propuestas profesionales, persuasivas y bien estructuradas en espanol. "
    "Tono formal, concreto, orientado a ganar el proceso. "
    "Produces un documento FINAL, listo para enviar a la entidad: usa los datos del "
    "oferente que se te dan (empresa, NIT, representante legal, correo, telefono, "
    "direccion) en el encabezado, la carta y la firma. "
    "Solo donde un dato del oferente falte realmente, deja [completar] como marcador. "
    "No inventes cifras, experiencia ni certificaciones que no esten en el contexto."
)

_TMPL_PROPUESTA = """Redacta una PROPUESTA COMPLETA y lista para enviar para esta \
licitacion publica, en espanol, formato markdown. Debe poder imprimirse y radicarse \
tal cual.

Estructura obligatoria:

# Propuesta — {objeto_corto}

**Encabezado del oferente:** razon social, NIT, representante legal, direccion, \
telefono, correo y sitio web (usa los datos dados; omite el que no exista).

**Ciudad y fecha:** usa la ciudad del oferente y deja la fecha como {fecha_hoy}.

**Señores {entidad}:** linea de destinatario.

1. **Carta de presentacion** firmada por el representante legal, manifestando interes \
formal en participar en el proceso (referencia el objeto y la entidad).
2. **Comprension del objeto y necesidad** de la entidad.
3. **Propuesta tecnica: enfoque y metodologia** para ejecutar el contrato.
4. **Equipo de trabajo** propuesto (perfiles y roles).
5. **Plan de trabajo y cronograma** por fases.
6. **Experiencia y valor diferencial** del oferente (usa solo lo dado; si no hay, \
redactalo de forma general sin inventar cifras).
7. **Compromisos del oferente** (cumplimiento de requisitos del pliego, garantias).
8. **Bloque de firma:** nombre del representante legal, cargo, empresa, NIT y datos \
de contacto.

=== OFERENTE ===
Empresa: {empresa}
NIT: {nit}
Representante legal: {representante}
Correo: {correo}
Telefono: {telefono}
Direccion: {direccion}
Ciudad del oferente: {oferente_ciudad}
Sitio web: {sitio_web}
Perfil / descripcion: {descripcion}

=== DATOS DEL PROCESO ===
Entidad: {entidad}
Objeto: {objeto}
Valor estimado: {valor}
Ubicacion: {ciudad}, {departamento}
{requisitos}
"""


def _fmt_valor(v) -> str:
    try:
        return f"${float(v):,.0f} COP"
    except (TypeError, ValueError):
        return "No publicado"


def _bloque_requisitos(requisitos: list[dict]) -> str:
    """Texto con requisitos extraidos del pliego, si los hay."""
    if not requisitos:
        return ""
    r = requisitos[0]
    campos = [
        ("Experiencia exigida", r.get("experiencia")),
        ("Capacidad financiera", r.get("financiero")),
        ("Personal requerido", r.get("personal")),
        ("Equipos requeridos", r.get("equipos")),
    ]
    lineas = [f"{etq}: {val}" for etq, val in campos if val]
    return "\n=== REQUISITOS DEL PLIEGO ===\n" + "\n".join(lineas) if lineas else ""


def _ctx(proc: dict) -> dict:
    return {
        "entidad": proc.get("entidad") or "No definida",
        "objeto": proc.get("objeto") or "No definido",
        "valor": _fmt_valor(proc.get("valor")),
        "departamento": proc.get("departamento") or "No definido",
        "ciudad": proc.get("ciudad") or "No definida",
        "estado": proc.get("estado") or "No definido",
        "fecha": (proc.get("fecha_publicacion") or "")[:10] or "No definida",
    }


def resumir(proc: dict, requisitos: list[dict] | None = None) -> str:
    """Resumen breve en markdown. '' si el motor LLM no responde."""
    if not engine.is_available():
        return ""
    ctx = _ctx(proc)
    ctx["requisitos"] = _bloque_requisitos(requisitos or [])
    return engine.generate(_TMPL_RESUMEN.format(**ctx), system=_SYS_RESUMEN).strip()


def generar_propuesta(
    proc: dict, oferente: dict | None = None, requisitos: list[dict] | None = None
) -> str:
    """Propuesta completa en markdown, lista para enviar. '' si el LLM no responde.

    `oferente` = perfil de la empresa (nombre, nit, representante, correo, etc.).
    """
    if not engine.is_available():
        return ""
    import datetime

    o = oferente or {}

    def _v(campo: str, default: str = "[completar]") -> str:
        return (o.get(campo) or "").strip() or default

    objeto = proc.get("objeto") or "la presente licitacion"
    ctx = _ctx(proc)
    ctx.update({
        "empresa": _v("nombre", "[Nombre de la empresa oferente]"),
        "nit": _v("nit"),
        "representante": _v("representante"),
        "correo": _v("correo"),
        "telefono": _v("telefono"),
        "direccion": _v("direccion"),
        "oferente_ciudad": _v("ciudad", "[ciudad]"),
        "sitio_web": _v("sitio_web", "No aplica"),
        "descripcion": _v("descripcion", "No suministrada"),
        "objeto_corto": objeto[:90],
        "fecha_hoy": datetime.date.today().strftime("%d/%m/%Y"),
        "requisitos": _bloque_requisitos(requisitos or []),
    })
    return engine.generate(_TMPL_PROPUESTA.format(**ctx), system=_SYS_PROPUESTA).strip()
