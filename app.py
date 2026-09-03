from __future__ import annotations

import base64
import json
import re
import uuid
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

# ============================================================
# S & J — App de 6 meses
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
MOMENTS_DIR = ASSETS_DIR / "moments"
BB_UPLOADS_DIR = ASSETS_DIR / "bb_uploads"
DATA_DIR = BASE_DIR / "data"
BB_MEMORY_DB = DATA_DIR / "bb_memories.json"
ANSWERS_DB = DATA_DIR / "respuestas_bb.json"

BB_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

INITIALS = "S & J"
BB = "bb"
RELATIONSHIP_START = date(2026, 3, 13)
SIX_MONTH_DATE = date(2026, 9, 13)
ACCESS_CODE = "13032026"

# Las carpetas están ordenadas como las compartiste.
# Las coordenadas son solo para lugares públicos que sí podemos ubicar con seguridad.
# Los lugares privados se dejan fuera del mapa.
MOMENTS = [
    {
        "slug": "01_long_lake",
        "title": "Long Lake, Colorado",
        "short": "Long Lake",
        "category": "Aventura",
        "phrase": "Entre montañas y agua, cualquier camino se disfruta más contigo.",
        "coords": (40.078, -105.584),
        "map_note": "Ubicación aproximada del área de Long Lake.",
    },
    {
        "slug": "02_silver_plume",
        "title": "Silver Plume, Colorado",
        "short": "Silver Plume",
        "category": "Aventura",
        "phrase": "Una parada pequeña que terminó convirtiéndose en un recuerdo enorme.",
        "coords": (39.6961, -105.7253),
    },
    {
        "slug": "03_nederland",
        "title": "Nederland, Colorado",
        "short": "Nederland",
        "category": "Aventura",
        "phrase": "Nuevos lugares, nuevas historias… siempre tú y yo.",
        "coords": (39.9614, -105.5108),
    },
    {
        "slug": "04_topgolf",
        "title": "TopGolf, Colorado",
        "short": "TopGolf",
        "category": "Salida",
        "phrase": "Competencia, risas y otro plan que terminó siendo de mis favoritos contigo.",
        "coords": None,
        "map_note": "Dime después cuál TopGolf fue y lo ponemos exacto en el mapa.",
    },
    {
        "slug": "05_primera_salida",
        "title": "Nuestra primera salida como novios",
        "short": "Primera salida",
        "category": "Nosotros",
        "phrase": "La primera salida con un nombre nuevo para lo nuestro: novios. ♡",
        "coords": None,
        "map_note": "Cuando me digas el lugar, lo agregamos al mapa.",
    },
    {
        "slug": "06_estes_park",
        "title": "Estes Park, Colorado",
        "short": "Estes Park",
        "category": "Escapada",
        "phrase": "Noches que se quedan en el alma, bb.",
        "coords": (40.3772, -105.5217),
    },
    {
        "slug": "07_black_hawk",
        "title": "Black Hawk, Colorado",
        "short": "Black Hawk",
        "category": "Noche",
        "phrase": "Entre luces, apuestas y risas, mi mejor suerte siempre eres tú.",
        "coords": (39.8017, -105.4939),
    },
    {
        "slug": "08_comida_depa",
        "title": "Comida en tu depa",
        "short": "En casa",
        "category": "Momentos simples",
        "phrase": "También amo esto: comer contigo, platicar y sentir que cualquier momento sencillo puede volverse especial.",
        "coords": None,
        "map_note": "Este recuerdo se queda privado, sin ubicación en el mapa. ♡",
    },
    {
        "slug": "09_vegas",
        "title": "Las Vegas, Nevada",
        "short": "Las Vegas",
        "category": "Viaje",
        "phrase": "Una de nuestras aventuras más grandes hasta ahora. Y todavía faltan muchas, bb.",
        "coords": (36.1699, -115.1398),
    },
    {
        "slug": "10_golden",
        "title": "Golden, Colorado",
        "short": "Golden",
        "category": "Aventura",
        "phrase": "Cada aventura contigo me confirma que mi lugar favorito no es un lugar: es juntos.",
        "coords": (39.7555, -105.2211),
    },
]

QUESTIONS = [
    "¿Qué fue lo que más te gustó de mí antes de que fuéramos novios?",
    "¿Qué es lo que más te ha gustado que he hecho por ti desde que somos novios?",
    "Dime 3 cosas de mí que te gusten — pueden ser de mi forma de ser, físicas o de cómo te trato.",
    "¿Cuál de nuestras salidas o viajes repetirías mañana sin pensarlo y por qué?",
    "¿Qué es algo que te gustaría que viviéramos juntos en nuestros próximos 6 meses?",
]

REASONS = [
    "Porque contigo puedo ser yo, sin filtros y sin sentir que tengo que fingir nada.",
    "Porque tu sonrisa tiene una forma muy tuya de cambiarme el día.",
    "Porque incluso un plan sencillo termina sintiéndose especial si estoy contigo.",
    "Porque amo nuestra complicidad y esas cosas que solo tú y yo entendemos.",
    "Porque contigo siempre quiero sumar otra salida, otro viaje y otra aventura.",
    "Porque admiro todo eso que te hace ser tú, bb.",
    "Porque verte feliz también se ha convertido en una de mis cosas favoritas.",
    "Porque contigo he aprendido a disfrutar más el presente y los pequeños momentos.",
    "Porque nuestras risas, conversaciones y locuras ya forman parte de mis recuerdos favoritos.",
    "Porque entre todas las posibilidades, bb, me sigue encantando elegirte a ti.",
]

