"""Cliente Ollama local via HTTP. Sin SDK pago. Soporta modo JSON."""
import json

import httpx

from config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL
from utils.logging_conf import get_logger

log = get_logger(__name__)


def is_available() -> bool:
    """True si Ollama responde."""
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except httpx.HTTPError:
        return False


def generate(prompt: str, system: str = "", json_mode: bool = False, model: str | None = None) -> str:
    """Llama /api/generate. Devuelve el texto generado ('' si falla)."""
    payload = {
        "model": model or OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    if json_mode:
        payload["format"] = "json"
    try:
        r = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=OLLAMA_TIMEOUT)
        r.raise_for_status()
        return r.json().get("response", "")
    except httpx.HTTPError as exc:
        log.error("ollama generate fallo: %s", exc)
        return ""


def parse_json(text: str) -> dict:
    """Parseo defensivo de JSON devuelto por el modelo."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if 0 <= start < end:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    return {}
