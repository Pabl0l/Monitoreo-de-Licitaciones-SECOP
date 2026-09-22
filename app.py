"""Dashboard Streamlit — SECOP Tracker.

Diseno liquid glass premium. Paleta blanca/negra/azul. Sin emojis.
Cards = contenedores reales estilizados como vidrio (botones nativos dentro).

Ejecutar:  streamlit run app.py
"""
import streamlit as st

from analysis import relevancia
from analysis import perfil_ia
from db import repository as repo
from db.database import init_db
from config import LLM_ENGINE
from llm import engine, propuesta
from pipeline import step_scrape
from utils import pdf
from ui.components import (
    CSS, brand_html, card_inner, field_label, form_tip, hero_html, swipe_html,
)

st.set_page_config(page_title="SECOP Tracker", layout="wide", initial_sidebar_state="expanded")
init_db()
st.markdown(CSS, unsafe_allow_html=True)

KEYWORDS = [
    "ciberseguridad", "software", "desarrollo", "redes", "datacenter", "nube",
    "consultoria", "interventoria", "mantenimiento", "obra", "infraestructura",
    "suministro", "dotacion", "tecnologia", "telecomunicaciones", "datos",
    "seguridad informatica", "soporte tecnico", "capacitacion", "vigilancia",
]
DEFAULT_SCRAPE_ROWS = 100   # procesos que trae el autoscrape inicial si la base esta vacia
RESULT_LIMIT = 90           # tope de resultados por busqueda (se cargan de a PAGE_SIZE)
PAGE_SIZE = 12              # cards visibles por pagina (carga incremental al hacer scroll)
MATCH_LIMIT = 100           # cola de pendientes en modo match


# ---------------- Cargas cacheadas ----------------
@st.cache_data(ttl=300, show_spinner=False)
def entidades_distintas() -> list[str]:
    return repo.distinct_values("entidad")


@st.cache_data(ttl=300, show_spinner=False)
def valores_distintos(columna: str) -> list[str]:
    return repo.distinct_values(columna)


@st.cache_data(ttl=120, show_spinner=False)
def buscar(entidad, ciudad, departamento, estado, texto, vmin, vmax, limit) -> list[dict]:
    """Busqueda cacheada por combinacion de filtros (acelera reruns repetidos)."""
    return repo.list_procesos(
        entidad=entidad, ciudad=ciudad, departamento=departamento, estado=estado,
        texto=texto, valor_min=vmin, valor_max=vmax, limit=limit,
    )


@st.cache_data(ttl=300, show_spinner=False)
def cargar_perfil() -> dict | None:
    return repo.get_perfil()


@st.cache_data(ttl=30, show_spinner=False)
def llm_disponible() -> bool:
    """Estado del motor LLM cacheado: evita revalidar en cada rerun/cambio de vista."""
    return engine.is_available()


@st.cache_data(ttl=300, show_spinner=False)
def autoscrape_si_vacio(keywords: tuple[str, ...]) -> int:
    """Primer llenado de la base. Si hay perfil, filtra por su sector en SECOP."""
    if repo.count_procesos() > 0:
        return 0
    return step_scrape(DEFAULT_SCRAPE_ROWS, keywords=list(keywords) or None)


def actualizar_licitaciones(perfil: dict | None) -> int:
    """Trae de SECOP licitaciones del sector del perfil y refresca los caches."""
    terms = relevancia.terminos_scrape(perfil)
    n = step_scrape(DEFAULT_SCRAPE_ROWS, keywords=terms or None)
    buscar.clear()
    valores_distintos.clear()
    entidades_distintas.clear()
    autoscrape_si_vacio.clear()
    return n


@st.cache_data(ttl=600, show_spinner=False)
def resumen_cacheado(proceso_id: int, _llm_ok: bool) -> str:
    """Resumen LLM por proceso. _llm_ok invalida el cache si cambia el estado."""
    proc = repo.get_proceso(proceso_id)
    if not proc:
        return ""
    return propuesta.resumir(proc, repo.list_requisitos(proceso_id))


st.session_state.setdefault("query", "")
st.session_state.setdefault("swipe_idx", 0)
st.session_state.setdefault("detalle_id", None)