# ============================================================
# PAGE + CSS
# ============================================================

st.set_page_config(
    page_title="S & J · Nuestros 6 meses",
    page_icon="♡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root {
    --paper:#fbf5ed;
    --paper2:#f2e5d8;
    --ink:#322925;
    --muted:#7c7068;
    --rose:#d89296;
    --rose2:#efd1cf;
    --gold:#bd9454;
    --black:#10100f;
}
html, body, [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 12% 6%, rgba(217,146,150,.11), transparent 26%),
      radial-gradient(circle at 90% 10%, rgba(189,148,84,.08), transparent 24%),
      linear-gradient(180deg,#fcf8f3 0%,#f5eadf 100%);
    color:var(--ink);
}
[data-testid="stHeader"] {background:transparent;}
.block-container {
  max-width:440px;
  padding:0.75rem 0.9rem 6.8rem;
  margin:0 auto;
  min-height:100vh;
  background:rgba(255,250,244,.97);
  border-left:1px solid rgba(111,82,61,.06);
  border-right:1px solid rgba(111,82,61,.06);
}
h1,h2,h3 {font-family:Georgia,'Times New Roman',serif!important;}

.hero {
  position:relative; overflow:hidden; border-radius:30px; padding:46px 32px 40px;
  background:linear-gradient(145deg,#0c0c0b,#1a1714 70%,#201a15);
  color:#f8eee1; border:1px solid rgba(189,148,84,.34);
  box-shadow:0 24px 60px rgba(63,42,30,.18);
}
.hero:after {content:"";position:absolute;width:480px;height:480px;border-radius:50%;right:-180px;top:-280px;background:radial-gradient(circle,rgba(189,148,84,.22),transparent 66%);}
.hero-kicker {position:relative;text-align:center;color:#d3ad72;letter-spacing:.28em;text-transform:uppercase;font-size:.76rem;z-index:1;}
.hero-title {position:relative;text-align:center;font:500 clamp(3.4rem,8vw,7rem)/1 Georgia,serif;z-index:1;margin:.4rem 0 .6rem;}
.hero-sub {position:relative;text-align:center;color:#d6c8bb;max-width:690px;margin:auto;z-index:1;line-height:1.7;}
.hero-heart {position:relative;z-index:1;text-align:center;color:#d3ad72;font-size:1.8rem;margin-top:14px;}

.paper-card {background:rgba(255,252,248,.93);border:1px solid rgba(102,75,57,.11);border-radius:22px;padding:22px;box-shadow:0 10px 30px rgba(76,54,39,.07);}
.scrap-note {background:#f1d6d2;border-radius:7px;padding:20px;box-shadow:0 8px 18px rgba(75,49,40,.09);transform:rotate(-.35deg);}
.scrap-note h3 {margin-top:0;text-align:center;}
.section-title {font:500 2.15rem Georgia,serif;margin:.5rem 0 .15rem;}
.section-sub {color:var(--muted);margin-bottom:1.3rem;}

.metric-shell {display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0 8px;}
.metric-card {background:linear-gradient(180deg,#fffaf5,#f1e2d7);border:1px solid rgba(216,146,150,.22);border-radius:22px;padding:22px 16px;text-align:center;min-height:145px;}
.metric-big {font:500 clamp(2.2rem,5vw,4rem)/1 Georgia,serif;color:#8c5f58;}
.metric-label {margin-top:.5rem;color:#756861;font-size:.92rem;}
.metric-mini {margin-top:.5rem;color:#aa7973;font-size:.82rem;}

.film-wrap {overflow-x:auto;padding:12px 4px 20px;scroll-snap-type:x mandatory;}
.film-roll {display:flex;gap:0;background:#111;padding:16px 10px;border-radius:16px;width:max-content;min-width:100%;box-shadow:0 12px 32px rgba(0,0,0,.17);}
.film-frame {width:190px;margin:0 8px;scroll-snap-align:start;}
.film-holes {height:9px;background:repeating-linear-gradient(90deg,#c59a55 0 9px,transparent 9px 18px);opacity:.7;margin:0 0 8px;}
.film-frame img {width:190px;height:225px;object-fit:cover;border:5px solid #1d1d1d;display:block;}
.film-caption {color:#e9d4b2;text-align:center;font-size:.78rem;padding:8px 4px 2px;white-space:normal;}

.polaroid {background:#fffdf9;border:1px solid rgba(0,0,0,.06);padding:10px 10px 23px;border-radius:5px;box-shadow:0 10px 28px rgba(56,39,28,.14);margin:8px 0 16px;}
.polaroid img {width:100%;height:300px;object-fit:cover;display:block;border-radius:2px;}
.polaroid-caption {padding:11px 5px 0;text-align:center;font:500 .98rem Georgia,serif;color:#574943;}

.location-card {background:#fffaf6;border:1px solid rgba(189,148,84,.18);border-radius:20px;padding:18px;margin-bottom:12px;}
.location-title {font:500 1.3rem Georgia,serif;}
.location-category {display:inline-block;color:#a56f6f;background:#f3dcd9;border-radius:999px;padding:4px 10px;font-size:.73rem;margin:.4rem 0;}
.location-phrase {color:#6d6059;font-style:italic;line-height:1.6;}

.question-num {width:38px;height:38px;border-radius:50%;background:#ecd2cf;color:#8f5f5d;display:flex;align-items:center;justify-content:center;font:500 1.1rem Georgia,serif;margin-bottom:8px;}
.reason-card {background:#fffaf6;border:1px solid rgba(189,148,84,.2);border-radius:19px;padding:18px;margin:8px 0;}
.reason-num {font:500 1.45rem Georgia,serif;color:#b17875;}
.reason-text {color:#50433f;line-height:1.6;margin-top:5px;}
.quote-strip {text-align:center;padding:24px 12px;font:italic 1.2rem Georgia,serif;color:#755b55;}

.stButton>button {border-radius:999px!important;border:1px solid rgba(158,108,91,.18)!important;background:linear-gradient(180deg,#da9b9b,#c97f83)!important;color:white!important;font-weight:650!important;min-height:42px;}
.stButton>button:hover {box-shadow:0 7px 20px rgba(168,101,103,.17);border-color:#b17072!important;}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {border-radius:14px!important;}
[data-baseweb="tab-list"] {gap:6px;background:rgba(255,251,247,.72);padding:6px;border-radius:18px;overflow-x:auto;}
[data-baseweb="tab"] {border-radius:13px;padding:9px 12px;white-space:nowrap;}
.small {font-size:.82rem;color:#81736b;}
.center {text-align:center;}




/* ==========================================================
   INTERFAZ MÓVIL + NAVEGACIÓN INFERIOR
   ========================================================== */
.mobile-topbar {
  display:flex; align-items:center; justify-content:space-between;
  padding:3px 2px 10px; color:#5d4a43;
}
.mobile-topbar-title {
  font-family:"Snell Roundhand","Apple Chancery","URW Chancery L","Segoe Script",cursive;
  font-size:1.65rem; color:#59453f;
}
.mobile-topbar-heart {font-size:1.25rem;color:#c98286;}
.mobile-page-title {
  font-family:Georgia,'Times New Roman',serif;
  font-size:1.75rem; color:#3b302c; margin:.2rem 0 .25rem;
}
.mobile-page-sub {color:#85756c;font-size:.9rem;line-height:1.5;margin-bottom:1rem;}
.home-cover {
  position:relative; overflow:hidden; border-radius:20px; height:205px;
  margin:4px 0 12px; box-shadow:0 10px 24px rgba(69,45,32,.10);
  background:#191615;
}
.home-cover img {
  width:100%; height:205px; object-fit:cover; object-position:center 38%; display:block;
  filter:brightness(.58) saturate(.72); opacity:.88;
}
.home-cover:after {
  content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(16,13,12,.08),rgba(16,13,12,.22) 52%,rgba(16,13,12,.68));
}
.home-cover-copy {position:absolute;z-index:2;left:18px;right:18px;bottom:16px;color:#fff7ef;}
.home-cover-copy .smallcap {font-size:.68rem;letter-spacing:.18em;text-transform:uppercase;color:#ead7bd;}
.home-cover-copy h1 {
  margin:.15rem 0 .15rem !important;
  font-family:"Snell Roundhand","Apple Chancery","URW Chancery L","Segoe Script",cursive !important;
  font-size:2.25rem !important;font-weight:400 !important;line-height:1 !important;
}
.home-cover-copy p {margin:0;color:#efe5db;font-size:.80rem;line-height:1.35;}
.compact-note {
  background:#f4ddd9;border-radius:14px;padding:14px 15px;margin:8px 0 12px;
  box-shadow:0 6px 16px rgba(81,53,42,.05);color:#5a4740;
}
.compact-note-title {font-family:Georgia,serif;font-size:1.04rem;margin-bottom:.3rem;}

.st-key-mobile_bottom_nav {
  position:fixed;
  left:50%;
  bottom:max(8px, env(safe-area-inset-bottom));
  transform:translateX(-50%);
  width:min(424px, calc(100vw - 16px));
  z-index:9999;
  padding:6px 6px 5px !important;
  background:rgba(252,247,240,.97);
  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  border:1px solid rgba(119,86,66,.13);
  border-radius:19px;
  box-shadow:0 10px 28px rgba(55,35,24,.16);
}
.st-key-mobile_bottom_nav [data-testid="stRadio"] > div {gap:0!important;}
.st-key-mobile_bottom_nav [role="radiogroup"] {
  display:flex!important;
  flex-wrap:nowrap!important;
  overflow-x:auto!important;
  gap:2px!important;
  scrollbar-width:none;
  justify-content:flex-start!important;
  padding:0!important;
}
.st-key-mobile_bottom_nav [role="radiogroup"]::-webkit-scrollbar {display:none;}
.st-key-mobile_bottom_nav [role="radiogroup"] label {
  flex:0 0 64px!important;
  min-width:64px!important;
  padding:6px 4px!important;
  border-radius:12px;
  margin:0!important;
  justify-content:center!important;
}
.st-key-mobile_bottom_nav [role="radiogroup"] label > div:first-child {display:none!important;}
.st-key-mobile_bottom_nav [role="radiogroup"] label p {
  font-size:.64rem!important;
  line-height:1.15!important;
  white-space:nowrap;
  color:#6c5d55!important;
  text-align:center!important;
  margin:0!important;
}
.st-key-mobile_bottom_nav [role="radiogroup"] label:has(input:checked) {background:#f0d9d6!important;}
.st-key-mobile_bottom_nav [role="radiogroup"] label:has(input:checked) p {color:#9c6667!important;font-weight:700!important;}


/* Login v4: estructura estable sin contenedores HTML abiertos */
.st-key-login_panel {
  max-width:372px;
  margin:8px auto 0;
  padding:14px 16px 20px !important;
  background:#171412;
  border-radius:22px;
  border:1px solid rgba(244,232,217,.12);
  box-shadow:0 18px 44px rgba(0,0,0,.16);
}
.login-photo-box {
  position:relative;
  height:215px;
  border-radius:17px;
  overflow:hidden;
  margin-bottom:17px;
  background:#111;
}
.login-photo-box img {
  width:100%;height:215px;object-fit:cover;object-position:center 34%;display:block;
  filter:brightness(.48) saturate(.68);opacity:.90;
}
.login-photo-box:after {
  content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(0,0,0,.10),rgba(0,0,0,.20) 45%,rgba(0,0,0,.62));
}
.login-photo-copy {position:absolute;z-index:2;left:12px;right:12px;top:28px;text-align:center;color:#f6ecdf;}
.login-photo-copy .sj {
  font-family:"Snell Roundhand","Apple Chancery","URW Chancery L","Segoe Script",cursive;
  font-size:4.2rem;line-height:.9;font-weight:400;text-shadow:0 3px 14px rgba(0,0,0,.35);
}
.login-photo-copy .story {font-family:Georgia,serif;font-size:1rem;margin-top:.2rem;}
.login-form-title {text-align:center;color:#efe5d9;font-family:Georgia,serif;font-size:1rem;margin:.1rem 0 .1rem;}
.login-form-hint {text-align:center;color:#ad9e91;font-size:.68rem;letter-spacing:.14em;margin-bottom:.35rem;}
.login-footer {text-align:center;color:#e7d8c8;font-family:"Snell Roundhand","Apple Chancery","URW Chancery L","Segoe Script",cursive;font-size:1.25rem;line-height:1.15;padding-top:12px;}
.st-key-login_panel [data-testid="stTextInput"] input {
  text-align:center!important;background:#211d1a!important;color:#f9f1e8!important;
  border:1px solid rgba(244,229,211,.24)!important;border-radius:9px!important;min-height:44px!important;
}
.st-key-login_panel [data-testid="stTextInput"] input::placeholder {color:#b9aa9d!important;}
.st-key-login_panel .stButton > button {
  background:#efe6dc!important;color:#2e2622!important;border-radius:9px!important;
  border:0!important;min-height:45px!important;font-family:Georgia,serif!important;letter-spacing:.08em!important;
}

/* Streamlit expander and inputs feel more like mobile cards */
[data-testid="stExpander"] {border-radius:16px!important;border-color:rgba(111,82,61,.10)!important;background:#fffaf5!important;}
[data-testid="stFileUploader"] {border-radius:16px!important;}

/* ==========================================================
   PORTADA / LOGIN — estilo oscuro tipo invitación
   ========================================================== */
.login-shell {max-width:372px;margin:10px auto 1rem;}
.login-card {
  position:relative; overflow:hidden; min-height:650px; border-radius:24px;
  box-shadow:0 22px 56px rgba(0,0,0,.18); border:1px solid rgba(244,232,217,.12);
}
.login-photo {
  position:absolute; inset:0; overflow:hidden; border-radius:24px;
}
.login-photo img {
  width:100%; height:100%; object-fit:cover; object-position:center 35%;
  filter:brightness(.26) saturate(.68) blur(.9px); transform:scale(1.04); opacity:.93;
}
.login-photo:after {
  content:""; position:absolute; inset:0;
  background:
    radial-gradient(circle at 50% 14%, rgba(255,245,229,.12), transparent 28%),
    linear-gradient(180deg, rgba(7,7,7,.14) 0%, rgba(11,11,11,.18) 22%, rgba(10,10,10,.32) 48%, rgba(10,10,10,.72) 78%, rgba(10,10,10,.86) 100%);
}
.login-inner {position:relative; z-index:2; padding:40px 26px 28px; color:#f6ecdd;}
.login-kicker {
  text-align:center; text-transform:uppercase; letter-spacing:.26em;
  font-size:.72rem; color:#dcc5a1; margin-bottom:.7rem;
}
.login-title {
  text-align:center;
  font-family:"Snell Roundhand","Apple Chancery","URW Chancery L","Brush Script MT","Segoe Script",cursive;
  font-size:clamp(4.1rem,11vw,5.5rem); line-height:.9; font-weight:400;
  color:#f8efe6; text-shadow:0 4px 18px rgba(0,0,0,.35);
}
.login-heart {text-align:center; font-size:1.12rem; color:#ead6b5; margin:.15rem 0 .15rem;}
.login-story {
  text-align:center; font-family:Georgia,'Times New Roman',serif; font-size:1.13rem;
  color:#f0e6da; letter-spacing:.02em;
}
.login-gap {height:150px;}
.login-label {
  text-align:center; font-family:Georgia,'Times New Roman',serif; font-size:1rem;
  color:#f0e5d8; margin-bottom:.28rem;
}
.login-hint {text-align:center; color:rgba(244,233,220,.66); font-size:.72rem; letter-spacing:.16em; margin-bottom:.25rem;}
.login-sep {text-align:center; color:#eadfce; padding-top:.6rem; font-family:Georgia,serif;}
.login-bottom {
  position:absolute; left:24px; right:24px; bottom:20px; z-index:2; text-align:center;
  color:#efe2d4; font-family:"Snell Roundhand","Apple Chancery","URW Chancery L","Brush Script MT","Segoe Script",cursive;
  font-size:1.42rem; line-height:1.18; text-shadow:0 2px 10px rgba(0,0,0,.45);
}
.login-bottom span {display:block; font-size:1rem; margin-top:.3rem; color:#ead8bb; font-family:Georgia,serif;}
.login-shell [data-testid="stTextInput"] input {
  text-align:center !important; min-height:46px !important; border-radius:9px !important;
  background:rgba(18,18,18,.22) !important; color:#fbf5eb !important;
  border:1px solid rgba(244,229,211,.35) !important; font-family:Georgia,'Times New Roman',serif !important;
}
.login-shell [data-testid="stTextInput"] input::placeholder {color:rgba(251,245,235,.68) !important;}
.login-shell .stButton > button {
  width:100%; min-height:47px !important; border-radius:9px !important;
  background:#f1e8dc !important; color:#2f2723 !important; border:1px solid rgba(255,255,255,.56) !important;
  font-family:Georgia,'Times New Roman',serif !important; font-weight:600 !important; letter-spacing:.08em !important;
  box-shadow:0 6px 18px rgba(0,0,0,.18);
}
.login-shell .stButton > button:hover {background:#fbf4ea !important; color:#241e1a !important;}
.login-shell [data-testid="stAlert"] {background:rgba(70,23,23,.80); color:white; border-radius:10px;}

@media(max-width:760px){
 .login-shell{max-width:360px}
 .login-card{min-height:630px;border-radius:20px}
 .login-photo,.login-photo img{border-radius:20px}
 .login-gap{height:145px}
 .login-title{font-size:4.25rem}
 .login-bottom{font-size:1.28rem;left:20px;right:20px}
 .block-container{padding-left:.85rem;padding-right:.85rem}.hero{padding:34px 18px 30px;border-radius:22px}
 .metric-shell{grid-template-columns:1fr}.polaroid img{height:260px}.film-frame,.film-frame img{width:160px}.film-frame img{height:200px}
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_TYPES = {".mp4", ".mov", ".m4v"}


def digits_only(value: str) -> str:
    return "".join(c for c in value if c.isdigit())


def read_json(path: Path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def write_json(path: Path, payload) -> bool:
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def image_uri(path: Path, max_side: int = 900) -> str | None:
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((max_side, max_side))
        from io import BytesIO
        buf = BytesIO()
        im.save(buf, format="JPEG", quality=84)
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None


def media_for_moment(moment: dict):
    folder = MOMENTS_DIR / moment["slug"]
    if not folder.exists():
        return [], []
    photos = sorted([p for p in folder.iterdir() if p.suffix.lower() in IMAGE_TYPES and p.name != "cover.jpg"])
    videos = sorted([p for p in folder.iterdir() if p.suffix.lower() in VIDEO_TYPES])
    return photos, videos


def cover_for(moment: dict) -> Path | None:
    p = MOMENTS_DIR / moment["slug"] / "cover.jpg"
    return p if p.exists() else None


def safe_filename(name: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return stem or "foto.jpg"


def save_bb_uploads(album: str, title: str, message: str, files) -> tuple[bool, int]:
    db = read_json(BB_MEMORY_DB, [])
    saved = 0
    try:
        for uploaded in files:
            ext = Path(uploaded.name).suffix.lower()
            if ext not in IMAGE_TYPES:
                continue
            new_name = f"{uuid.uuid4().hex[:10]}_{safe_filename(uploaded.name)}"
            target = BB_UPLOADS_DIR / new_name
            target.write_bytes(uploaded.getvalue())
            db.append({
                "id": uuid.uuid4().hex,
                "album": album,
                "title": title.strip() or "Un recuerdo de bb",
                "message": message.strip(),
                "file": str(target.relative_to(BASE_DIR)).replace("\\", "/"),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            })
            saved += 1
        ok = write_json(BB_MEMORY_DB, db)
        return ok, saved
    except Exception:
        return False, saved


def bb_uploads(album: str | None = None):
    records = read_json(BB_MEMORY_DB, [])
    if album is None:
        return records
    return [r for r in records if r.get("album") == album]


def polaroid(path: Path, caption: str):
    uri = image_uri(path)
    if not uri:
        return
    st.markdown(
        f'<div class="polaroid"><img src="{uri}"><div class="polaroid-caption">{caption}</div></div>',
        unsafe_allow_html=True,
    )


def polaroid_record(record: dict):
    p = BASE_DIR / record.get("file", "")
    if not p.exists():
        return
    caption = record.get("title") or "Un recuerdo de bb"
    if record.get("message"):
        caption += f" · {record['message']}"
    polaroid(p, caption)


def render_film_roll():
    frames = []
    for moment in MOMENTS:
        cover = cover_for(moment)
        if not cover:
            continue
        uri = image_uri(cover, 520)
        if not uri:
            continue
        frames.append(
            f'<div class="film-frame"><div class="film-holes"></div><img src="{uri}"><div class="film-caption">{moment["short"]}</div><div class="film-holes" style="margin:8px 0 0"></div></div>'
        )
    st.markdown(
        '<div class="film-wrap"><div class="film-roll">' + "".join(frames) + "</div></div>",
        unsafe_allow_html=True,
    )


def live_counter_component():
    components.html(
        """
        <div id="metrics" class="metric-shell"></div>
        <style>
          body{margin:0;background:transparent;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#322925}
          .metric-shell{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;padding:1px 0 5px}
          .metric-card{box-sizing:border-box;background:linear-gradient(180deg,#fffaf5,#f1e2d7);border:1px solid rgba(216,146,150,.22);border-radius:16px;padding:13px 7px;text-align:center;min-height:102px}
          .metric-big{font:500 1.65rem/1 Georgia,serif;color:#8c5f58;white-space:nowrap}.metric-label{margin-top:.4rem;color:#756861;font-size:.66rem;line-height:1.25}.metric-mini{margin-top:.35rem;color:#aa7973;font-size:.58rem;line-height:1.3}
        </style>
        <script>
        const start = new Date(2026, 2, 13, 0, 0, 0);
        const target = new Date(2026, 8, 13, 0, 0, 0);
        const dayMs = 86400000;
        function calendarParts(now){
          if(now < start) return {months:0, days:0};
          let months=(now.getFullYear()-start.getFullYear())*12+(now.getMonth()-start.getMonth());
          let anchor=new Date(start.getFullYear(), start.getMonth()+months, start.getDate());
          if(anchor>now){months--; anchor=new Date(start.getFullYear(), start.getMonth()+months, start.getDate());}
          const days=Math.floor((new Date(now.getFullYear(),now.getMonth(),now.getDate())-new Date(anchor.getFullYear(),anchor.getMonth(),anchor.getDate()))/dayMs);
          return {months,days};
        }
        function render(){
          const now=new Date();
          const daysTogether=Math.max(0,Math.floor((new Date(now.getFullYear(),now.getMonth(),now.getDate())-start)/dayMs));
          const parts=calendarParts(now);
          let diff=target-now;
          let countMain='♡', countMini='Ya llegamos';
          if(diff>0){
            const d=Math.floor(diff/dayMs); diff-=d*dayMs;
            const h=Math.floor(diff/3600000); diff-=h*3600000;
            const m=Math.floor(diff/60000); diff-=m*60000;
            const s=Math.floor(diff/1000);
            countMain=`${d}d`;
            countMini=`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
          }
          document.getElementById('metrics').innerHTML=`
            <div class="metric-card"><div class="metric-big">${daysTogether}</div><div class="metric-label">días juntos</div><div class="metric-mini">desde 13/03/26</div></div>
            <div class="metric-card"><div class="metric-big">${parts.months}m ${parts.days}d</div><div class="metric-label">siendo novios</div><div class="metric-mini">nuestro tiempo ♡</div></div>
            <div class="metric-card"><div class="metric-big">${countMain}</div><div class="metric-label">para 6 meses</div><div class="metric-mini">${countMini}</div></div>`;
        }
        render(); setInterval(render,1000);
        </script>
        """,
        height=112,
        scrolling=False,
    )


# ============================================================
# SESSION / LOGIN
# ============================================================

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "reason_selected" not in st.session_state:
    st.session_state.reason_selected = None

if not st.session_state.unlocked:
    login_cover = ASSETS_DIR / "login_cover_v4.jpg"
    login_uri = image_uri(login_cover, 1200) if login_cover.exists() else None

    with st.container(key="login_panel"):
        if login_uri:
            st.markdown(
                f"""
                <div class="login-photo-box">
                  <img src="{login_uri}" alt="S y J">
                  <div class="login-photo-copy">
                    <div class="sj">{INITIALS}</div>
                    <div style="font-size:1rem;color:#ead7bc">♡</div>
                    <div class="story">Nuestra historia</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"<div class='login-form-title' style='font-size:2rem'>{INITIALS} ♡</div>", unsafe_allow_html=True)

        st.markdown('<div class="login-form-title">Ingresa nuestra fecha</div><div class="login-form-hint">DÍA · MES · AÑO</div>', unsafe_allow_html=True)
        dcol, mcol, ycol = st.columns([1, 1, 1.35], gap="small")
        with dcol:
            login_day = st.text_input("Día", placeholder="13", max_chars=2, label_visibility="collapsed", key="login_day")
        with mcol:
            login_month = st.text_input("Mes", placeholder="03", max_chars=2, label_visibility="collapsed", key="login_month")
        with ycol:
            login_year = st.text_input("Año", placeholder="2026", max_chars=4, label_visibility="collapsed", key="login_year")

        if st.button("ENTRAR", use_container_width=True, key="login_enter"):
            code = f"{login_day}{login_month}{login_year}"
            if digits_only(code) == ACCESS_CODE:
                st.session_state.unlocked = True
                st.rerun()
            else:
                st.error("Mmm bb… esa no es nuestra fecha 👀♡")

        st.markdown('<div class="login-footer">Cada aventura nos trajo hasta aquí ♡</div>', unsafe_allow_html=True)

    st.stop()

# ============================================================
# MAIN APP
# ============================================================

# Navegación estilo app móvil. La barra queda fija en la parte inferior
# y se puede deslizar horizontalmente cuando la pantalla es pequeña.
NAV_OPTIONS = [
    "⌂ Inicio",
    "▣ Álbum",
    "⌖ Mapa",
    "? Preguntas",
    "♡ Razones",
    "✉ Carta",
]

with st.container(key="mobile_bottom_nav"):
    active_section = st.radio(
        "Navegación",
        NAV_OPTIONS,
        horizontal=True,
        label_visibility="collapsed",
        key="app_section",
    )

st.markdown(
    f"""
    <div class="mobile-topbar">
      <div class="mobile-topbar-title">S & J</div>
      <div class="mobile-topbar-heart">♡</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# INICIO
# ------------------------------------------------------------
if active_section == "⌂ Inicio":
    home_cover = ASSETS_DIR / "home_cover.jpg"
    home_uri = image_uri(home_cover, 1000) if home_cover.exists() else None

    if home_uri:
        st.markdown(
            f"""
            <div class="home-cover">
              <img src="{home_uri}" alt="S y J">
              <div class="home-cover-copy">
                <div class="smallcap">13 · 03 · 2026</div>
                <h1>S & J ♡</h1>
                <p>Un pedacito de nosotros, bb.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="mobile-page-title">Nuestro tiempo ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="mobile-page-sub">Lo que llevamos juntos y lo que falta para nuestros 6 meses.</div>', unsafe_allow_html=True)
    live_counter_component()

    st.markdown(
        '<div class="compact-note"><div class="compact-note-title">Cada momento cuenta ♡</div>'
        'No es solo cuánto tiempo llevamos; es todo lo que ya hemos vivido juntos.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="mobile-page-title" style="font-size:1.45rem">Nuestro rollo fotográfico</div>', unsafe_allow_html=True)
    st.markdown('<div class="mobile-page-sub">Desliza hacia los lados para recorrer nuestras salidas, viajes y momentos.</div>', unsafe_allow_html=True)
    render_film_roll()

    st.markdown(
        f"""
        <div class="paper-card" style="padding:16px 17px">
          <div style="font-family:Georgia,serif;font-size:1.05rem;margin-bottom:.35rem">Nuestro pequeño mundo ♡</div>
          <div class="small">Usa la barra de abajo para entrar al álbum, mapa, preguntas, razones o carta.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# ALBUM
# ------------------------------------------------------------
if active_section == "▣ Álbum":
    st.markdown('<div class="mobile-page-title">Nuestro álbum ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Cada lugar tiene su propia pequeña historia. Abre los recuerdos y recórrelos a tu ritmo.</div>', unsafe_allow_html=True)

    # Mini navegación por recuerdo
    moment_names = [m["title"] for m in MOMENTS]
    selected_name = st.selectbox("Ir directamente a un recuerdo", ["Ver todos"] + moment_names)
    filtered = MOMENTS if selected_name == "Ver todos" else [m for m in MOMENTS if m["title"] == selected_name]

    for n, moment in enumerate(filtered, 1):
        photos, videos = media_for_moment(moment)
        user_records = bb_uploads(moment["slug"])
        with st.expander(f"{moment['short']} · {moment['category']} ♡", expanded=(selected_name != "Ver todos" or n == 1)):
            st.markdown(
                f"""
                <div class="location-card">
                  <div class="location-title">{moment['title']}</div>
                  <div class="location-category">{moment['category']}</div>
                  <div class="location-phrase">“{moment['phrase']}”</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            all_photo_items = [(p, moment["short"]) for p in photos]
            cols = st.columns(2 if len(all_photo_items) > 1 else 1)
            for i, (photo, caption) in enumerate(all_photo_items):
                with cols[i % len(cols)]:
                    polaroid(photo, caption)

            if videos:
                st.markdown("**Un pedacito en movimiento 🎥**")
                for video in videos:
                    st.video(str(video))

            if user_records:
                st.markdown(f"**Fotos que {BB} agregó a este recuerdo ♡**")
                ucols = st.columns(2)
                for i, record in enumerate(user_records):
                    with ucols[i % 2]:
                        polaroid_record(record)

    # Fotos nuevas de ella
    st.write("")
    st.markdown('<div class="section-title">Agrega tus favoritas, bb ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Puedes sumar fotos tuyas que quieras guardar dentro de nuestro álbum.</div>', unsafe_allow_html=True)

    with st.form("bb_upload_form", clear_on_submit=True):
        album_label = st.selectbox(
            "¿A qué recuerdo pertenece?",
            ["Álbum general"] + [m["title"] for m in MOMENTS],
        )
        title = st.text_input("Ponle un nombre", placeholder="Ej. Una de mis fotos favoritas")
        message = st.text_area("¿Quieres escribir algo?", placeholder="Ej. Me encanta este día porque…", height=85)
        files = st.file_uploader("Sube una o varias fotos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        submitted = st.form_submit_button("Guardar en nuestro álbum ♡", use_container_width=True)

    if submitted:
        if not files:
            st.warning("Primero elige al menos una foto, bb ♡")
        else:
            slug_by_title = {m["title"]: m["slug"] for m in MOMENTS}
            album = "general" if album_label == "Álbum general" else slug_by_title[album_label]
            ok, saved = save_bb_uploads(album, title, message, files)
            if ok and saved:
                st.success(f"Listo bb ♡ Guardé {saved} foto(s) en nuestro álbum.")
                st.rerun()
            else:
                st.error("No pude guardar las fotos en el disco de esta versión. Más adelante podemos conectarlo a Supabase para que queden guardadas en la nube.")

    general_records = bb_uploads("general")
    if general_records:
        st.markdown("### Las favoritas que bb agregó ♡")
        gcols = st.columns(3)
        for i, record in enumerate(general_records):
            with gcols[i % 3]:
                polaroid_record(record)

# ------------------------------------------------------------
# MAPA
# ------------------------------------------------------------
if active_section == "⌖ Mapa":
    st.markdown('<div class="mobile-page-title">Nuestro mapa ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Cada punto es una historia que ya podemos volver a visitar. Los lugares privados no aparecen por ubicación.</div>', unsafe_allow_html=True)

    mapped = [m for m in MOMENTS if m.get("coords")]
    df = pd.DataFrame([
        {"lat": m["coords"][0], "lon": m["coords"][1], "Lugar": m["title"]}
        for m in mapped
    ])
    st.map(df, latitude="lat", longitude="lon", size=90, zoom=5)

    place = st.selectbox("Explora un punto del mapa", [m["title"] for m in mapped], key="map_place")
    chosen = next(m for m in mapped if m["title"] == place)
    cover = cover_for(chosen)
    c1, c2 = st.columns([.8, 1.2])
    with c1:
        if cover:
            polaroid(cover, chosen["short"])
    with c2:
        st.markdown(
            f"""
            <div class="paper-card">
              <h3 style="margin-top:0">{chosen['title']}</h3>
              <p style="font-family:Georgia,serif;font-style:italic">“{chosen['phrase']}”</p>
              <p class="small">Cada lugar, un recuerdo. Cada recuerdo, tú y yo. ♡</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info("TopGolf y nuestra primera salida todavía no tienen ubicación exacta en el mapa. En cuanto me digas dónde fueron, los agregamos. La comida en el depa se mantiene privada a propósito.")

# ------------------------------------------------------------
# 5 PREGUNTAS
# ------------------------------------------------------------
if active_section == "? Preguntas":
    st.markdown(f'<div class="mobile-page-title">5 preguntas para ti, {BB} ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">No es un examen. Solo quiero saber cómo se ve nuestra historia desde tus ojos.</div>', unsafe_allow_html=True)

    saved_answers = read_json(ANSWERS_DB, {})
    with st.form("questions_form"):
        responses = {}
        for i, q in enumerate(QUESTIONS, 1):
            st.markdown(f'<div class="question-num">{i}</div><b>{q}</b>', unsafe_allow_html=True)
            responses[str(i)] = st.text_area(
                f"Respuesta {i}",
                value=saved_answers.get(str(i), ""),
                placeholder="Escribe aquí lo que piensas…",
                height=95,
                label_visibility="collapsed",
                key=f"question_{i}",
            )
            st.write("")
        save_answers = st.form_submit_button("Guardar mis respuestas ♡", use_container_width=True)

    if save_answers:
        if write_json(ANSWERS_DB, responses):
            st.success("Ya quedaron guardadas, bb ♡ Estas respuestas también son parte de nuestra historia.")
        else:
            st.error("No pude guardar las respuestas en el disco de esta versión.")

# ------------------------------------------------------------
# 10 RAZONES
# ------------------------------------------------------------
if active_section == "♡ Razones":
    st.markdown('<div class="mobile-page-title">10 razones por las que amo estar contigo ♡</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Toca un corazón, {BB}. No quiero que las leas todas de golpe.</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for i in range(10):
        with cols[i % 5]:
            if st.button(f"♡ {i+1}", key=f"reason_{i}", use_container_width=True):
                st.session_state.reason_selected = i

    if st.session_state.reason_selected is None:
        st.markdown('<div class="scrap-note"><h3>Hay 10 pequeños mensajes escondidos aquí ♡</h3><p class="center">Elige el corazón que quieras abrir primero.</p></div>', unsafe_allow_html=True)
    else:
        i = st.session_state.reason_selected
        st.markdown(
            f"""
            <div class="reason-card">
              <div class="reason-num">Razón #{i+1}</div>
              <div class="reason-text">{REASONS[i]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------
# CARTA
# ------------------------------------------------------------
if active_section == "✉ Carta":
    st.markdown(f'<div class="mobile-page-title">Para ti, {BB} ♡</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Una última página antes de seguir escribiendo las siguientes.</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="scrap-note">
          <h3>Mi bb,</h3>
          <p>Quise hacer esto porque seis meses pueden parecer solo una fecha, pero cuando pienso en todo lo que hemos vivido dentro de ese tiempo, para mí significa muchísimo más.</p>
          <p>Me gustan nuestros viajes y nuestras salidas, pero también me gustan los momentos normales: comer juntos, platicar, reírnos, estar cansados y aun así querer compartir el rato.</p>
          <p>No somos perfectos, pero nuestra historia es mi favorita. Gracias por cada aventura, por cada foto y por todo lo que todavía nos falta conocer juntos.</p>
          <p>Porque lo mejor apenas comienza… ♡</p>
          <p style="text-align:right;font-family:Georgia,serif;font-size:1.08rem">— J</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        """
        <div class="paper-card center">
          <h3>Nuestro próximo capítulo</h3>
          <p>13 de septiembre de 2026 · 6 meses juntos ♡</p>
          <p class="small">Y después… otro mes, otro viaje, otra foto, otra historia.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

