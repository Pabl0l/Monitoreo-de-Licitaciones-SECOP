"""Conversion de propuesta (markdown) a PDF profesional, lista para enviar.

Usa PyMuPDF (fitz.Story) para maquetar HTML/CSS y paginar. Sin servicios pagos.
"""
from __future__ import annotations

import io

import fitz  # PyMuPDF
import markdown as md_lib

# Estilo sobrio corporativo: azul institucional, jerarquia clara, buen interlineado.
_CSS = """
* { font-family: "Helvetica", "Arial", sans-serif; }
body { font-size: 10.5pt; color: #1b1b1b; line-height: 1.55; }
h1 { font-size: 19pt; color: #0b2f5e; margin: 0 0 4pt 0; }
h2 { font-size: 13pt; color: #0b2f5e; margin: 16pt 0 4pt 0;
     border-bottom: 1px solid #cdd6e4; padding-bottom: 3pt; }
h3 { font-size: 11pt; color: #22426e; margin: 12pt 0 2pt 0; }
p  { margin: 4pt 0; text-align: justify; }
ul, ol { margin: 4pt 0 4pt 16pt; }
li { margin: 2pt 0; }
strong { color: #0b2f5e; }
hr { border: none; border-top: 1px solid #cdd6e4; margin: 10pt 0; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; }
td, th { border: 1px solid #c8c8c8; padding: 4pt 6pt; font-size: 10pt; }
th { background: #eef2f8; color: #0b2f5e; text-align: left; }
"""

_MARGINS = (50, 55, 50, 60)  # left, top, right, bottom (pt)


def _encabezado_html(empresa: str, contacto: str) -> str:
    """Membrete simple con el nombre del oferente y su linea de contacto."""
    if not empresa and not contacto:
        return ""
    emp = f'<div style="font-size:12pt;color:#0b2f5e;"><strong>{empresa}</strong></div>' if empresa else ""
    con = f'<div style="font-size:8.5pt;color:#555;">{contacto}</div>' if contacto else ""
    return f'<div style="margin-bottom:8pt;">{emp}{con}<hr/></div>'


def markdown_a_pdf(md_text: str, empresa: str = "", contacto: str = "") -> bytes:
    """Convierte markdown -> PDF (bytes A4). Membrete opcional con datos del oferente."""
    cuerpo = md_lib.markdown(
        md_text or "", extensions=["extra", "sane_lists", "nl2br"]
    )
    html_doc = (
        f"<html><head><style>{_CSS}</style></head><body>"
        f"{_encabezado_html(empresa, contacto)}{cuerpo}"
        f"</body></html>"
    )

    buf = io.BytesIO()
    writer = fitz.DocumentWriter(buf)
    story = fitz.Story(html=html_doc)
    media = fitz.paper_rect("a4")
    ml, mt, mr, mb = _MARGINS
    where = fitz.Rect(ml, mt, media.width - mr, media.height - mb)

    more = 1
    while more:
        dev = writer.begin_page(media)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
    writer.close()
    return buf.getvalue()