# ---------------- Filtros (viven en la barra lateral) ----------------
def filtros_sidebar() -> dict:
    """Renderiza todos los filtros en el sidebar y devuelve la seleccion."""
    st.markdown('<div class="lt-side-label">Buscar</div>', unsafe_allow_html=True)
    actual = st.session_state["query"]
    opciones = KEYWORDS if not actual or actual in KEYWORDS else [actual, *KEYWORDS]
    query = st.selectbox(
        "Buscar", options=opciones,
        index=opciones.index(actual) if actual in opciones else None,
        placeholder="Escribe o elige un sector...",
        accept_new_options=True, label_visibility="collapsed",
    )
    query = query or ""
    if query != st.session_state["query"]:
        st.session_state["query"] = query
        st.rerun()

    st.markdown('<div class="lt-side-label">Ubicacion</div>', unsafe_allow_html=True)
    ciudad = st.selectbox("Ciudad", ["Todas"] + valores_distintos("ciudad"))
    departamento = st.selectbox("Departamento", ["Todos"] + valores_distintos("departamento"))

    st.markdown('<div class="lt-side-label">Proceso</div>', unsafe_allow_html=True)
    estado = st.selectbox("Estado", ["Todos"] + valores_distintos("estado"))
    entidad = st.selectbox("Entidad", ["Todas"] + entidades_distintas())

    with st.expander("Valor (COP)"):
        valor_min = st.number_input("Minimo", 0, step=1_000_000, value=0)
        valor_max = st.number_input("Maximo", 0, step=1_000_000, value=0)

    perfil = cargar_perfil()
    keywords = relevancia.keywords_de_perfil(perfil)
    priorizar, solo, acertadas = True, False, False
    if keywords:
        st.markdown('<div class="lt-side-label">Mi empresa</div>', unsafe_allow_html=True)
        priorizar = st.toggle("Priorizar mi sector", value=True)
        solo = st.toggle("Solo mi sector", value=False)
        acertadas = st.toggle(
            "Solo más acertadas", value=False,
            help="Solo licitaciones con coincidencia fuerte (en el objeto) con tu perfil.",
        )

    return {
        "ciudad": ciudad, "departamento": departamento, "estado": estado, "entidad": entidad,
        "valor_min": valor_min, "valor_max": valor_max,
        "perfil": perfil, "keywords": keywords, "priorizar": priorizar,
        "solo": solo, "acertadas": acertadas,
    }


# Navegacion: nombre + icono material (SVG nativo de Streamlit).
NAV = [
    ("Explorar", ":material/travel_explore:"),
    ("Match", ":material/bolt:"),
    ("Favoritos", ":material/bookmark:"),
    ("Perfil", ":material/apartment:"),
]


# El sitio funciona a partir del perfil: sin perfil, todo se bloquea menos Perfil.
def perfil_creado() -> bool:
    """True si ya existe un perfil minimo (nombre + sector o palabras clave)."""
    p = cargar_perfil()
    return bool(p and (p.get("nombre") or "").strip()
                and ((p.get("sector") or "").strip() or (p.get("palabras_clave") or "").strip()))


# ---------------- Sidebar ----------------
st.session_state.setdefault("vista", "Explorar")
_perfil_ok = perfil_creado()
if not _perfil_ok:
    st.session_state["vista"] = "Perfil"  # fuerza onboarding

with st.sidebar:
    st.markdown(brand_html(), unsafe_allow_html=True)
    # Navegacion en rejilla 2x2: solo iconos; el texto aparece al pasar el cursor.
    for _fila in (NAV[:2], NAV[2:]):
        for _col, (_nombre, _icono) in zip(st.columns(2), _fila):
            with _col:
                _bloqueado = (not _perfil_ok) and _nombre != "Perfil"
                if st.button(
                    _nombre, icon=_icono, key=f"nav_{_nombre}", use_container_width=True,
                    type="primary" if st.session_state["vista"] == _nombre else "secondary",
                    disabled=_bloqueado,
                    help="Crea tu perfil primero" if _bloqueado else None,
                ):
                    st.session_state["vista"] = _nombre
                    st.rerun()
    vista = st.session_state["vista"]
    st.markdown(
        f'<p class="lt-side-count">{repo.count_procesos()} licitaciones en base</p>',
        unsafe_allow_html=True,
    )
    filtros = filtros_sidebar() if (_perfil_ok and vista in ("Explorar", "Match")) else {}

