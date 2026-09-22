"""Cliente DeepSeek via Playwright (chat web, sin API key).

Usa un PERFIL PERSISTENTE de Chrome real (no el Chromium empaquetado) para
evitar la deteccion de "navegador no seguro" en el login con Google/DeepSeek y
los problemas de pestanas que no cargan. Las cookies viven en el perfil, asi
que el login se hace una sola vez:

    .venv/Scripts/python.exe -m llm.deepseek_playwright login

Despues `generate()` reutiliza ese perfil headless. Fragil por diseno
(depende del DOM y del login): el resto de la app degrada con gracia cuando
`is_available()` es False.
"""
from __future__ import annotations

import sys
import time

from config import (
    DEEPSEEK_CHANNEL,
    DEEPSEEK_HEADLESS,
    DEEPSEEK_MARKER,
    DEEPSEEK_NAV_TIMEOUT,
    DEEPSEEK_PROFILE_DIR,
    DEEPSEEK_TIMEOUT,
)
from utils.logging_conf import get_logger

log = get_logger(__name__)

CHAT_URL = "https://chat.deepseek.com/"
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Flags anti-deteccion: ocultan que es un navegador controlado.
_LAUNCH_ARGS = ["--disable-blink-features=AutomationControlled"]
_IGNORE_ARGS = ["--enable-automation"]

# Selectores con fallback: DeepSeek cambia el DOM cada tanto.
_INPUT_SELECTORS = ("textarea#chat-input", "textarea[id='chat-input']", "textarea")
_ANSWER_SELECTOR = "div.ds-markdown"
_STOP_SELECTORS = (
    "div[role='button'][aria-label*='Stop']",
    "div[role='button'][aria-label*='Detener']",
)
_POLL_INTERVAL = 1.0          # s entre lecturas del texto
_STABLE_READS = 3             # lecturas iguales seguidas => respuesta terminada
_MIN_ANSWER_CHARS = 1


def is_available() -> bool:
    """True si ya se completo el login (marker presente). No lanza navegador."""
    return DEEPSEEK_MARKER.exists()


def _launch_context(p, headless: bool):
    """Lanza un contexto persistente con Chrome real; cae a Chromium si falla."""
    DEEPSEEK_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    common = dict(
        user_data_dir=str(DEEPSEEK_PROFILE_DIR),
        headless=headless,
        user_agent=_UA,
        args=_LAUNCH_ARGS,
        ignore_default_args=_IGNORE_ARGS,
        viewport={"width": 1280, "height": 860},
    )
    if DEEPSEEK_CHANNEL:
        try:
            return p.chromium.launch_persistent_context(channel=DEEPSEEK_CHANNEL, **common)
        except Exception as exc:  # noqa: BLE001 - canal no instalado, caemos a chromium
            log.warning("deepseek: canal '%s' fallo (%s); uso chromium", DEEPSEEK_CHANNEL, exc)
    return p.chromium.launch_persistent_context(**common)


def login() -> None:
    """Abre Chrome visible para login manual y deja la sesion en el perfil.

    Uso: `.venv/Scripts/python.exe -m llm.deepseek_playwright login`
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        ctx = _launch_context(p, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(CHAT_URL, wait_until="domcontentloaded")
        print("\n=== Inicia sesion en DeepSeek en la ventana abierta ===")
        print("Sugerencia: usa correo + contrasena (el login con Google a veces")
        print("bloquea navegadores automatizados). Si ya tienes cuenta, entra normal.")
        print("Cuando veas el chat listo para escribir, vuelve aqui y presiona ENTER...")
        input()
        DEEPSEEK_MARKER.parent.mkdir(parents=True, exist_ok=True)
        DEEPSEEK_MARKER.write_text("ok", encoding="utf-8")
        ctx.close()
        print(f"Sesion guardada en el perfil {DEEPSEEK_PROFILE_DIR}")


def _find_input(page):
    """Primer selector de input que exista en la pagina."""
    for sel in _INPUT_SELECTORS:
        loc = page.locator(sel).first
        try:
            loc.wait_for(state="visible", timeout=5000)
            return loc
        except Exception:  # noqa: BLE001 - probamos el siguiente selector
            continue
    return None


def _generating(page) -> bool:
    """True mientras exista el boton de Stop (respuesta en curso)."""
    for sel in _STOP_SELECTORS:
        try:
            if page.locator(sel).first.is_visible():
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _last_answer_text(page) -> str:
    """innerText del ultimo bloque de respuesta (markdown)."""
    answers = page.locator(_ANSWER_SELECTOR)
    try:
        n = answers.count()
    except Exception:  # noqa: BLE001
        return ""
    if n == 0:
        return ""
    try:
        return (answers.nth(n - 1).inner_text() or "").strip()
    except Exception:  # noqa: BLE001
        return ""


def _wait_for_answer(page, deadline: float) -> str:
    """Espera a que la respuesta deje de crecer y devuelve su texto."""
    last = ""
    stable = 0
    while time.monotonic() < deadline:
        time.sleep(_POLL_INTERVAL)
        text = _last_answer_text(page)
        if text and text == last:
            stable += 1
            # Estable y ya no esta generando => listo.
            if stable >= _STABLE_READS and not _generating(page):
                return text
        else:
            stable = 0
            last = text
    return last


def generate(prompt: str, system: str = "", model: str | None = None) -> str:
    """Envia un mensaje al chat y devuelve la respuesta ('' si falla).

    `model` se ignora (lo define la UI); se mantiene por compatibilidad con
    la firma de ollama_client.generate.
    """
    if not is_available():
        log.warning("deepseek: sin login (corre 'login' primero)")
        return ""

    from playwright.sync_api import sync_playwright

    full_prompt = f"{system}\n\n{prompt}".strip() if system else prompt

    try:
        with sync_playwright() as p:
            ctx = _launch_context(p, headless=DEEPSEEK_HEADLESS)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.set_default_timeout(DEEPSEEK_NAV_TIMEOUT * 1000)
            page.goto(CHAT_URL, wait_until="domcontentloaded")

            box = _find_input(page)
            if box is None:
                log.error("deepseek: input de chat no encontrado (login vencido?)")
                ctx.close()
                return ""

            box.click()
            box.fill(full_prompt)
            box.press("Enter")

            deadline = time.monotonic() + DEEPSEEK_TIMEOUT
            answer = _wait_for_answer(page, deadline)
            ctx.close()

            if len(answer) < _MIN_ANSWER_CHARS:
                log.warning("deepseek: respuesta vacia")
            return answer
    except Exception as exc:  # noqa: BLE001 - playwright lanza varios tipos
        log.error("deepseek generate fallo: %s", exc)
        return ""


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        login()
    else:
        print("Uso: python -m llm.deepseek_playwright login")
