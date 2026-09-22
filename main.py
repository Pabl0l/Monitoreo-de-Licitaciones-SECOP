"""CLI orquestador. Ejecuta pasos del pipeline manualmente o todo junto.

Uso:
    python main.py init                 # crea la base de datos
    python main.py scrape [--rows 100]  # trae procesos SECOP
    python main.py download             # descarga documentos
    python main.py process              # OCR + LLM + metricas
    python main.py all [--rows 100]     # pipeline completo
"""
import argparse

from db.database import init_db
from pipeline import run_all, step_download, step_process, step_scrape
from utils.logging_conf import get_logger

log = get_logger("main")


def main() -> None:
    parser = argparse.ArgumentParser(description="SECOP Tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")
    s = sub.add_parser("scrape")
    s.add_argument("--rows", type=int, default=None)
    sub.add_parser("download")
    sub.add_parser("process")
    a = sub.add_parser("all")
    a.add_argument("--rows", type=int, default=None)

    args = parser.parse_args()

    if args.cmd == "init":
        init_db()
        log.info("DB inicializada")
    elif args.cmd == "scrape":
        log.info("scrape -> %d procesos", step_scrape(args.rows))
    elif args.cmd == "download":
        log.info("download -> %d docs", step_download())
    elif args.cmd == "process":
        log.info("process -> %d procesados", step_process())
    elif args.cmd == "all":
        log.info("pipeline completo: %s", run_all(args.rows))


if __name__ == "__main__":
    main()
