"""Sistema visual: liquid glass premium. Paleta estricta blanco/negro/azul.

Cada card es un CONTENEDOR real de Streamlit estilizado como vidrio via :has(),
para que los botones nativos vivan DENTRO del vidrio (no desacoplados).
Sin emojis. Iconos SVG inline. Tipografia: Bricolage Grotesque + Plus Jakarta Sans.
"""
import html

ICONS = {
    "building": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M9 7h2M9 11h2M9 15h2M15 21V11h4v10"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "money": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.5-1.5 3-3.3 3-5.5A4.5 4.5 0 0 0 12 6 4.5 4.5 0 0 0 2 8.5c0 2.2 1.5 4 3 5.5l7 7Z"/></svg>',
    "heart_fill": '<svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"><path d="M19 14c1.5-1.5 3-3.3 3-5.5A4.5 4.5 0 0 0 12 6 4.5 4.5 0 0 0 2 8.5c0 2.2 1.5 4 3 5.5l7 7Z"/></svg>',
    "search": '<svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/></svg>',
    "bookmark": '<svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
    "logo": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 12l9 4 9-4M3 17l9 4 9-4"/></svg>',
    "grid": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
    "user": '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>',
    "briefcase": '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="7" width="19" height="13" rx="2.5"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M2.5 12h19"/></svg>',
    "key": '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="5"/><path d="m11.5 11.5 8 8M16 16l2.5-2.5M19.5 19.5 22 17"/></svg>',
    "layers": '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5M3 18l9 5 9-5"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></svg>',
    "rocket": '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 15c-1 1-1.5 3.5-1.5 5 1.5 0 4-.5 5-1.5M9 11a8 8 0 0 1 8-8c2 0 3 1 3 3a8 8 0 0 1-8 8l-3-3Z"/><circle cx="14.5" cy="9.5" r="1.4"/><path d="M9 11l-2 1 3 3 1-2"/></svg>',
}

# Overlay de ruido fino (textura premium) como data-URI.
_NOISE = (
    "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmci"
    "IHdpZHRoPSIxMjAiIGhlaWdodD0iMTIwIj48ZmlsdGVyIGlkPSJuIj48ZmVUdXJidWxlbmNlIHR5"
    "cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iLjkiIG51bU9jdGF2ZXM9IjIiLz48L2Zp"
    "bHRlcj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWx0ZXI9InVybCgjbikiIG9w"
    "YWNpdHk9Ii4wNCIvPjwvc3ZnPg=="
)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root{{
  --white:#F4F7FC; --muted:rgba(244,247,252,.60); --faint:rgba(244,247,252,.40);
  --blue:#6E93CF; --blue-deep:#3C5C96; --blue-soft:rgba(110,147,207,.15);
  --glass:linear-gradient(135deg, rgba(255,255,255,.11), rgba(255,255,255,.035));
  --glass-strong:linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.05));
  --hair:rgba(255,255,255,.16); --hair-2:rgba(255,255,255,.30);
  --shadow:0 10px 34px rgba(2,6,23,.55);
  --inset:inset 0 1px 0 rgba(255,255,255,.30), inset 0 -10px 24px rgba(2,6,23,.18);
}}

html, body, [class*="css"]{{font-family:'Plus Jakarta Sans',sans-serif}}

