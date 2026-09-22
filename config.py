"""Configuracion central. Todo local, sin servicios pagos.

Override por variables de entorno (.env opcional).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Rutas ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documentos"   # PDFs descargados
DB_PATH = DATA_DIR / "secop.db"
LOG_DIR = DATA_DIR / "logs"

for _d in (DATA_DIR, DOCS_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- SECOP (Socrata open data: gratis) ---
SECOP_DOMAIN = os.getenv("SECOP_DOMAIN", "www.datos.gov.co")
SECOP_DATASET = os.getenv("SECOP_DATASET", "p6dx-8zbt")  # SECOP II Procesos
SECOP_APP_TOKEN = os.getenv("SECOP_APP_TOKEN", "")        # opcional, gratis
SECOP_MAX_ROWS = int(os.getenv("SECOP_MAX_ROWS", "100"))  # limite por corrida (8GB)

# --- Motor LLM ---
# "deepseek" (Playwright sobre chat.deepseek.com) | "ollama" (local).
LLM_ENGINE = os.getenv("LLM_ENGINE", "deepseek")

# --- Ollama (LLM local) ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
# llama3.2:3b: ~2GB, rapido en CPU/8GB. Mejor calidad: llama3.1:8b (mas lento).
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))

# --- DeepSeek via Playwright (chat web, sin API key) ---
# Login manual una vez: `python -m llm.deepseek_playwright login`.
# Perfil persistente (cookies reales) + Chrome real para evitar deteccion de
# "navegador no seguro" en el login con Google/DeepSeek.
DEEPSEEK_PROFILE_DIR = DATA_DIR / "deepseek_profile"
DEEPSEEK_MARKER = DATA_DIR / "deepseek_logged_in"   # flag tras login OK
DEEPSEEK_CHANNEL = os.getenv("DEEPSEEK_CHANNEL", "chrome")  # chrome | msedge | ""(chromium)
DEEPSEEK_HEADLESS = os.getenv("DEEPSEEK_HEADLESS", "true").lower() == "true"
DEEPSEEK_TIMEOUT = int(os.getenv("DEEPSEEK_TIMEOUT", "120"))      # s espera respuesta
DEEPSEEK_NAV_TIMEOUT = int(os.getenv("DEEPSEEK_NAV_TIMEOUT", "60"))  # s navegacion
# Compat: ya no se usa storage_state, pero se deja por si algun import viejo lo lee.
DEEPSEEK_STATE_PATH = DATA_DIR / "deepseek_state.json"

# --- OCR ---
OCR_ENGINE = os.getenv("OCR_ENGINE", "paddle")  # paddle | tesseract
OCR_LANG = os.getenv("OCR_LANG", "es")
# Si una pagina PDF tiene menos de N chars de texto extraible -> se considera escaneada.
OCR_MIN_CHARS_PER_PAGE = int(os.getenv("OCR_MIN_CHARS_PER_PAGE", "50"))

# --- Descargas ---
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "60"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "SECOP-Tracker/0.1 (local research tool)",
)