autoscrape_si_vacio(tuple(relevancia.terminos_scrape(cargar_perfil())))
favs = repo.favorito_ids()


# ---------------- Dialog: detalle + propuesta ----------------
@st.dialog("Detalle de la licitacion", width="large")
def dialog_detalle(proc: dict):
    st.markdown(f"### {(proc.get('objeto') or 'Sin objeto')[:160]}")
    meta = " · ".join(
        x for x in (proc.get("entidad"), proc.get("ciudad"), proc.get("departamento")) if x
    )
    st.caption(meta or "Sin metadatos")

    llm_ok = llm_disponible()
    if not llm_ok:
        if LLM_ENGINE == "deepseek":
            st.warning(
                "DeepSeek sin sesion. Inicia sesion una vez con "
                "`.venv/Scripts/python.exe -m llm.deepseek_playwright login` "
                "para resumir y generar propuestas."
            )
        else:
            st.warning("Ollama no esta activo. Inicialo con `ollama serve` para resumir y generar propuestas.")
    else:
        with st.spinner("Resumiendo licitacion (DeepSeek)..."):
            resumen = resumen_cacheado(proc["id"], llm_ok)
        st.markdown(resumen or "_No se pudo generar el resumen._")

    st.markdown("---")
    _perfil = cargar_perfil() or {}
    empresa = st.text_input(
        "Tu empresa (opcional)", value=_perfil.get("nombre", ""),
        placeholder="Nombre del oferente para personalizar la propuesta",
    )
    # Avisa si faltan datos de contacto: la propuesta sale con marcadores [completar].
    _faltantes = [
        etq for etq, campo in (
            ("NIT", "nit"), ("representante legal", "representante"),
            ("correo", "correo"), ("teléfono", "telefono"), ("dirección", "direccion"),
        ) if not (_perfil.get(campo) or "").strip()
    ]
    if _faltantes:
        st.caption(
            "Para una propuesta lista para enviar, completa en **Perfil**: "
            + ", ".join(_faltantes) + "."
        )
    gen = st.button(
        "Generar propuesta profesional", type="primary",
        use_container_width=True, disabled=not llm_ok,
    )
    prop_key = f"propuesta_{proc['id']}"
    _motor = "DeepSeek" if LLM_ENGINE == "deepseek" else "Ollama local (CPU)"
    if gen:
        oferente = {**_perfil, "nombre": (empresa.strip() or _perfil.get("nombre", ""))}
        with st.spinner(f"Redactando propuesta ({_motor})..."):
            st.session_state[prop_key] = propuesta.generar_propuesta(
                proc, oferente, repo.list_requisitos(proc["id"])
            )

    if st.session_state.get(prop_key):
        st.markdown("---")
        st.markdown(st.session_state[prop_key])
        _contacto = " · ".join(
            x for x in (
                f"NIT {_perfil.get('nit')}" if _perfil.get("nit") else None,
                _perfil.get("correo"), _perfil.get("telefono"),
                _perfil.get("direccion"),
            ) if x
        )
        _nombre_emp = empresa.strip() or _perfil.get("nombre", "")
        try:
            pdf_bytes = pdf.markdown_a_pdf(
                st.session_state[prop_key], empresa=_nombre_emp, contacto=_contacto
            )
            st.download_button(
                "Descargar propuesta (PDF)", pdf_bytes,
                file_name=f"propuesta_{proc['id']}.pdf", mime="application/pdf",
                type="primary", use_container_width=True,
            )
        except Exception as exc:  # noqa: BLE001 - no romper el modal por el PDF
            st.warning(f"No se pudo generar el PDF ({exc}). Descarga en Markdown abajo.")
        st.download_button(
            "Descargar en Markdown (.md)", st.session_state[prop_key],
            file_name=f"propuesta_{proc['id']}.md", use_container_width=True,
        )

    cerrar, secop = st.columns(2)
    if cerrar.button("Cerrar", key="dlg_cerrar", use_container_width=True):
        st.session_state["detalle_id"] = None
        st.rerun()
    if proc.get("url"):
        secop.link_button("Abrir en SECOP", proc["url"], use_container_width=True)


