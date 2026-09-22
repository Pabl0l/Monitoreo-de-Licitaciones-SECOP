# SECOP Tracker

App **100% local y gratuita** para monitorear licitaciones públicas (SECOP II), descargar
pliegos, extraer texto (con OCR si están escaneados), detectar requisitos clave con un **LLM
local (Ollama)** y explorar todo en un **dashboard Streamlit**.

> Sin APIs pagas. Sin SaaS. Corre en CPU con 8GB RAM.

## Arquitectura (flujo)

```
SECOP (Socrata open data)
   ↓  scraper/secop_api.py  (+ doc_links.py: requests/BS4 → Playwright fallback)
SQLite (db/)
   ↓  downloader/downloader.py     → guarda PDFs en data/documentos/
OCR (ocr/extract.py)               → PyMuPDF texto · PaddleOCR/Tesseract si escaneado
   ↓
LLM local (llm/) Ollama            → requisitos JSON {experiencia, financiero, personal, equipos}
   ↓
Análisis (analysis/metrics.py)     → n_requisitos, complejidad, % estructurado
   ↓
Streamlit (app.py)
```

## Estructura

```
secop-tracker/
├── config.py            # rutas, modelo Ollama, límites
├── main.py              # CLI: init/scrape/download/process/all
├── app.py               # dashboard Streamlit
├── pipeline.py          # orquestación de pasos
├── scraper/             # secop_api · doc_links · normalizer
├── downloader/          # descarga + registro de PDFs
├── ocr/                 # extracción texto + OCR
├── llm/                 # ollama_client · extractor
├── analysis/            # métricas heurísticas
├── db/                  # database (schema) · repository (CRUD)
├── utils/               # logging
└── data/                # SQLite, PDFs, logs (se crea solo)
```

## 1. Instalar dependencias Python

```bash
cd secop-intelligence-mvp
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium      # solo si usarás el fallback dinámico de documentos
```

> **OCR opcional:** PaddleOCR (`paddleocr`+`paddlepaddle`) es pesado. Si falla la instalación,
> el sistema usa **Tesseract** automáticamente. Para Tesseract instala el binario:
> - Windows: https://github.com/UB-Mannheim/tesseract/wiki (idioma español)
> - Linux: `sudo apt install tesseract-ocr tesseract-ocr-spa`
> Si no necesitas OCR (pliegos con texto), puedes omitir ambos.

## 2. Instalar Ollama + modelo local

```bash
# 1) Instala Ollama: https://ollama.com/download
# 2) Descarga el modelo (preferido, liviano para 8GB):
ollama pull qwen2.5:3b-instruct

# Alternativas (si tienes más RAM / quieres más calidad):
#   ollama pull qwen2.5:7b-instruct
#   ollama pull mistral-small
#   ollama pull gemma3
```

Ollama corre como servicio en `http://localhost:11434`. Verifica: `ollama list`.
Para cambiar de modelo: edita `OLLAMA_MODEL` en `.env` o `config.py`.

## 3. Ejecutar

### Opción A — dashboard (recomendado)

```bash
streamlit run app.py
```

En la barra lateral: **1) Scrapear SECOP → 2) Descargar documentos → 3) OCR + IA**.
Luego filtra y explora procesos, documentos y requisitos.

### Opción B — CLI (scheduler / sin UI)

```bash
python main.py init
python main.py scrape --rows 100
python main.py download
python main.py process
# o todo junto:
python main.py all --rows 100
```

**Scheduler simple:** programa `python main.py all` con el Programador de tareas de Windows
o `cron` en Linux (ej. cada 6h).

## Configuración (`.env` opcional)

| Variable | Default | Para qué |
|----------|---------|----------|
| `OLLAMA_MODEL` | `qwen2.5:3b-instruct` | modelo LLM local |
| `SECOP_MAX_ROWS` | `100` | procesos por corrida (cuida RAM) |
| `SECOP_APP_TOKEN` | — | token gratis Socrata (sube rate-limit) |
| `OCR_ENGINE` | `paddle` | `paddle` o `tesseract` |
| `OCR_MIN_CHARS_PER_PAGE` | `50` | umbral para decidir si una página es escaneada |

## Supuestos de diseño

- **Fuente de datos:** API abierta de SECOP (Socrata, dataset `p6dx-8zbt`) en vez de scraping
  HTML — es gratis, estable y trae los metadatos pedidos (ID, entidad, objeto, valor, fecha).
  Playwright se usa solo como **fallback** para descubrir enlaces a documentos en la página del
  proceso (dinámica).
- **DB:** SQLite (cero configuración, local). El repositorio está aislado en `db/` por si luego
  se migra a PostgreSQL.
- **OCR selectivo:** solo se aplica OCR a páginas sin texto embebido → ahorra CPU.
- **Modelo pequeño por defecto** (3B) para caber en 8GB; subir a 7B si hay RAM.
- **Sin scoring complejo** (por requerimiento): métricas heurísticas transparentes.

## Manejo de errores

- Timeouts y reintentos con backoff en scraping y descargas.
- PDFs corruptos / sin texto → se registran y se omiten sin romper el pipeline.
- Ollama caído → la extracción LLM se omite con aviso (el resto del flujo sigue).
- PaddleOCR no instalado → cae a Tesseract; si tampoco, devuelve texto vacío.

## Criterio de éxito (cumplido)

✅ Corre local sin internet continuo (salvo el fetch SECOP). ✅ Detecta y almacena procesos.
✅ Extrae texto de pliegos (con OCR). ✅ Muestra resultados en Streamlit. ✅ Cero servicios pagos.
