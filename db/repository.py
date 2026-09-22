"""CRUD helpers sobre SQLite. Upsert idempotente para evitar duplicados."""
import json
from typing import Any

from db.database import get_conn


# ---------------- Procesos ----------------
def upsert_proceso(p: dict) -> int:
    """Inserta/actualiza por secop_id. Devuelve proceso_id."""
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO procesos (secop_id, entidad, objeto, valor, fecha_publicacion,
                                  estado, departamento, ciudad, url, raw_json)
            VALUES (:secop_id, :entidad, :objeto, :valor, :fecha_publicacion,
                    :estado, :departamento, :ciudad, :url, :raw_json)
            ON CONFLICT(secop_id) DO UPDATE SET
                entidad=excluded.entidad, objeto=excluded.objeto, valor=excluded.valor,
                fecha_publicacion=excluded.fecha_publicacion, estado=excluded.estado,
                departamento=excluded.departamento, ciudad=excluded.ciudad,
                url=excluded.url, raw_json=excluded.raw_json
            """,
            {
                "secop_id": p["secop_id"],
                "entidad": p.get("entidad"),
                "objeto": p.get("objeto"),
                "valor": p.get("valor"),
                "fecha_publicacion": p.get("fecha_publicacion"),
                "estado": p.get("estado"),
                "departamento": p.get("departamento"),
                "ciudad": p.get("ciudad"),
                "url": p.get("url"),
                "raw_json": json.dumps(p.get("raw", {}), ensure_ascii=False),
            },
        )
        _ = cur  # lastrowid no es fiable en ON CONFLICT UPDATE -> resolver por secop_id
        row = conn.execute(
            "SELECT id FROM procesos WHERE secop_id=?", (p["secop_id"],)
        ).fetchone()
        return row["id"] if row else -1


def list_procesos(
    entidad: str | None = None,
    valor_min: float | None = None,
    valor_max: float | None = None,
    texto: str | None = None,
    ciudad: str | None = None,
    departamento: str | None = None,
    estado: str | None = None,
    limit: int = 500,
) -> list[dict]:
    sql = "SELECT * FROM procesos WHERE 1=1"
    params: list[Any] = []
    if entidad:
        sql += " AND entidad LIKE ?"
        params.append(f"%{entidad}%")
    if ciudad:
        sql += " AND ciudad LIKE ?"
        params.append(f"%{ciudad}%")
    if departamento:
        sql += " AND departamento LIKE ?"
        params.append(f"%{departamento}%")
    if estado:
        sql += " AND estado LIKE ?"
        params.append(f"%{estado}%")
    if valor_min is not None:
        sql += " AND valor >= ?"
        params.append(valor_min)
    if valor_max is not None:
        sql += " AND valor <= ?"
        params.append(valor_max)
    if texto:
        sql += " AND (objeto LIKE ? OR entidad LIKE ?)"
        params += [f"%{texto}%", f"%{texto}%"]
    sql += " ORDER BY fecha_publicacion DESC LIMIT ?"
    params.append(limit)
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def get_proceso(proceso_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM procesos WHERE id=?", (proceso_id,)).fetchone()
        return dict(row) if row else None


def distinct_values(columna: str, limit: int = 200) -> list[str]:
    """Valores distintos no nulos de una columna (para autocompletar)."""
    if columna not in {"entidad", "departamento", "estado", "ciudad"}:
        return []
    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT DISTINCT {columna} AS v FROM procesos "
            f"WHERE {columna} IS NOT NULL AND {columna} != '' ORDER BY v LIMIT ?",
            (limit,),
        ).fetchall()
        return [r["v"] for r in rows]


def count_procesos() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) AS c FROM procesos").fetchone()["c"]


# ---------------- Perfil de empresa ----------------
_PERFIL_CAMPOS = (
    "nombre", "sector", "palabras_clave", "ciudad", "departamento", "descripcion",
    "nit", "representante", "correo", "telefono", "direccion", "sitio_web",
)
# Campos generados/refinados por IA (DeepSeek): se actualizan aparte.
_PERFIL_CAMPOS_IA = ("palabras_clave_ia", "descripcion_ia")


def get_perfil() -> dict | None:
    """Perfil unico de la empresa (fila id=1) o None si no existe."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM empresa_perfil WHERE id=1").fetchone()
        return dict(row) if row else None


def save_perfil(data: dict) -> None:
    """Upsert de los campos editables por el usuario (siempre id=1).

    El SQL se arma desde `_PERFIL_CAMPOS` para no desincronizarse al agregar campos.
    """
    valores = {c: (data.get(c) or "").strip() for c in _PERFIL_CAMPOS}
    cols = ", ".join(_PERFIL_CAMPOS)
    placeholders = ", ".join(f":{c}" for c in _PERFIL_CAMPOS)
    updates = ", ".join(f"{c}=excluded.{c}" for c in _PERFIL_CAMPOS)
    with get_conn() as conn:
        conn.execute(
            f"""
            INSERT INTO empresa_perfil (id, {cols}, updated_at)
            VALUES (1, {placeholders}, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                {updates}, updated_at=datetime('now')
            """,
            valores,
        )