# ---------------- Render de cards (grid alineada, carga incremental) ----------------
def render_grid(procesos: list[dict], key_prefix: str, cols_per_row: int = 3):
    """Renderiza cards. `key_prefix` evita colisiones de key entre vistas/tabs.

    Solo dibuja los primeros N (PAGE_SIZE); el resto se carga con 'Cargar mas'
    para que el primer render sea rapido (menos widgets en pantalla).
    """
    if not procesos:
        st.info("Sin resultados. Ajusta los filtros del panel izquierdo.")
        return

    sk = f"shown_{key_prefix}"
    shown = st.session_state.setdefault(sk, PAGE_SIZE)
    visibles = procesos[:shown]

    for i in range(0, len(visibles), cols_per_row):
        fila = visibles[i : i + cols_per_row]
        cols = st.columns(cols_per_row, gap="medium")
        for col, proc in zip(cols, fila):
            pid = proc["id"]
            with col, st.container(border=True):
                es_fav = pid in favs
                st.markdown(card_inner(proc, es_fav), unsafe_allow_html=True)
                if st.button(
                    "Ver detalle y propuesta", key=f"det_{key_prefix}_{pid}",
                    use_container_width=True, type="primary",
                ):
                    st.session_state["detalle_id"] = pid
                    st.rerun()
                b1, b2 = st.columns(2)
                if b1.button(
                    "Guardado" if es_fav else "Guardar",
                    key=f"fav_{key_prefix}_{pid}", use_container_width=True,
                ):
                    repo.toggle_favorito(pid)
                    st.rerun()
                if proc.get("url"):
                    b2.link_button("Ver SECOP", proc["url"], use_container_width=True)

    restantes = len(procesos) - shown
    if restantes > 0:
        if st.button(
            f"Cargar mas ({restantes})", key=f"more_{key_prefix}",
            use_container_width=True,
        ):
            st.session_state[sk] = shown + PAGE_SIZE
            st.rerun()


# ---------------- Filtro + ranking compartido (Explorar y Match) ----------------
def aplicar_filtros(f: dict, limit: int, excluir_ids: set[int] | None = None):
    """Busca con los filtros del sidebar, excluye ids opcionales y rankea por perfil.

    Devuelve (procesos, n_relevantes).
    """
    procesos = buscar(
        None if f["entidad"] == "Todas" else f["entidad"],
        None if f["ciudad"] == "Todas" else f["ciudad"],
        None if f["departamento"] == "Todos" else f["departamento"],
        None if f["estado"] == "Todos" else f["estado"],
        st.session_state["query"] or None,
        f["valor_min"] or None,
        f["valor_max"] or None,
        limit,
    )
    if excluir_ids:
        procesos = [p for p in procesos if p["id"] not in excluir_ids]

    n_rel = 0
    if f["keywords"]:
        procesos, n_rel = relevancia.anotar_relevancia(procesos, f["perfil"])
        if f.get("acertadas"):
            procesos = [p for p in procesos if p.get("_acertada")]
        elif f["solo"]:
            procesos = [p for p in procesos if p["_relevante"]]
        if f["priorizar"]:
            procesos = relevancia.ordenar_por_relevancia(procesos)
    return procesos, n_rel


def chips_activos_html(f: dict) -> str:
    activos = [
        f'"{st.session_state["query"]}"' if st.session_state["query"] else None,
        f"Ciudad: {f['ciudad']}" if f["ciudad"] != "Todas" else None,
        f"Depto: {f['departamento']}" if f["departamento"] != "Todos" else None,
        f"Estado: {f['estado']}" if f["estado"] != "Todos" else None,
        f"Entidad: {f['entidad']}" if f["entidad"] != "Todas" else None,
        "Solo mi sector" if f["keywords"] and f["solo"] else None,
    ]
    chips = "".join(f'<span class="lt-chip">{c}</span>' for c in activos if c)
    return f'<div class="lt-chips">{chips}</div>' if chips else ""


