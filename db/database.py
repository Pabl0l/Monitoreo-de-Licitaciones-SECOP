"""SQLite local: conexion + schema. Tablas: procesos, documentos, requisitos_extraidos."""
import sqlite3
from contextlib import contextmanager

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS procesos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    secop_id        TEXT UNIQUE NOT NULL,
    entidad         TEXT,
    objeto          TEXT,
    valor           REAL,
    fecha_publicacion TEXT,
    estado          TEXT,
    departamento    TEXT,
    ciudad          TEXT,
    url             TEXT,
    raw_json        TEXT,
    scraped_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS documentos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id   INTEGER NOT NULL REFERENCES procesos(id) ON DELETE CASCADE,
    nombre       TEXT,
    url          TEXT,
    ruta_local   TEXT,
    mime         TEXT,
    bytes        INTEGER,
    texto        TEXT,
    ocr_usado    INTEGER DEFAULT 0,
    procesado    INTEGER DEFAULT 0,
    created_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(proceso_id, url)
);

CREATE TABLE IF NOT EXISTS requisitos_extraidos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id      INTEGER NOT NULL REFERENCES procesos(id) ON DELETE CASCADE,
    documento_id    INTEGER REFERENCES documentos(id) ON DELETE CASCADE,
    experiencia     TEXT,
    financiero      TEXT,
    personal        TEXT,
    equipos         TEXT,
    n_requisitos    INTEGER DEFAULT 0,
    complejidad     TEXT,
    pct_estructurado REAL,
    modelo          TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS favoritos (
    proceso_id  INTEGER PRIMARY KEY REFERENCES procesos(id) ON DELETE CASCADE,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS decisiones (
    proceso_id  INTEGER PRIMARY KEY REFERENCES procesos(id) ON DELETE CASCADE,
    decision    TEXT NOT NULL,   -- match | descartar
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS empresa_perfil (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    nombre          TEXT,
    sector          TEXT,
    palabras_clave  TEXT,   -- separadas por coma
    ciudad          TEXT,
    departamento    TEXT,
    descripcion     TEXT,
    nit             TEXT,
    representante   TEXT,
    correo          TEXT,
    telefono        TEXT,
    direccion       TEXT,
    sitio_web       TEXT,
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_proc_entidad ON procesos(entidad);
CREATE INDEX IF NOT EXISTS idx_proc_valor   ON procesos(valor);
CREATE INDEX IF NOT EXISTS idx_doc_proceso  ON documentos(proceso_id);
"""

# Columnas agregadas tras la version inicial -> migracion idempotente.
# (column add, luego index; en ese orden, para bases ya existentes.)
MIGRATIONS = [
    ("procesos", "ciudad", "ALTER TABLE procesos ADD COLUMN ciudad TEXT"),
    # Perfil mejorado por IA (DeepSeek): keywords expandidas + descripcion refinada.
    ("empresa_perfil", "palabras_clave_ia",
     "ALTER TABLE empresa_perfil ADD COLUMN palabras_clave_ia TEXT"),
    ("empresa_perfil", "descripcion_ia",
     "ALTER TABLE empresa_perfil ADD COLUMN descripcion_ia TEXT"),
    # Datos de contacto del oferente -> propuesta lista para enviar.
    ("empresa_perfil", "nit", "ALTER TABLE empresa_perfil ADD COLUMN nit TEXT"),
    ("empresa_perfil", "representante",
     "ALTER TABLE empresa_perfil ADD COLUMN representante TEXT"),
    ("empresa_perfil", "correo", "ALTER TABLE empresa_perfil ADD COLUMN correo TEXT"),
    ("empresa_perfil", "telefono", "ALTER TABLE empresa_perfil ADD COLUMN telefono TEXT"),
    ("empresa_perfil", "direccion", "ALTER TABLE empresa_perfil ADD COLUMN direccion TEXT"),
    ("empresa_perfil", "sitio_web", "ALTER TABLE empresa_perfil ADD COLUMN sitio_web TEXT"),
]
POST_MIGRATION_DDL = [
    "CREATE INDEX IF NOT EXISTS idx_proc_ciudad ON procesos(ciudad)",
]


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        _migrate(conn)


def _migrate(conn: sqlite3.Connection) -> None:
    """Aplica ALTERs faltantes en bases ya creadas (sin perder datos)."""
    for tabla, columna, ddl in MIGRATIONS:
        cols = {r["name"] for r in conn.execute(f"PRAGMA table_info({tabla})")}
        if columna not in cols:
            conn.execute(ddl)
    for ddl in POST_MIGRATION_DDL:
        conn.execute(ddl)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
