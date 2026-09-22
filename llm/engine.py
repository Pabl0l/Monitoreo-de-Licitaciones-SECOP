"""Dispatcher de motor LLM. Selecciona backend segun config.LLM_ENGINE.

Expone la misma firma que ollama_client (is_available / generate / parse_json)
para que propuesta.py y extractor.py no dependan de un backend concreto.

Backends:
- "deepseek": Playwright sobre chat.deepseek.com (sin API key).
- "ollama":   LLM local via HTTP.
"""
from __future__ import annotations

from config import LLM_ENGINE
from llm import ollama_client
from utils.logging_conf import get_logger

log = get_logger(__name__)

_JSON_HINT = (
    "\n\nIMPORTANTE: responde UNICAMENTE con JSON valido, sin texto antes "
    "ni despues, sin bloques de codigo markdown."
)


def is_available() -> bool:
    if LLM_ENGINE == "deepseek":
        from llm import deepseek_playwright

        return deepseek_playwright.is_available()
    return ollama_client.is_available()


def generate(
    prompt: str,
    system: str = "",
    json_mode: bool = False,
    model: str | None = None,
) -> str:
    """Genera texto con el backend activo. '' si falla."""
    if LLM_ENGINE == "deepseek":
        from llm import deepseek_playwright

        # El chat web no tiene modo JSON nativo: se pide por prompt.
        if json_mode:
            prompt = prompt + _JSON_HINT
        return deepseek_playwright.generate(prompt, system=system, model=model)
    return ollama_client.generate(
        prompt, system=system, json_mode=json_mode, model=model
    )


def parse_json(text: str) -> dict:
    """Parseo defensivo de JSON (reutiliza el de ollama_client)."""
    return ollama_client.parse_json(text)