# ===================== VISTA: EXPLORAR =====================
def vista_explorar(f: dict):
    st.markdown(hero_html("Licitaciones", "SECOP II — datos abiertos en vivo"),
                unsafe_allow_html=True)
    st.markdown(chips_activos_html(f), unsafe_allow_html=True)

    if f.get("keywords"):
        _, c_act = st.columns([3, 1])
        if c_act.button(
            "Actualizar de mi sector", icon=":material/refresh:",
            use_container_width=True,
            help="Trae de SECOP nuevas licitaciones afines a tu perfil.",
        ):
            with st.spinner("Buscando licitaciones de tu sector en SECOP..."):
                n = actualizar_licitaciones(f["perfil"])
            st.toast(f"{n} licitaciones de tu sector cargadas.")
            st.rerun()

    with st.spinner("Cargando licitaciones..."):
        procesos, n_rel = aplicar_filtros(f, RESULT_LIMIT)
    extra = (
        f' · <b style="color:#7BE6B0">{n_rel}</b> para tu empresa'
        if f["keywords"] and not f["solo"]
        else ""
    )
    st.markdown(
        f'<p style="color:rgba(244,247,252,.6);font-size:13px;margin:6px 0 18px">'
        f'<b style="color:#fff">{len(procesos)}</b> resultados{extra}</p>',
        unsafe_allow_html=True,
    )
    render_grid(procesos, key_prefix="exp")


# ===================== VISTA: MATCH =====================
def vista_match(f: dict):
    st.markdown(hero_html("Modo match", "Decide rapido: te interesa o no", "spark"),
                unsafe_allow_html=True)
    st.markdown(chips_activos_html(f), unsafe_allow_html=True)

    # Misma logica de filtros del sidebar; excluye lo ya decidido y prioriza por perfil.
    with st.spinner("Cargando cola..."):
        pendientes, _ = aplicar_filtros(f, MATCH_LIMIT, excluir_ids=repo.decision_ids())
    if not pendientes:
        st.success("No hay licitaciones pendientes con estos filtros. Ajustalos o revisa Favoritos.")
        if st.button("Reiniciar decisiones"):
            repo.reset_decisiones()
            st.session_state["swipe_idx"] = 0
            st.rerun()
        return

    proc = pendientes[st.session_state["swipe_idx"] % len(pendientes)]
    st.markdown(swipe_html(proc), unsafe_allow_html=True)
    st.write("")

    _, c_no, c_si, _ = st.columns([1.4, 1, 1, 1.4])
    if c_no.button("Descartar", key="sw_no", use_container_width=True):
        repo.set_decision(proc["id"], "descartar")
        st.session_state["swipe_idx"] += 1
        st.rerun()
    if c_si.button("Match", key="sw_si", type="primary", use_container_width=True):
        repo.set_decision(proc["id"], "match")
        if proc["id"] not in favs:
            repo.toggle_favorito(proc["id"])
        st.session_state["swipe_idx"] += 1
        st.rerun()
    st.markdown(
        f'<p style="text-align:center;color:rgba(244,247,252,.5);font-size:12px;margin-top:14px">'
        f'{len(pendientes)} pendientes</p>', unsafe_allow_html=True,
    )