def save_perfil_ia(palabras_clave_ia: str, descripcion_ia: str) -> None:
    """Guarda los campos enriquecidos por IA sin tocar lo que escribio el usuario.

    Requiere que el perfil ya exista (fila id=1).
    """
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE empresa_perfil
               SET palabras_clave_ia = :kw_ia,
                   descripcion_ia    = :desc_ia,
                   updated_at        = datetime('now')
             WHERE id = 1
            """,
            {"kw_ia": (palabras_clave_ia or "").strip(),
             "desc_ia": (descripcion_ia or "").strip()},
        )


# ---------------- Favoritos ----------------
def toggle_favorito(proceso_id: int) -> bool:
    """Agrega/quita favorito. Devuelve True si quedo marcado."""
    with get_conn() as conn:
        existe = conn.execute(
            "SELECT 1 FROM favoritos WHERE proceso_id=?", (proceso_id,)
        ).fetchone()
        if existe:
            conn.execute("DELETE FROM favoritos WHERE proceso_id=?", (proceso_id,))
            return False
        conn.execute("INSERT INTO favoritos (proceso_id) VALUES (?)", (proceso_id,))
        return True


def favorito_ids() -> set[int]:
    with get_conn() as conn:
        return {r["proceso_id"] for r in conn.execute("SELECT proceso_id FROM favoritos")}


def list_favoritos() -> list[dict]:
    with get_conn() as conn:
        return [
            dict(r)
            for r in conn.execute(
                "SELECT p.* FROM procesos p JOIN favoritos f ON f.proceso_id=p.id "
                "ORDER BY f.created_at DESC"
            ).fetchall()
        ]


# ---------------- Decisiones (modo match/descartar) ----------------
def set_decision(proceso_id: int, decision: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO decisiones (proceso_id, decision) VALUES (?, ?) "
            "ON CONFLICT(proceso_id) DO UPDATE SET decision=excluded.decision, "
            "created_at=datetime('now')",
            (proceso_id, decision),
        )


def decision_ids() -> set[int]:
    with get_conn() as conn:
        return {r["proceso_id"] for r in conn.execute("SELECT proceso_id FROM decisiones")}


def reset_decisiones() -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM decisiones")


def list_matches() -> list[dict]:
    with get_conn() as conn:
        return [
            dict(r)
            for r in conn.execute(
                "SELECT p.* FROM procesos p JOIN decisiones d ON d.proceso_id=p.id "
                "WHERE d.decision='match' ORDER BY d.created_at DESC"
            ).fetchall()
        ]


# ---------------- Documentos ----------------
def insert_documento(doc: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO documentos (proceso_id, nombre, url, ruta_local, mime, bytes)
            VALUES (:proceso_id, :nombre, :url, :ruta_local, :mime, :bytes)
            ON CONFLICT(proceso_id, url) DO UPDATE SET
                ruta_local=excluded.ruta_local, mime=excluded.mime, bytes=excluded.bytes
            """,
            doc,
        )
        _ = cur
        row = conn.execute(
            "SELECT id FROM documentos WHERE proceso_id=? AND url=?",
            (doc["proceso_id"], doc["url"]),
        ).fetchone()
        return row["id"]


def set_documento_texto(doc_id: int, texto: str, ocr_usado: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE documentos SET texto=?, ocr_usado=?, procesado=1 WHERE id=?",
            (texto, int(ocr_usado), doc_id),
        )


def list_documentos(proceso_id: int) -> list[dict]:
    with get_conn() as conn:
        return [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM documentos WHERE proceso_id=?", (proceso_id,)
            ).fetchall()
        ]


def docs_sin_procesar(limit: int = 50) -> list[dict]:
    with get_conn() as conn:
        return [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM documentos WHERE procesado=0 AND ruta_local IS NOT NULL LIMIT ?",
                (limit,),
            ).fetchall()
        ]


# ---------------- Requisitos ----------------
def insert_requisitos(req: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO requisitos_extraidos
                (proceso_id, documento_id, experiencia, financiero, personal, equipos,
                 n_requisitos, complejidad, pct_estructurado, modelo)
            VALUES (:proceso_id, :documento_id, :experiencia, :financiero, :personal, :equipos,
                    :n_requisitos, :complejidad, :pct_estructurado, :modelo)
            """,
            req,
        )
        return cur.lastrowid


def list_requisitos(proceso_id: int) -> list[dict]:
    with get_conn() as conn:
        return [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM requisitos_extraidos WHERE proceso_id=? ORDER BY created_at DESC",
                (proceso_id,),
            ).fetchall()
        ]
