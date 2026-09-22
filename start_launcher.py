"""Lanzador de un solo clic para SECOP Tracker.

Compilado a start.exe con PyInstaller (--noconsole). No bundlea Streamlit:
invoca el interprete del .venv del proyecto, asi evita el empaquetado pesado
de Streamlit y mantiene el exe minimo. Abre el dashboard en el navegador.
"""
import os
import socket
import subprocess
import sys
import time
import webbrowser

PORT = 8501
HOST = "localhost"


def base_dir() -> str:
    """Carpeta del proyecto = donde vive el exe (o el script en dev)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def venv_pythonw(root: str) -> str:
    """pythonw.exe del venv (sin ventana de consola)."""
    return os.path.join(root, ".venv", "Scripts", "pythonw.exe")


def port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0


def main() -> None:
    root = base_dir()
    python = venv_pythonw(root)
    app = os.path.join(root, "app.py")

    if not os.path.exists(python):
        python = os.path.join(root, ".venv", "Scripts", "python.exe")
    if not os.path.exists(python) or not os.path.exists(app):
        # Sin venv/app no hay nada que lanzar.
        return

    # Si ya esta corriendo, solo abre el navegador.
    if not port_open(HOST, PORT):
        creationflags = 0x08000000  # CREATE_NO_WINDOW
        subprocess.Popen(
            [python, "-m", "streamlit", "run", app,
             f"--server.port={PORT}", "--server.headless=true"],
            cwd=root,
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Espera a que el servidor levante (max ~30s) y abre el navegador.
    for _ in range(60):
        if port_open(HOST, PORT):
            break
        time.sleep(0.5)

    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    main()