# ===================== VISTA: FAVORITOS =====================
def vista_favoritos():
    st.markdown(hero_html("Favoritos y matches", "Licitaciones que guardaste", "bookmark"),
                unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Favoritos", "Matches"])
    with tab1, st.spinner("Cargando favoritos..."):
        render_grid(repo.list_favoritos(), key_prefix="fav")
    with tab2, st.spinner("Cargando matches..."):
        render_grid(repo.list_matches(), key_prefix="match")


# ===================== VISTA: PERFIL =====================
def vista_perfil():
    st.markdown(
        hero_html("Perfil de la empresa", "Define tu sector para priorizar licitaciones afines",
                  "building"),
        unsafe_allow_html=True,
    )
    perfil = repo.get_perfil() or {}

    if not perfil_creado():
        st.info(
            "Bienvenido. Para empezar, crea el perfil de tu empresa: "
            "es la base con la que el sitio prioriza y filtra las licitaciones. "
            "Completa al menos **nombre** y **sector** (o palabras clave) y guarda."
        )

    with st.form("form_perfil"):
        st.markdown(
            form_tip("Cuéntanos quién eres: cuanto más completes, mejor priorizamos tus licitaciones."),
            unsafe_allow_html=True,
        )

        st.markdown(field_label("user", "Nombre de la empresa"), unsafe_allow_html=True)
        nombre = st.text_input(
            "Nombre de la empresa", value=perfil.get("nombre", ""),
            placeholder="Mi Empresa S.A.S.", label_visibility="collapsed",
        )

        st.markdown(
            field_label("briefcase", "Sector", "¿a qué se dedica?"),
            unsafe_allow_html=True,
        )
        sector = st.text_input(
            "Sector", value=perfil.get("sector", ""),
            placeholder="Tecnología, ciberseguridad, construcción...",
            label_visibility="collapsed",
        )

        st.markdown(
            field_label("key", "Palabras clave", "separadas por coma"),
            unsafe_allow_html=True,
        )
        palabras = st.text_area(
            "Palabras clave", value=perfil.get("palabras_clave", ""),
            placeholder="software, redes, seguridad informática, datacenter",
            help="Se usan para detectar licitaciones relacionadas con tu empresa.",
            label_visibility="collapsed", height=80,
        )

        st.markdown('<hr class="ff-sep"/>', unsafe_allow_html=True)

        cp1, cp2 = st.columns(2)
        with cp1:
            st.markdown(field_label("pin", "Ciudad", "opcional"), unsafe_allow_html=True)
            ciudad = st.text_input(
                "Ciudad", value=perfil.get("ciudad", ""),
                placeholder="Bogotá", label_visibility="collapsed",
            )
        with cp2:
            st.markdown(field_label("layers", "Departamento", "opcional"), unsafe_allow_html=True)
            departamento = st.text_input(
                "Departamento", value=perfil.get("departamento", ""),
                placeholder="Cundinamarca", label_visibility="collapsed",
            )

        st.markdown('<hr class="ff-sep"/>', unsafe_allow_html=True)
        st.markdown(
            field_label("user", "Datos de contacto",
                        "se usan en la propuesta lista para enviar"),
            unsafe_allow_html=True,
        )
        cc1, cc2 = st.columns(2)
        with cc1:
            representante = st.text_input(
                "Representante legal", value=perfil.get("representante", ""),
                placeholder="Nombre del representante legal",
            )
            correo = st.text_input(
                "Correo", value=perfil.get("correo", ""),
                placeholder="contacto@miempresa.com",
            )
            direccion = st.text_input(
                "Dirección", value=perfil.get("direccion", ""),
                placeholder="Calle 00 # 00-00, oficina 000",
            )
        with cc2:
            nit = st.text_input(
                "NIT", value=perfil.get("nit", ""),
                placeholder="900.000.000-0",
            )
            telefono = st.text_input(
                "Teléfono", value=perfil.get("telefono", ""),
                placeholder="+57 300 000 0000",
            )
            sitio_web = st.text_input(
                "Sitio web", value=perfil.get("sitio_web", ""),
                placeholder="www.miempresa.com",
            )

        st.markdown('<hr class="ff-sep"/>', unsafe_allow_html=True)
        st.markdown(
            field_label("doc", "Descripción", "opcional"),
            unsafe_allow_html=True,
        )
        descripcion = st.text_area(
            "Descripción", value=perfil.get("descripcion", ""),
            placeholder="Qué hace la empresa, experiencia, diferenciales...",
            label_visibility="collapsed", height=100,
        )
        guardar = st.form_submit_button(
            "Guardar perfil", type="primary", use_container_width=True
        )

    if guardar:
        repo.save_perfil({
            "nombre": nombre, "sector": sector, "palabras_clave": palabras,
            "ciudad": ciudad, "departamento": departamento, "descripcion": descripcion,
            "nit": nit, "representante": representante, "correo": correo,
            "telefono": telefono, "direccion": direccion, "sitio_web": sitio_web,
        })
        cargar_perfil.clear()
        with st.spinner("Buscando licitaciones de tu sector en SECOP..."):
            actualizar_licitaciones(repo.get_perfil())
        st.success("Perfil guardado. Cargamos licitaciones de tu sector; revisa Explorar.")
        st.rerun()  # desbloquea el resto del sitio de inmediato

    # ---- Mejora del perfil con IA (DeepSeek) ----
    st.markdown('<hr class="ff-sep"/>', unsafe_allow_html=True)
    perfil_actual = repo.get_perfil() or {}
    llm_ok = llm_disponible()
    tiene_datos = bool((perfil_actual.get("sector") or perfil_actual.get("descripcion")
                        or perfil_actual.get("palabras_clave")))

    st.markdown(
        field_label("spark", "Afinar con IA",
                    "DeepSeek expande tus términos y filtra las más acertadas"),
        unsafe_allow_html=True,
    )
    if not llm_ok:
        st.warning(
            "DeepSeek sin sesión. Inicia sesión una vez con "
            "`.venv/Scripts/python.exe -m llm.deepseek_playwright login`."
        )
    mejorar = st.button(
        "Mejorar perfil con DeepSeek", type="primary", use_container_width=True,
        disabled=not (llm_ok and tiene_datos),
        help=None if tiene_datos else "Completa y guarda al menos sector o descripción.",
    )
    if mejorar:
        with st.spinner("DeepSeek analizando tu empresa..."):
            res = perfil_ia.mejorar_perfil(perfil_actual)
        if res:
            repo.save_perfil_ia(res["palabras_clave_ia"], res["descripcion_ia"])
            cargar_perfil.clear()
            with st.spinner("Trayendo licitaciones con los nuevos términos..."):
                actualizar_licitaciones(repo.get_perfil())
            st.success("Perfil mejorado. Usa el filtro 'Solo más acertadas' en Explorar.")
            st.rerun()
        else:
            st.error("No se pudo mejorar el perfil (DeepSeek no respondió o sesión vencida).")

    if perfil_actual.get("descripcion_ia"):
        st.markdown('<div class="lt-side-label">Enfoque sugerido (IA)</div>',
                    unsafe_allow_html=True)
        st.markdown(perfil_actual["descripcion_ia"])

    # ---- Términos activos: clic para añadirlos a palabras clave ----
    perfil_now = repo.get_perfil() or {}
    raw_user = [t.strip() for t in (perfil_now.get("palabras_clave") or "").split(",") if t.strip()]
    norm_user = {relevancia._norm(t) for t in raw_user}

    # Candidatos (grafía original) desde palabras del usuario + IA + sector; dedup por forma normalizada.
    candidatos: list[str] = []
    vistos: set[str] = set()
    for campo in ("palabras_clave", "palabras_clave_ia"):
        for t in (perfil_now.get(campo) or "").split(","):
            t, n = t.strip(), relevancia._norm(t)
            if t and n not in vistos:
                vistos.add(n)
                candidatos.append(t)
    if perfil_now.get("sector"):
        s, n = perfil_now["sector"].strip(), relevancia._norm(perfil_now["sector"])
        if s and n not in vistos:
            vistos.add(n)
            candidatos.append(s)

    if candidatos:
        st.markdown('<div class="lt-side-label">Términos activos</div>', unsafe_allow_html=True)
        st.caption("Haz clic en un término para añadirlo a tus palabras clave. "
                   "Los atenuados ya están incluidos.")
        cols = st.columns(3)
        for i, term in enumerate(candidatos):
            ya_incluido = relevancia._norm(term) in norm_user
            with cols[i % 3]:
                if st.button(
                    term, key=f"kwchip_{i}", use_container_width=True,
                    disabled=ya_incluido, type="secondary",
                    help="Ya está en tus palabras clave" if ya_incluido
                    else "Añadir a palabras clave",
                ):
                    repo.save_perfil({**perfil_now, "palabras_clave": ", ".join(raw_user + [term])})
                    cargar_perfil.clear()
                    st.rerun()


if not _perfil_ok:
    # Sin perfil no hay sitio: solo se renderiza el onboarding del perfil.
    vista_perfil()
elif vista == "Explorar":
    vista_explorar(filtros)
elif vista == "Match":
    vista_match(filtros)
elif vista == "Perfil":
    vista_perfil()
else:
    vista_favoritos()

# Abre el modal de detalle si hay una licitacion seleccionada.
# Se mantiene abierto entre reruns internos (resumen/propuesta); se cierra con "Cerrar".
if st.session_state["detalle_id"] is not None:
    _proc = repo.get_proceso(st.session_state["detalle_id"])
    if _proc:
        dialog_detalle(_proc)
    else:
        st.session_state["detalle_id"] = None