/* --- Fondo atmosferico, animacion sutil y profesional detras del vidrio --- */
.stApp{{
  background:
    radial-gradient(760px 760px at 50% 118%, rgba(110,147,207,.07), transparent 60%),
    linear-gradient(165deg, #0A1326 0%, #070C18 52%, #04060D 100%);
  background-attachment:fixed;color:var(--white);overflow-x:hidden;
}}
/* Capa de bruma profunda en deriva lenta (tonos azul/acero, sin neon) */
.stApp::before{{content:"";position:fixed;inset:-28%;pointer-events:none;z-index:0;
  background:
    radial-gradient(520px 520px at 18% 24%, rgba(110,147,207,.18), transparent 62%),
    radial-gradient(480px 480px at 84% 14%, rgba(60,92,150,.16), transparent 62%),
    radial-gradient(560px 560px at 70% 84%, rgba(86,112,160,.12), transparent 64%),
    radial-gradient(440px 440px at 26% 80%, rgba(110,147,207,.10), transparent 64%);
  filter:blur(46px);will-change:transform,opacity;
  animation:auroraDrift 46s ease-in-out infinite alternate,
            auroraBreath 14s ease-in-out infinite;}}
.stApp::after{{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:url('{_NOISE}');background-size:120px;opacity:.6;mix-blend-mode:overlay}}
.block-container{{padding-top:2rem;padding-bottom:4rem;max-width:1240px;position:relative;z-index:1}}
h1,h2,h3{{font-family:'Bricolage Grotesque',sans-serif;letter-spacing:-.02em}}

/* ================= ANIMACIONES ================= */
@keyframes auroraDrift{{
  0%{{transform:translate3d(-2%,-1%,0) scale(1) rotate(0deg)}}
  50%{{transform:translate3d(3%,2%,0) scale(1.06) rotate(2deg)}}
  100%{{transform:translate3d(-1%,3%,0) scale(1.03) rotate(-2deg)}}
}}
@keyframes auroraBreath{{0%,100%{{opacity:.85}}50%{{opacity:1}}}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes navPop{{from{{opacity:0;transform:translateY(8px) scale(.96)}}to{{opacity:1;transform:none}}}}
@keyframes floatY{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
@keyframes sheen{{0%{{transform:translateX(-120%)}}100%{{transform:translateX(220%)}}}}
@media (prefers-reduced-motion:reduce){{
  .stApp::before{{animation:none}}
  *{{animation-duration:.01ms !important;animation-iteration-count:1 !important}}
}}

/* ================= SIDEBAR ================= */
section[data-testid="stSidebar"]{{
  background:linear-gradient(180deg, rgba(12,22,44,.86), rgba(7,12,24,.94));
  backdrop-filter:blur(16px) saturate(140%);-webkit-backdrop-filter:blur(16px) saturate(140%);
  border-right:1px solid var(--hair);
}}
section[data-testid="stSidebar"] .block-container{{padding-top:1.4rem}}
section[data-testid="stSidebar"] *{{color:var(--white)}}
.lt-brand{{display:flex;align-items:center;gap:11px;padding:4px 2px 2px}}
.lt-brand .mark{{display:grid;place-items:center;width:38px;height:38px;border-radius:12px;
  background:var(--glass-strong);border:1px solid var(--hair-2);color:var(--blue);
  box-shadow:var(--inset)}}
.lt-brand .name{{font-family:'Bricolage Grotesque';font-weight:750;font-size:17px;line-height:1}}
.lt-brand .tag{{color:var(--faint);font-size:11px;margin-top:3px;letter-spacing:.04em;
  text-transform:uppercase}}
.lt-side-label{{color:var(--faint);font-size:11px;font-weight:700;letter-spacing:.12em;
  text-transform:uppercase;margin:20px 0 9px;padding-bottom:7px;
  border-bottom:1px solid var(--hair)}}
.lt-side-count{{color:var(--muted);font-size:12px;margin:12px 2px 4px}}
.lt-side-count::before{{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;
  background:var(--blue);margin-right:7px;vertical-align:middle}}
/* Sidebar: inputs/selects mas compactos y alineados */
section[data-testid="stSidebar"] .stTextInput,
section[data-testid="stSidebar"] .stSelectbox{{margin-bottom:2px}}
section[data-testid="stSidebar"] [data-testid="stExpander"]{{margin-top:6px}}

/* ===== Navegacion 2x2: iconos cuadrados; hover expande y revela el texto ===== */
/* las dos filas de st.columns que contienen los botones nav_* */
section[data-testid="stSidebar"]
  [data-testid="stHorizontalBlock"]:has([class*="st-key-nav_"]){{
  gap:10px;margin-bottom:10px}}
section[data-testid="stSidebar"] [class*="st-key-nav_"]{{
  position:relative;animation:navPop .42s cubic-bezier(.16,1,.3,1) both}}
section[data-testid="stSidebar"] [class*="st-key-nav_Match"]{{animation-delay:.05s}}
section[data-testid="stSidebar"] [class*="st-key-nav_Favoritos"]{{animation-delay:.10s}}
section[data-testid="stSidebar"] [class*="st-key-nav_Perfil"]{{animation-delay:.15s}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton{{margin:0}}

section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button{{
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0;
  width:100%;min-height:84px;padding:6px;border-radius:16px;overflow:hidden;
  transition:min-height .28s cubic-bezier(.16,1,.3,1),padding .28s,transform .28s
    cubic-bezier(.16,1,.3,1),background .24s,border-color .24s,box-shadow .24s;}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button
  [data-testid="stIconMaterial"]{{
  font-size:27px;line-height:1;margin:0;
  transition:transform .28s cubic-bezier(.16,1,.3,1)}}
/* etiqueta: colapsada por defecto (solo icono), accesible en el DOM */
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button
  [data-testid="stMarkdownContainer"]{{
  max-height:0;opacity:0;overflow:hidden;margin-top:0;
  font-size:12.5px;font-weight:650;letter-spacing:.01em;white-space:nowrap;
  transition:max-height .28s cubic-bezier(.16,1,.3,1),opacity .22s ease,margin-top .28s}}
/* hover/focus: crece y aparece el texto bajo el icono */
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button:hover,
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button:focus-visible{{
  min-height:106px;padding:14px 8px;transform:translateY(-3px)}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button:hover
  [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button:focus-visible
  [data-testid="stIconMaterial"]{{transform:scale(1.12) translateY(-1px)}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button:hover
  [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [class*="st-key-nav_"] .stButton>button:focus-visible
  [data-testid="stMarkdownContainer"]{{max-height:24px;opacity:1;margin-top:9px}}
/* estados (sin neon): vidrio neutro + activo en azul apagado */
section[data-testid="stSidebar"] [class*="st-key-nav_"]
  .stButton>button[kind="secondary"]{{
  background:var(--glass);border:1px solid var(--hair);color:var(--muted);box-shadow:none}}
section[data-testid="stSidebar"] [class*="st-key-nav_"]
  .stButton>button[kind="secondary"]:hover{{
  background:var(--glass-strong);border-color:var(--hair-2);color:var(--white)}}
section[data-testid="stSidebar"] [class*="st-key-nav_"]
  .stButton>button[kind="primary"]{{
  background:linear-gradient(160deg,var(--blue),var(--blue-deep));
  border:1px solid var(--hair-2);color:#fff;box-shadow:0 8px 20px rgba(2,6,23,.45),var(--inset)}}
section[data-testid="stSidebar"] [class*="st-key-nav_"]
  .stButton>button[kind="primary"] [data-testid="stIconMaterial"]{{color:#fff}}

/* ================= HERO ================= */
.lt-hero{{display:flex;align-items:center;gap:13px;margin-bottom:2px;
  animation:fadeUp .5s cubic-bezier(.16,1,.3,1) both}}
.lt-hero .ic{{display:grid;place-items:center;width:44px;height:44px;border-radius:14px;
  background:var(--glass-strong);border:1px solid var(--hair-2);color:var(--blue);
  box-shadow:var(--shadow),var(--inset);backdrop-filter:blur(12px);
  animation:floatY 5s ease-in-out infinite}}
.lt-hero h1{{font-size:30px;font-weight:800;margin:0;color:var(--white)}}
.lt-sub{{color:var(--muted);font-size:14px;margin:6px 0 22px 57px;
  animation:fadeUp .5s .06s cubic-bezier(.16,1,.3,1) both}}

/* ================= GRID ALIGN ================= */
[data-testid="stHorizontalBlock"]{{align-items:stretch;gap:18px}}

/* ===== CARD = contenedor bordeado con marcador .gcard (vidrio real) ===== */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.gcard){{
  height:100%;border-radius:22px;padding:6px;
  background:var(--glass);
  border:1px solid var(--hair) !important;
  backdrop-filter:blur(13px) saturate(150%);-webkit-backdrop-filter:blur(13px) saturate(150%);
  box-shadow:var(--shadow),var(--inset);
  position:relative;overflow:hidden;
  transition:transform .2s cubic-bezier(.16,1,.3,1),border-color .2s,box-shadow .2s;
  animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.gcard)::before{{
  content:"";position:absolute;inset:0;pointer-events:none;border-radius:22px;z-index:0;
  background:radial-gradient(120% 80% at 0% 0%, rgba(255,255,255,.18), transparent 45%);}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.gcard):hover{{
  transform:translateY(-4px);border-color:var(--hair-2) !important;
  box-shadow:0 22px 54px rgba(2,6,23,.6),var(--inset)}}
/* contenido interno en columna flexible, padding y botones al fondo */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.gcard) > div{{
  height:100%;position:relative;z-index:1}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.gcard) > div > div[data-testid="stVerticalBlock"]{{
  height:100%;display:flex;flex-direction:column;padding:12px 14px 12px;gap:0}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.gcard)
  div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:last-child{{
  margin-top:auto;padding-top:12px}}

.gcard{{display:none}}
.lt-badge{{display:inline-flex;align-items:center;font-size:10.5px;font-weight:700;
  letter-spacing:.04em;text-transform:uppercase;color:#BFD6FF;background:var(--blue-soft);
  border:1px solid rgba(76,141,255,.4);border-radius:999px;padding:4px 11px}}
.lt-badge-rel{{display:inline-flex;align-items:center;margin-left:7px;font-size:10.5px;
  font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#C7D6F0;
  background:rgba(110,147,207,.14);border:1px solid rgba(110,147,207,.40);
  border-radius:999px;padding:4px 11px;transition:background .2s,border-color .2s}}
.lt-fav{{margin-left:auto}}
.lt-head{{display:flex;align-items:center;margin-bottom:13px}}
.lt-title{{font-family:'Bricolage Grotesque';font-size:15.5px;font-weight:650;color:var(--white);
  line-height:1.32;margin:0 0 14px;min-height:62px;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.lt-row{{display:flex;align-items:center;gap:9px;color:var(--muted);font-size:12.5px;margin:6px 0;
  transition:color .2s ease}}
.lt-row svg{{color:var(--blue);flex:0 0 auto;transition:transform .2s ease}}
.lt-badge{{transition:background .2s,border-color .2s}}
.lt-fav svg{{transition:transform .2s cubic-bezier(.16,1,.3,1)}}
.lt-fav:hover svg{{transform:scale(1.18)}}
.lt-row b{{color:var(--white);font-weight:600}}
.lt-money{{color:#9FC2FF;font-weight:700;font-size:13.5px}}
.lt-div{{height:1px;background:var(--hair);margin:13px 0 11px;border:0}}

/* ================= INPUTS ================= */
.stTextInput label,.stSelectbox label,.stNumberInput label{{
  color:var(--faint) !important;font-size:11.5px !important;font-weight:700 !important;
  text-transform:uppercase;letter-spacing:.06em}}
div[data-baseweb="input"], div[data-baseweb="select"]>div, .stNumberInput div[data-baseweb]{{
  background:var(--glass) !important;border:1px solid var(--hair) !important;
  border-radius:13px !important;backdrop-filter:blur(10px)}}
div[data-baseweb="input"] input, .stNumberInput input{{color:var(--white) !important;
  background:transparent !important}}
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]>div:focus-within{{
  border-color:var(--blue) !important;box-shadow:0 0 0 3px var(--blue-soft) !important}}
input::placeholder{{color:var(--faint) !important}}

/* ================= PILLS (sugerencias) ================= */
[data-testid="stPills"] button, .lt-pill{{
  background:var(--glass) !important;border:1px solid var(--hair) !important;
  color:var(--muted) !important;border-radius:999px !important;font-weight:600 !important;
  padding:5px 14px !important;backdrop-filter:blur(10px)}}
[data-testid="stPills"] button:hover{{color:var(--white) !important;border-color:var(--hair-2) !important}}
[data-testid="stPills"] button[aria-checked="true"]{{
  background:linear-gradient(160deg,var(--blue),var(--blue-deep)) !important;color:#fff !important;
  border-color:transparent !important;box-shadow:0 6px 16px rgba(2,6,23,.4) !important}}

/* ================= BOTONES ================= */
.stButton>button{{border-radius:12px;font-weight:600;color:var(--white);
  background:var(--glass);border:1px solid var(--hair);backdrop-filter:blur(12px);
  transition:background .2s ease,border-color .2s ease,box-shadow .2s ease,
    transform .2s cubic-bezier(.16,1,.3,1)}}
.stButton>button:hover{{background:var(--glass-strong);border-color:var(--hair-2);
  transform:translateY(-1px)}}
.stButton>button:active{{transform:translateY(0) scale(.98)}}
.stButton>button[kind="primary"]{{background:linear-gradient(160deg,var(--blue),var(--blue-deep));
  border:1px solid var(--hair-2);box-shadow:0 8px 20px rgba(2,6,23,.45)}}
.stLinkButton>a{{border-radius:12px !important;background:var(--glass) !important;
  border:1px solid var(--hair) !important;color:var(--white) !important;backdrop-filter:blur(12px)}}

/* ================= SWIPE (match) — ficha profesional ================= */
.lt-swipe{{max-width:620px;margin:6px auto 0;border-radius:28px;padding:30px 32px 32px;
  background:var(--glass-strong);border:1px solid var(--hair-2);
  backdrop-filter:blur(20px) saturate(155%);-webkit-backdrop-filter:blur(20px) saturate(155%);
  box-shadow:0 34px 80px rgba(2,6,23,.62),var(--inset);position:relative;overflow:hidden;
  animation:fadeUp .42s cubic-bezier(.16,1,.3,1) both}}
.lt-swipe::before{{content:"";position:absolute;inset:0;pointer-events:none;border-radius:28px;
  background:radial-gradient(120% 70% at 0% 0%, rgba(255,255,255,.22), transparent 46%)}}
/* franja de brillo que cruza la ficha al aparecer */
.lt-swipe::after{{content:"";position:absolute;top:0;left:0;width:40%;height:100%;
  pointer-events:none;transform:skewX(-18deg);
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.10),transparent);
  animation:sheen 2.6s ease-in-out .3s 1}}
.lt-swipe>*{{position:relative;z-index:1}}
.lt-swipe .lt-title{{-webkit-line-clamp:4;min-height:auto;font-size:21px;margin:14px 0 16px}}
.lt-swipe-head{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.lt-rank{{margin-left:auto;display:inline-flex;align-items:center;gap:6px;font-size:11px;
  font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--faint)}}
/* Bloque entidad destacado */
.lt-entity{{display:flex;align-items:center;gap:12px;padding:13px 15px;margin:4px 0 16px;
  border-radius:16px;background:var(--glass);border:1px solid var(--hair)}}
.lt-entity .ava{{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;
  flex:0 0 auto;background:linear-gradient(135deg,rgba(76,141,255,.30),rgba(37,99,235,.12));
  border:1px solid var(--hair-2);color:#BFD6FF;font-family:'Bricolage Grotesque';
  font-weight:750;font-size:17px}}
.lt-entity .meta{{min-width:0}}
.lt-entity .meta .nm{{font-family:'Bricolage Grotesque';font-weight:650;font-size:14.5px;
  color:var(--white);line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.lt-entity .meta .lc{{color:var(--muted);font-size:12px;margin-top:2px;display:flex;
  align-items:center;gap:6px}}
.lt-entity .meta .lc svg{{color:var(--blue)}}
/* Grid de stats */
.lt-stats{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:2px 0 6px}}
.lt-stat{{padding:12px 14px;border-radius:15px;background:var(--glass);
  border:1px solid var(--hair);transition:border-color .2s,transform .2s}}
.lt-stat:hover{{border-color:var(--hair-2);transform:translateY(-2px)}}
.lt-stat .k{{display:flex;align-items:center;gap:7px;color:var(--faint);font-size:10.5px;
  font-weight:700;letter-spacing:.07em;text-transform:uppercase;margin-bottom:6px}}
.lt-stat .k svg{{color:var(--blue);width:14px;height:14px}}
.lt-stat .v{{font-family:'Bricolage Grotesque';color:var(--white);font-weight:700;
  font-size:15px;line-height:1.2;word-break:break-word}}
.lt-stat .v.money{{color:#9FC2FF}}
.lt-stat.span2{{grid-column:1 / -1}}

/* ================= FORM PERFIL — expresivo y amigable ================= */
[data-testid="stForm"]{{
  background:var(--glass-strong);border:1px solid var(--hair-2) !important;border-radius:24px;
  padding:26px 26px 22px !important;position:relative;overflow:hidden;
  backdrop-filter:blur(18px) saturate(150%);-webkit-backdrop-filter:blur(18px) saturate(150%);
  box-shadow:0 28px 64px rgba(2,6,23,.5),var(--inset);
  animation:fadeUp .5s cubic-bezier(.16,1,.3,1) both}}
[data-testid="stForm"]::before{{content:"";position:absolute;inset:0;pointer-events:none;
  border-radius:24px;background:radial-gradient(120% 60% at 0% 0%,rgba(255,255,255,.16),transparent 44%)}}
[data-testid="stForm"]>div{{position:relative;z-index:1}}
/* label con icono para cada campo */
.ff-label{{display:flex;align-items:center;gap:9px;margin:4px 0 7px}}
.ff-label .ff-ic{{display:grid;place-items:center;width:30px;height:30px;border-radius:10px;
  flex:0 0 auto;background:linear-gradient(135deg,rgba(76,141,255,.26),rgba(37,99,235,.10));
  border:1px solid var(--hair-2);color:#BFD6FF}}
.ff-label .ff-t{{font-family:'Bricolage Grotesque';font-weight:650;font-size:14.5px;color:var(--white)}}
.ff-label .ff-hint{{color:var(--faint);font-size:12px;font-weight:500;margin-left:2px}}
/* separador suave entre bloques del form */
.ff-sep{{height:1px;background:var(--hair);margin:18px 0 16px;border:0}}
.ff-tip{{display:flex;align-items:center;gap:9px;margin:2px 0 18px;padding:11px 14px;
  border-radius:14px;background:var(--blue-soft);border:1px solid rgba(76,141,255,.32);
  color:#CFE0FF;font-size:12.5px}}
.ff-tip svg{{color:var(--blue);flex:0 0 auto}}

/* ================= CHIPS DE FILTROS ACTIVOS ================= */
.lt-chips{{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 4px}}
.lt-chip{{display:inline-flex;align-items:center;font-size:12px;font-weight:600;
  color:#BFD6FF;background:var(--blue-soft);border:1px solid rgba(76,141,255,.4);
  border-radius:999px;padding:4px 12px;backdrop-filter:blur(8px)}}

/* Expander (filtros plegables) acorde al vidrio */
[data-testid="stExpander"] details{{background:var(--glass) !important;
  border:1px solid var(--hair) !important;border-radius:14px !important;
  backdrop-filter:blur(12px)}}
[data-testid="stExpander"] summary{{color:var(--muted) !important;font-weight:600}}

/* Metric, tabs */
[data-testid="stMetricValue"]{{color:var(--white);font-family:'Bricolage Grotesque'}}
[data-testid="stMetricLabel"]{{color:var(--muted)}}
.stTabs [aria-selected="true"]{{color:var(--white)}}
.stTabs [data-baseweb="tab-highlight"]{{background:var(--blue)}}
#MainMenu,header[data-testid="stHeader"]{{background:transparent}}
</style>
"""


def _fmt_money(v) -> str:
    try:
        return f"${float(v):,.0f} COP"
    except (TypeError, ValueError):
        return "Sin valor"


def _esc(v, fallback="Sin dato") -> str:
    return html.escape(str(v)) if v else fallback


def _fmt_ubicacion(proc: dict) -> str:
    """Ciudad, Departamento -> 'Ciudad · Depto'. Omite partes vacias."""
    partes = [p for p in (proc.get("ciudad"), proc.get("departamento")) if p]
    return html.escape(" · ".join(partes)) if partes else "Sin ubicacion"


def card_inner(proc: dict, es_favorito: bool) -> str:
    """Contenido del card (sin borde; el contenedor aporta el vidrio). Incluye marcador."""
    estado = _esc(proc.get("estado"), "Sin estado")
    objeto = _esc((proc.get("objeto") or "Sin objeto")[:170])
    entidad = _esc(proc.get("entidad"), "Sin entidad")
    depto = _fmt_ubicacion(proc)
    fecha = _esc(proc.get("fecha_publicacion"), "Sin fecha")[:10]
    money = _fmt_money(proc.get("valor"))
    heart = ICONS["heart_fill"] if es_favorito else ICONS["heart"]
    hcolor = "#6E93CF" if es_favorito else "rgba(244,247,252,.4)"
    rel = (
        '<span class="lt-badge-rel">Para tu empresa</span>'
        if proc.get("_relevante")
        else ""
    )
    return f"""
    <span class="gcard"></span>
    <div class="lt-head">
      <span class="lt-badge">{estado}</span>{rel}
      <span class="lt-fav" style="color:{hcolor}">{heart}</span>
    </div>
    <p class="lt-title">{objeto}</p>
    <div class="lt-row">{ICONS['building']}<span><b>{entidad}</b></span></div>
    <div class="lt-row">{ICONS['pin']}<span>{depto}</span></div>
    <hr class="lt-div"/>
    <div class="lt-row">{ICONS['money']}<span class="lt-money">{money}</span></div>
    <div class="lt-row">{ICONS['calendar']}<span>{fecha}</span></div>
    """


def _raw(proc: dict) -> dict:
    """Decodifica raw_json del proceso (campos extra del dataset SECOP)."""
    import json
    try:
        return json.loads(proc.get("raw_json") or "{}")
    except (ValueError, TypeError):
        return {}


def _cap(v: str, n: int = 40) -> str:
    """Capitaliza y recorta un valor de texto para mostrarlo limpio."""
    s = str(v or "").strip()
    if not s:
        return ""
    s = s if s.isupper() is False and any(c.islower() for c in s) else s.title()
    return html.escape(s[:n] + ("…" if len(s) > n else ""))


def _stat(icon: str, label: str, value: str, money: bool = False, span: bool = False) -> str:
    if not value:
        return ""
    cls = "lt-stat span2" if span else "lt-stat"
    vcls = "v money" if money else "v"
    return (f'<div class="{cls}"><div class="k">{ICONS[icon]}{html.escape(label)}</div>'
            f'<div class="{vcls}">{value}</div></div>')


def swipe_html(proc: dict) -> str:
    """Ficha de match ampliada: entidad destacada + grid de datos del proceso."""
    raw = _raw(proc)
    objeto = _esc((proc.get("objeto") or "Sin objeto")[:240])
    entidad = proc.get("entidad") or "Sin entidad"
    inicial = html.escape(entidad.strip()[:1].upper() or "?")
    ubic_ent = " · ".join(
        x for x in (raw.get("ciudad_entidad"), raw.get("departamento_entidad")) if x
    ) or _fmt_ubicacion(proc)
    estado = _esc(proc.get("estado"), "Sin estado")
    rel = ('<span class="lt-badge-rel">Para tu empresa</span>'
           if proc.get("_relevante") else "")
    orden = _cap(raw.get("ordenentidad"), 26)

    duracion = ""
    if raw.get("duracion"):
        duracion = f"{html.escape(str(raw['duracion']))} {_cap(raw.get('unidad_de_duracion'), 14)}".strip()

    stats = "".join([
        _stat("money", "Valor estimado", _fmt_money(proc.get("valor")), money=True),
        _stat("briefcase", "Modalidad", _cap(raw.get("modalidad_de_contratacion"), 36)),
        _stat("doc", "Tipo de contrato", _cap(raw.get("tipo_de_contrato"), 28)),
        _stat("calendar", "Duracion", duracion),
        _stat("calendar", "Publicado", _esc(proc.get("fecha_publicacion"), "")[:10]),
        _stat("user", "Respuestas recibidas", _cap(raw.get("respuestas_al_procedimiento"), 10)),
        _stat("layers", "Referencia", _cap(raw.get("referencia_del_proceso"), 30), span=True),
    ])

    nit = _cap(raw.get("nit_entidad"), 18)
    ent_sub = " · ".join(x for x in (orden, f"NIT {nit}" if nit else "") if x)

    return f"""
    <div class="lt-swipe">
      <div class="lt-swipe-head">
        <span class="lt-badge">{estado}</span>{rel}
        <span class="lt-rank">{ICONS['spark']} Match</span>
      </div>
      <p class="lt-title">{objeto}</p>
      <div class="lt-entity">
        <span class="ava">{inicial}</span>
        <div class="meta">
          <div class="nm">{html.escape(entidad)}</div>
          <div class="lc">{ICONS['pin']}<span>{html.escape(ubic_ent) or 'Sin ubicacion'}</span></div>
          {f'<div class="lc" style="margin-top:3px">{ICONS["building"]}<span>{html.escape(ent_sub)}</span></div>' if ent_sub else ''}
        </div>
      </div>
      <div class="lt-stats">{stats}</div>
    </div>
    """


def field_label(icon: str, titulo: str, hint: str = "") -> str:
    """Etiqueta con icono para un campo del formulario de perfil."""
    h = f'<span class="ff-hint">{html.escape(hint)}</span>' if hint else ""
    return (f'<div class="ff-label"><span class="ff-ic">{ICONS.get(icon, ICONS["user"])}</span>'
            f'<span class="ff-t">{html.escape(titulo)}</span>{h}</div>')


def form_tip(texto: str) -> str:
    return f'<div class="ff-tip">{ICONS["rocket"]}<span>{html.escape(texto)}</span></div>'


def hero_html(titulo: str, subtitulo: str, icono: str = "search") -> str:
    return f"""
    <div class="lt-hero"><span class="ic">{ICONS.get(icono, ICONS['search'])}</span>
    <h1>{html.escape(titulo)}</h1></div>
    <p class="lt-sub">{html.escape(subtitulo)}</p>
    """


def brand_html() -> str:
    return f"""
    <div class="lt-brand">
      <span class="mark">{ICONS['logo']}</span>
      <div><div class="name">SECOP Tracker</div>
      <div class="tag">Licitaciones · IA local</div></div>
    </div>
    """
