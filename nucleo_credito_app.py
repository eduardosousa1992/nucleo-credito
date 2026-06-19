import re
import streamlit as st
import os, hashlib, hmac
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cryptography.fernet import Fernet
import base64

# ── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Núcleo Crédito",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETA ───────────────────────────────────────────────────────────────────
NAVY   = "#1B3A6B"
GREEN  = "#1A7A5E"
RED    = "#C0392B"
YELLOW = "#E67E22"
LIGHT  = "#F7F9FC"

# ── CSS PREMIUM ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {{ font-family: 'Inter', sans-serif !important; }}

/* ── FUNDO GERAL ── */
.stApp {{
    background: #0A1628 !important;
}}
[data-testid="stAppViewContainer"] {{
    background: #0A1628 !important;
}}
[data-testid="stAppViewContainer"] > .main {{
    background: #0A1628 !important;
}}
.main .block-container {{
    background: transparent !important;
    padding: 1rem 1.5rem !important;
    max-width: 100% !important;
}}

/* ── ESCONDE ELEMENTOS NATIVOS ── */
header[data-testid="stHeader"] {{ display: none !important; }}
footer {{ display: none !important; }}
#MainMenu {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}

/* ── SIDEBAR ESTÁTICA — NUNCA SOME ── */
[data-testid="stSidebar"],
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0D1B35 0%, #0A1628 100%) !important;
    border-right: 1px solid rgba(26,122,94,0.25) !important;
    min-width: 240px !important;
    max-width: 240px !important;
    width: 240px !important;
    transform: translateX(0px) !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}}
/* Mobile: sidebar colapsável */
@media (max-width: 768px) {{

    [data-testid="stSidebarCollapseButton"] {{
        display: flex !important;
        visibility: visible !important;
        pointer-events: all !important;
    }}
    [data-testid="collapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        pointer-events: all !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 1000 !important;
        background: #1A7A5E !important;
        border-radius: 8px !important;
        width: 40px !important;
        height: 40px !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
    }}
    .main .block-container {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100vw !important;
    }}
    [data-testid="stHorizontalBlock"] {{
        flex-direction: column !important;
        gap: 8px !important;
    }}
    [data-testid="column"] {{
        width: 100% !important;
        min-width: 100% !important;
    }}
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    width: 240px !important;
}}

/* Desktop: esconde botão de colapso da sidebar */
@media (min-width: 769px) {{
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[title="Close sidebar"],
    button[title="Collapse sidebar"] {{
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }}
}}
/* Mobile: estiliza botão nativo e esconde texto feio */
@media (max-width: 768px) {{
    [data-testid="collapsedControl"] {{
        background: #1A7A5E !important;
        border-radius: 10px !important;
        width: 44px !important;
        height: 44px !important;
        overflow: hidden !important;
        font-size: 0 !important;
        color: transparent !important;
    }}
    [data-testid="collapsedControl"] * {{
        font-size: 0 !important;
        color: transparent !important;
    }}
    [data-testid="collapsedControl"] svg {{
        width: 22px !important;
        height: 22px !important;
        fill: white !important;
        color: white !important;
        font-size: 22px !important;
    }}
    [data-testid="stSidebarCollapseButton"] button {{
        background: rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebarCollapseButton"] svg {{
        fill: white !important;
    }}
}}


/* ── FILE UPLOADER PREMIUM ── */
[data-testid="stFileUploader"] > label {{
    display: none !important;
}}
[data-testid="stFileUploader"] section {{
    background: rgba(26,122,94,0.06) !important;
    border: 1.5px solid rgba(26,122,94,0.3) !important;
    border-radius: 10px !important;
    padding: 6px 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 52px !important;
    height: 52px !important;
    cursor: pointer !important;
}}
[data-testid="stFileUploader"] section:hover {{
    border-color: #4ADE80 !important;
    background: rgba(74,222,128,0.1) !important;
}}
[data-testid="stFileUploader"] section > div {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
[data-testid="stFileUploader"] section button {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 36px !important;
    height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
[data-testid="stFileUploader"] section button p {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
}}
[data-testid="stFileUploader"] section button::after {{
    content: "📎" !important;
    font-size: 22px !important;
    line-height: 1 !important;
}}
[data-testid="stFileUploader"] section > div > span {{
    display: none !important;
}}
[data-testid="stFileUploader"] section small {{
    display: none !important;
}}
[data-testid="stFileUploaderFile"] {{
    background: rgba(74,222,128,0.06) !important;
    border: 1px solid rgba(74,222,128,0.2) !important;
    border-radius: 8px !important;
    padding: 6px 10px !important;
    margin-top: 6px !important;
}}

/* ── SIDEBAR RADIO MENU ── */
[data-testid="stSidebar"] .stRadio > label {{ display: none !important; }}
[data-testid="stSidebar"] .stRadio label {{
    color: rgba(255,255,255,0.6) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 9px 16px !important;
    border-radius: 8px !important;
    display: block !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    margin: 1px 8px !important;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    background: rgba(26,122,94,0.2) !important;
    color: white !important;
}}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {{
    display: none !important;
}}
[data-testid="stSidebar"] .stRadio p {{
    color: inherit !important;
    font-size: 13px !important;
    margin: 0 !important;
}}
[data-testid="stSidebar"] .stRadio [aria-checked="true"] label {{
    background: rgba(26,122,94,0.25) !important;
    color: #4ADE80 !important;
    font-weight: 700 !important;
    border-left: 3px solid #1A7A5E !important;
}}

/* ── KPI CARDS ── */
.kpi-card {{
    background: linear-gradient(135deg, #0D1B35 0%, #0F2040 100%) !important;
    border: 1px solid rgba(26,122,94,0.2) !important;
    border-radius: 14px !important;
    padding: 16px 12px 12px !important;
    text-align: center !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
}}

/* ── CHART CARDS ── */
.chart-card {{
    background: #0D1B35 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
}}
.chart-title {{
    font-size: 13px !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,0.9) !important;
    margin-bottom: 14px !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}}

/* ── PAGE HEADER ── */
.page-header {{
    background: linear-gradient(135deg, #0D1B35 0%, #0F2040 100%) !important;
    border: 1px solid rgba(26,122,94,0.3) !important;
    border-left: 4px solid #1A7A5E !important;
    border-radius: 14px !important;
    padding: 20px 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
}}
.page-header h2 {{ color: white !important; font-size: 18px !important; font-weight: 800 !important; margin: 0 0 3px !important; }}
.page-header p {{ color: rgba(255,255,255,0.45) !important; font-size: 12px !important; margin: 0 !important; }}

/* ── BRAND TOPBAR ── */
.brand-topbar {{
    background: linear-gradient(90deg, #0D1B35 0%, #0F2040 100%) !important;
    border: 1px solid rgba(26,122,94,0.2) !important;
    border-radius: 14px !important;
    padding: 14px 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
}}
.brand-topbar-title {{ color: white !important; font-size: 16px !important; font-weight: 800 !important; }}
.brand-topbar-sub {{ color: rgba(255,255,255,0.4) !important; font-size: 10px !important; font-style: italic !important; }}
.brand-topbar-right {{ color: rgba(255,255,255,0.5) !important; font-size: 12px !important; }}

/* ── ALERT BOXES ── */
.alert-opp {{
    background: linear-gradient(135deg, #0D2B1F, #0A2318) !important;
    border: 1px solid rgba(26,122,94,0.4) !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
}}
.alert-urgent {{
    background: linear-gradient(135deg, #2B1A0D, #231408) !important;
    border: 1px solid rgba(230,126,34,0.4) !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
}}
.alert-name {{ font-size: 14px !important; font-weight: 700 !important; color: white !important; }}
.alert-sub {{ font-size: 11px !important; color: rgba(255,255,255,0.5) !important; margin-top: 2px !important; }}
.alert-value {{ font-size: 22px !important; font-weight: 800 !important; color: #4ADE80 !important; }}
.alert-value-label {{ font-size: 10px !important; color: rgba(255,255,255,0.4) !important; }}
.alert-row {{ display: flex !important; justify-content: space-between !important; align-items: flex-start !important; }}

/* ── BADGE ── */
.badge {{ display: inline-block !important; padding: 2px 9px !important; border-radius: 99px !important; font-size: 10px !important; font-weight: 700 !important; margin-right: 4px !important; }}
.b-green  {{ background: rgba(74,222,128,0.15) !important; color: #4ADE80 !important; }}
.b-yellow {{ background: rgba(251,191,36,0.15) !important; color: #FBB724 !important; }}
.b-red    {{ background: rgba(239,68,68,0.15) !important; color: #EF4444 !important; }}
.b-blue   {{ background: rgba(96,165,250,0.15) !important; color: #60A5FA !important; }}
.b-slate  {{ background: rgba(255,255,255,0.08) !important; color: rgba(255,255,255,0.7) !important; }}

/* ── CLIENTE CARD ── */
.cli-card {{
    background: #0D1B35 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 8px !important;
    border-left: 4px solid rgba(255,255,255,0.1) !important;
}}
.cli-card.opp    {{ border-left-color: #1A7A5E !important; }}
.cli-card.warn   {{ border-left-color: #E67E22 !important; }}
.cli-card.danger {{ border-left-color: #E74C3C !important; }}

/* ── KANBAN ── */
.kanban-col {{
    background: #0D1B35 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    min-height: 120px !important;
}}
.kanban-header {{ font-size: 12px !important; font-weight: 700 !important; margin-bottom: 10px !important; display: flex !important; align-items: center !important; justify-content: space-between !important; }}
.kanban-card {{
    background: rgba(255,255,255,0.05) !important;
    border-radius: 9px !important;
    padding: 10px 12px !important;
    margin-bottom: 8px !important;
    border-left: 3px solid rgba(255,255,255,0.1) !important;
}}

/* ── META BAR ── */
.meta-bar-wrap {{
    background: #0D1B35 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
    margin-bottom: 10px !important;
}}
.meta-bar-track {{ background: rgba(255,255,255,0.08) !important; border-radius: 99px !important; height: 10px !important; overflow: hidden !important; margin: 8px 0 4px !important; }}
.meta-bar-fill {{ height: 100% !important; border-radius: 99px !important; }}

/* ── PROGRESS BAR ── */
.progress-bar-wrap {{ background: rgba(255,255,255,0.08) !important; border-radius: 99px !important; height: 6px !important; overflow: hidden !important; margin-top: 6px !important; }}
.progress-bar-fill {{ height: 100% !important; border-radius: 99px !important; }}
.hist-item {{ background: rgba(255,255,255,0.05) !important; border-radius: 9px !important; padding: 9px 13px !important; margin-bottom: 6px !important; border-left: 3px solid #1A7A5E !important; font-size: 12px !important; }}
.hist-meta {{ font-size: 10px !important; color: rgba(255,255,255,0.4) !important; margin-bottom: 3px !important; }}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 9px !important;
    color: white !important;
    font-size: 13px !important;
}}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{
    color: rgba(255,255,255,0.3) !important;
}}
.stSelectbox > div > div {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 9px !important;
    color: white !important;
}}
.stSelectbox svg {{ fill: rgba(255,255,255,0.5) !important; }}

/* ── LABELS ── */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stTextArea label, .stDateInput label, .stCheckbox label,
.stMultiSelect label, .stSlider label, .stRadio label {{
    color: rgba(255,255,255,0.7) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}}

/* ── BOTÕES ── */
.stButton > button {{
    background: linear-gradient(135deg, #1A7A5E 0%, #156B51 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 9px 18px !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(26,122,94,0.3) !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #1E8C6B 0%, #1A7A5E 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(26,122,94,0.4) !important;
}}

/* ── EXPANDER ── */
.streamlit-expanderHeader {{
    background: #0D1B35 !important;
    color: white !important;
    border-radius: 9px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}}
.streamlit-expanderContent {{
    background: #0A1628 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-top: none !important;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    gap: 8px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: rgba(255,255,255,0.06) !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,0.6) !important;
    font-weight: 500 !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background: rgba(26,122,94,0.3) !important;
    color: #4ADE80 !important;
    font-weight: 700 !important;
}}

/* ── DATAFRAME ── */
.stDataFrame {{ border-radius: 10px !important; overflow: hidden !important; }}
.stDataFrame thead th {{
    background: #0D1B35 !important;
    color: rgba(255,255,255,0.7) !important;
}}

/* ── INFO/SUCCESS/ERROR ── */
.stInfo {{ background: rgba(96,165,250,0.1) !important; border-color: rgba(96,165,250,0.3) !important; color: #93C5FD !important; }}
.stSuccess {{ background: rgba(74,222,128,0.1) !important; border-color: rgba(74,222,128,0.3) !important; color: #4ADE80 !important; }}
.stError {{ background: rgba(239,68,68,0.1) !important; border-color: rgba(239,68,68,0.3) !important; color: #FCA5A5 !important; }}
.stWarning {{ background: rgba(251,191,36,0.1) !important; border-color: rgba(251,191,36,0.3) !important; color: #FCD34D !important; }}

/* ── METRICS (KPI fallback) ── */
[data-testid="stMetric"] {{
    background: #0D1B35 !important;
    border: 1px solid rgba(26,122,94,0.2) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}}
[data-testid="stMetricLabel"] {{ color: rgba(255,255,255,0.5) !important; font-size: 10px !important; }}
[data-testid="stMetricValue"] {{ color: white !important; font-weight: 800 !important; }}

/* ── LOGIN ── */
.login-wrap {{
    background: linear-gradient(135deg, #0D1B35 0%, #0A1628 100%) !important;
    border: 1px solid rgba(26,122,94,0.3) !important;
    border-radius: 20px !important;
    padding: 40px 36px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5) !important;
    text-align: center !important;
}}
</style>
""", unsafe_allow_html=True)# ── SECRETS ──────────────────────────────────────────────────────────────────
def gs(key, default=""):
    try:
        v = st.secrets.get(key)
        if v: return str(v)
    except: pass
    return os.environ.get(key, default)

SUPABASE_URL  = gs("SUPABASE_URL")
SUPABASE_KEY  = gs("SUPABASE_KEY")
BREVO_KEY     = gs("BREVO_API_KEY")
SENDER_EMAIL  = gs("SENDER_EMAIL", "nucleocastelo.credito@gmail.com")
SENDER_NAME   = gs("SENDER_NAME",  "Núcleo Crédito")

# ── SUPABASE (lazy) ───────────────────────────────────────────────────────────
@st.cache_resource
def get_sb():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

sb = get_sb()

# ── CRIPTO ────────────────────────────────────────────────────────────────────
def _fernet():
    k = gs("ENCRYPT_KEY", "")
    if k: return Fernet(k.encode())
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(b"nucleo2026_sec").digest()))

def enc(t):
    if not t: return ""
    try: return _fernet().encrypt(str(t).encode()).decode()
    except: return t

def dec(t):
    if not t: return ""
    try: return _fernet().decrypt(str(t).encode()).decode()
    except: return t

def mask_cpf(c):
    """Máscara parcial: 621.XXX.XXX-12 — primeiros 3 e últimos 2 visíveis"""
    d = "".join(filter(str.isdigit, c or ""))
    if len(d) == 11:
        return f"{d[0:3]}.XXX.XXX-{d[9:11]}"
    return "XXX.XXX.XXX-XX"

def mask_tel(t):
    """Máscara parcial: (86) 952-XXX-015 — DDD + 3 primeiros + 3 últimos"""
    d = "".join(filter(str.isdigit, t or ""))
    if len(d) == 11:
        return f"({d[0:2]}) {d[2:5]}-XXX-{d[8:11]}"
    elif len(d) == 10:
        return f"({d[0:2]}) {d[2:5]}-XX-{d[7:10]}"
    return "(XX) XXX-XXX-XXX"

# ── INSS 2026 ────────────────────────────────────────────────────────────────
INSS = {
    1:{"jan":"2026-01-26","fev":"2026-02-23","mar":"2026-03-25","abr":"2026-04-24","mai":"2026-05-25","jun":"2026-06-24","jul":"2026-07-24","ago":"2026-08-24","set":"2026-09-24","out":"2026-10-26","nov":"2026-11-24","dez":"2026-12-22"},
    2:{"jan":"2026-01-27","fev":"2026-02-24","mar":"2026-03-26","abr":"2026-04-27","mai":"2026-05-26","jun":"2026-06-25","jul":"2026-07-28","ago":"2026-08-26","set":"2026-09-25","out":"2026-10-27","nov":"2026-11-25","dez":"2026-12-23"},
    3:{"jan":"2026-01-28","fev":"2026-02-25","mar":"2026-03-27","abr":"2026-04-28","mai":"2026-05-27","jun":"2026-06-26","jul":"2026-07-29","ago":"2026-08-27","set":"2026-09-28","out":"2026-10-28","nov":"2026-11-26","dez":"2026-12-24"},
    4:{"jan":"2026-01-29","fev":"2026-02-26","mar":"2026-03-30","abr":"2026-04-29","mai":"2026-05-28","jun":"2026-06-29","jul":"2026-07-30","ago":"2026-08-28","set":"2026-09-29","out":"2026-10-29","nov":"2026-11-27","dez":"2026-12-29"},
    5:{"jan":"2026-01-30","fev":"2026-02-27","mar":"2026-03-31","abr":"2026-04-30","mai":"2026-05-29","jun":"2026-06-30","jul":"2026-07-31","ago":"2026-08-31","set":"2026-09-30","out":"2026-10-30","nov":"2026-11-30","dez":"2026-12-30"},
    6:{"jan":"2026-02-02","fev":"2026-03-02","mar":"2026-04-01","abr":"2026-05-04","mai":"2026-06-01","jun":"2026-07-01","jul":"2026-08-03","ago":"2026-09-01","set":"2026-10-01","out":"2026-11-02","nov":"2026-12-01","dez":"2026-12-30"},
    7:{"jan":"2026-02-03","fev":"2026-03-03","mar":"2026-04-02","abr":"2026-05-05","mai":"2026-06-02","jun":"2026-07-02","jul":"2026-08-04","ago":"2026-09-02","set":"2026-10-02","out":"2026-11-04","nov":"2026-12-02","dez":"2026-12-30"},
    8:{"jan":"2026-02-05","fev":"2026-03-05","mar":"2026-04-02","abr":"2026-05-06","mai":"2026-06-03","jun":"2026-07-03","jul":"2026-08-05","ago":"2026-09-03","set":"2026-10-05","out":"2026-11-05","nov":"2026-12-03","dez":"2026-12-30"},
    9:{"jan":"2026-02-07","fev":"2026-03-07","mar":"2026-04-07","abr":"2026-05-07","mai":"2026-06-05","jun":"2026-07-06","jul":"2026-08-06","ago":"2026-09-04","set":"2026-10-06","out":"2026-11-06","nov":"2026-12-04","dez":"2026-12-30"},
    0:{"jan":"2026-02-08","fev":"2026-03-08","mar":"2026-04-08","abr":"2026-05-08","mai":"2026-06-06","jun":"2026-07-07","jul":"2026-08-07","ago":"2026-09-08","set":"2026-10-07","out":"2026-11-09","nov":"2026-12-05","dez":"2026-12-30"},
}
MESES = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

def prox_pg(cpf_raw):
    try:
        d = "".join(filter(str.isdigit, cpf_raw or ""))
        if not d: return None, None
        u = int(d[-1]); hoje = date.today()
        mes = MESES[hoje.month - 1]
        if u in INSS and mes in INSS[u]:
            pg = datetime.strptime(INSS[u][mes], "%Y-%m-%d").date()
            if pg < hoje:
                pm = MESES[hoje.month % 12]
                if pm in INSS[u]:
                    pg = datetime.strptime(INSS[u][pm], "%Y-%m-%d").date()
            return pg, (pg - hoje).days
    except: pass
    return None, None

# ── SCORE ─────────────────────────────────────────────────────────────────────
def calc_score(row):
    s = 0
    tipo_ben = row.get("tipo_beneficio","") or ""
    eh_bpc = "BPC" in tipo_ben or "LOAS" in tipo_ben
    # BPC margem 35%, demais 40%
    pct_margem = 0.35 if eh_bpc else 0.40
    beneficio = float(row.get("beneficio", 0) or 0)
    parcelas  = float(row.get("parcelas", 0) or 0)
    m = round(beneficio * pct_margem - parcelas, 2)
    row["margem"] = m  # atualiza para uso posterior
    if m > 600: s += 40
    elif m > 300: s += 30
    elif m > 100: s += 15
    s += {"Ativo":20,"Lead Quente":25,"Em análise":15}.get(row.get("status",""), 0)
    s += {"Indicação":20,"WhatsApp":15,"Rádio":12,"Panfletagem":10,"Google":12,"Instagram":8}.get(row.get("canal",""), 5)
    _, dias = prox_pg(row.get("cpf_raw",""))
    if dias is not None:
        if 0 <= dias <= 2: s += 15
        elif 3 <= dias <= 5: s += 10
    return min(s, 100)

# ── DB ────────────────────────────────────────────────────────────────────────
def load_clientes():
    if not sb: return pd.DataFrame()
    try:
        r = sb.table("clientes").select("*").order("created_at", desc=True).execute()
        if not r.data: return pd.DataFrame()
        df = pd.DataFrame(r.data)
        df["cpf_raw"] = df["cpf"].apply(lambda x: dec(x) if x else "")
        df["tel_raw"] = df["telefone"].apply(lambda x: dec(x) if x else "")
        df["cpf_d"]   = df["cpf_raw"].apply(mask_cpf)
        df["tel_d"]   = df["tel_raw"].apply(mask_tel)
        def calc_margem(r):
            eh_bpc = "BPC" in str(r.get("tipo_beneficio","")) or "LOAS" in str(r.get("tipo_beneficio",""))
            pct = 0.35 if eh_bpc else 0.40
            return round(float(r["beneficio"])*pct - float(r["parcelas"]), 2)
        df["margem"]  = df.apply(calc_margem, axis=1)
        def calc_pct(r):
            if r["beneficio"] <= 0: return 0
            eh_bpc = "BPC" in str(r.get("tipo_beneficio","")) or "LOAS" in str(r.get("tipo_beneficio",""))
            pct = 0.35 if eh_bpc else 0.40
            return min(100, round(float(r["parcelas"])/(float(r["beneficio"])*pct)*100, 1))
        df["pct"] = df.apply(calc_pct, axis=1)
        df["score"]   = df.apply(calc_score, axis=1)
        df["prox"], df["dias"] = zip(*df.apply(lambda r: prox_pg(r["cpf_raw"]), axis=1))
        return df
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")
        return pd.DataFrame()

def load_leads():
    if not sb: return pd.DataFrame()
    try:
        r = sb.table("leads").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except: return pd.DataFrame()

def load_contratos():
    if not sb: return pd.DataFrame()
    try:
        r = sb.table("contratos").select("*, clientes(nome)").order("created_at", desc=True).execute()
        if not r.data: return pd.DataFrame()
        df = pd.DataFrame(r.data)
        df["cliente_nome"] = df["clientes"].apply(lambda x: x["nome"] if isinstance(x, dict) else "")
        return df
    except: return pd.DataFrame()

def load_hist(cid):
    if not sb: return pd.DataFrame()
    try:
        r = sb.table("historico").select("*").eq("cliente_id", cid).order("created_at", desc=True).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except: return pd.DataFrame()

def load_fu():
    if not sb: return pd.DataFrame()
    try:
        r = sb.table("followups").select("*, clientes(nome)").order("data_followup").execute()
        if not r.data: return pd.DataFrame()
        df = pd.DataFrame(r.data)
        df["cliente_nome"] = df["clientes"].apply(lambda x: x["nome"] if isinstance(x, dict) else "")
        return df
    except: return pd.DataFrame()

def ins_cli(d):
    d["cpf"] = enc(d.get("cpf", ""))
    d["telefone"] = enc(d.get("telefone", ""))
    sb.table("clientes").insert(d).execute()

def upd_cli(id, d):
    """Atualiza dados do cliente — edição completa"""
    if "cpf" in d and d["cpf"]: d["cpf"] = enc(d["cpf"])
    if "telefone" in d and d["telefone"]: d["telefone"] = enc(d["telefone"])
    sb.table("clientes").update(d).eq("id", id).execute()

def converter_lead_para_cliente(lead_row):
    """Migra dados do lead para a tabela clientes e arquiva o lead"""
    d = {
        "nome":      lead_row.get("nome", ""),
        "telefone":  lead_row.get("telefone", ""),
        "email":     lead_row.get("email", ""),
        "canal":     lead_row.get("canal", ""),
        "interesse": lead_row.get("interesse", ""),
        "beneficio": float(lead_row.get("beneficio", 0) or 0),
        "parcelas":  0.0,
        "status":    "Ativo",
        "observacoes": f"Convertido do funil em {date.today().strftime('%d/%m/%Y')}. {lead_row.get('observacoes','')}"
    }
    ins_cli(d)
    # Arquiva o lead: marca como Convertido e move para etapa final
    # Lead fica arquivado — não some do histórico, mas sai do funil ativo
    sb.table("leads").update({
        "etapa": "Contrato Pago",
        "status": "Convertido",
        "temperatura": "Convertido"
    }).eq("id", int(lead_row["id"])).execute()

def ins_lead(d):   sb.table("leads").insert(d).execute()
def ins_hist(d):   sb.table("historico").insert(d).execute()
def ins_fu(d):     sb.table("followups").insert(d).execute()
def ins_ct(d):     sb.table("contratos").insert(d).execute()
def upd_lead(id, s): sb.table("leads").update({"status": s}).eq("id", id).execute()

def upd_lead_etapa(id, etapa, extra=None):
    d = {"etapa": etapa, "updated_at": datetime.now().isoformat()}
    if extra: d.update(extra)
    sb.table("leads").update(d).eq("id", id).execute()

def load_alertas():
    if not sb: return pd.DataFrame()
    try:
        r = sb.table("alertas").select("*").eq("lido", False).order("criado_em", desc=True).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except: return pd.DataFrame()

def marcar_alerta_lido(id):
    if sb: sb.table("alertas").update({"lido": True}).eq("id", id).execute()

def gerar_alertas_automaticos(df_cli, df_leads):
    """Gera alertas automáticos baseados em regras de negócio"""
    if not sb: return
    alertas = []
    agora = datetime.now()

    # Leads parados há mais de 24h
    if not df_leads.empty and "updated_at" in df_leads.columns:
        for _, row in df_leads.iterrows():
            try:
                upd = pd.to_datetime(row.get("updated_at"))
                if upd and hasattr(upd, 'tzinfo'):
                    upd = upd.tz_localize(None) if upd.tzinfo else upd
                if upd:
                    horas = (agora - upd).total_seconds() / 3600
                    etapa = row.get("etapa", row.get("status", ""))
                    if horas > 48 and etapa not in ["Convertido", "Perdido", "Pago"]:
                        alertas.append({
                            "tipo": "lead_parado",
                            "titulo": f"Lead parado: {row['nome']}",
                            "descricao": f"Sem atualização há {int(horas)}h — Etapa: {etapa}",
                            "entidade": "lead",
                            "entidade_id": int(row["id"]),
                            "prioridade": "alta" if horas > 96 else "media"
                        })
            except: pass

    # Clientes com INSS em 2 dias e margem disponível
    if not df_cli.empty:
        for _, row in df_cli.iterrows():
            try:
                dias = row.get("dias")
                if dias is not None and 0 <= float(dias) <= 2 and row.get("margem", 0) > 200:
                    alertas.append({
                        "tipo": "inss_oportunidade",
                        "titulo": f"INSS em {int(dias)} dia(s): {row['nome'].split()[0]}",
                        "descricao": f"Margem disponível: {fmt(row['margem'])} — Score {row.get('score',0)}%",
                        "entidade": "cliente",
                        "entidade_id": int(row["id"]),
                        "prioridade": "urgente"
                    })
            except: pass

    # Regra 3: Clientes com contratos quitando em 90 dias
    try:
        if sb:
            r_cts = sb.table("contratos").select("*, clientes(nome,id)").execute()
            for ct in (r_cts.data or []):
                try:
                    inicio = datetime.strptime(str(ct.get("data_inicio",""))[:10], "%Y-%m-%d")
                    total_meses = int(ct.get("parcelas_total", 0))
                    if total_meses > 0:
                        quitacao = inicio + timedelta(days=total_meses*30)
                        dias_quit = (quitacao - agora).days
                        nome_cli = ct.get("clientes",{}).get("nome","") if isinstance(ct.get("clientes"),dict) else ""
                        if 0 <= dias_quit <= 90 and nome_cli:
                            alertas.append({
                                "tipo": "contrato_quitando",
                                "titulo": f"Contrato quitando: {nome_cli.split()[0]}",
                                "descricao": f"Contrato {ct.get('banco','')} quita em {dias_quit} dias — Margem será liberada!",
                                "entidade": "contrato",
                                "entidade_id": int(ct.get("id",0)),
                                "prioridade": "alta" if dias_quit <= 30 else "media"
                            })
                except: pass
    except: pass

    # Regra 4: Reajuste INSS — alertas nos momentos certos
    # Dezembro: preparar lista de clientes para abordagem em janeiro
    if agora.month == 12 and agora.day >= 15:
        alertas.append({
            "tipo": "reajuste_inss",
            "titulo": "Reajuste INSS em janeiro — prepare sua lista",
            "descricao": "Em janeiro o INSS paga com novo valor reajustado. A margem aumenta imediatamente. Contate seus clientes ANTES da concorrência — prepare abordagem agora.",
            "entidade": "sistema",
            "entidade_id": 0,
            "prioridade": "urgente"
        })
    # Janeiro: margem já atualizada — janela de oportunidade aberta
    if agora.month == 1:
        alertas.append({
            "tipo": "reajuste_inss",
            "titulo": "🚀 Reajuste INSS ativo — margem aumentou agora",
            "descricao": "Todos os benefícios foram reajustados. A margem consignável aumentou. Contate TODOS os clientes ativos hoje — janela de oportunidade máxima antes da concorrência.",
            "entidade": "sistema",
            "entidade_id": 0,
            "prioridade": "urgente"
        })
    # Fevereiro: segunda onda — quem não converteu em janeiro
    if agora.month == 2:
        alertas.append({
            "tipo": "reajuste_inss",
            "titulo": "⏰ Segunda onda reajuste — clientes não contatados",
            "descricao": "Ainda há clientes com margem aumentada que não foram abordados. Filtre por Score alto e contate antes de março.",
            "entidade": "sistema",
            "entidade_id": 0,
            "prioridade": "alta"
        })

    # Inserir apenas alertas novos (evitar duplicatas verificando título)
    try:
        existentes = sb.table("alertas").select("titulo").eq("lido", False).execute()
        titulos_existentes = {r["titulo"] for r in (existentes.data or [])}
        novos = [a for a in alertas if a["titulo"] not in titulos_existentes]
        if novos:
            sb.table("alertas").insert(novos).execute()
    except: pass
def del_cli(id):
    for t in ["historico","followups","clientes"]:
        sb.table(t).delete().eq("cliente_id" if t != "clientes" else "id", id).execute()
def del_fu(id): sb.table("followups").delete().eq("id", id).execute()

# ── EMAIL ─────────────────────────────────────────────────────────────────────
def exportar_excel(df, nome_aba="Dados"):
    """Exporta DataFrame para Excel em memória — download direto"""
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=nome_aba)
    output.seek(0)
    return output.getvalue()

def exportar_clientes_excel(df):
    """Prepara relatório de clientes para Excel"""
    if df.empty: return None
    cols = {
        "nome": "Nome",
        "cpf_d": "CPF (mascarado)",
        "tel_d": "Telefone (mascarado)",
        "email": "Email",
        "canal": "Canal",
        "status": "Status",
        "interesse": "Interesse",
        "tipo_beneficio": "Tipo Benefício",
        "beneficio": "Benefício (R$)",
        "parcelas": "Parcelas (R$)",
        "margem": "Margem (R$)",
        "pct": "Comprometido (%)",
        "score": "Score (%)",
        "created_at": "Cadastrado em",
    }
    cols_disp = {k:v for k,v in cols.items() if k in df.columns}
    df_exp = df[list(cols_disp.keys())].rename(columns=cols_disp)
    return exportar_excel(df_exp, "Clientes")

def exportar_contratos_excel(dfc):
    """Prepara relatório de contratos para Excel"""
    if dfc.empty: return None
    cols = {
        "cliente_nome": "Cliente",
        "banco": "Banco",
        "valor": "Valor (R$)",
        "parcelas_total": "Total Parcelas",
        "parcelas_pagas": "Pagas",
        "taxa_juros": "Taxa (% a.m.)",
        "data_inicio": "Início",
        "comissao": "Comissão (R$)",
    }
    if "comissao" not in dfc.columns:
        dfc = dfc.copy()
        dfc["comissao"] = (dfc["valor"] * 0.03).round(2)
    cols_disp = {k:v for k,v in cols.items() if k in dfc.columns}
    df_exp = dfc[list(cols_disp.keys())].rename(columns=cols_disp)
    return exportar_excel(df_exp, "Contratos")

def send_email(to_email, to_name, subject, html):
    try:
        import sib_api_v3_sdk
        cfg = sib_api_v3_sdk.Configuration()
        cfg.api_key["api-key"] = BREVO_KEY
        api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(cfg))
        api.send_transac_email(sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email, "name": to_name}],
            sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
            subject=subject, html_content=html
        ))
        return True, None
    except Exception as e:
        return False, str(e)

def send_email_safe(to_email, to_name, subject, html):
    """Wrapper com debug visível"""
    if not BREVO_KEY or BREVO_KEY == "":
        return False, "BREVO_API_KEY não configurada nos Secrets"
    if not to_email:
        return False, "Email do destinatário vazio"
    ok, err = send_email(to_email, to_name, subject, html)
    return ok, err

# ── AUTH ──────────────────────────────────────────────────────────────────────
# ── SISTEMA DE USUÁRIOS ──────────────────────────────────────────────────────
def load_users():
    """Carrega usuários do Supabase. Admin fixo sempre presente."""
    users = {
        "eduardo": {
            "pwd": hashlib.sha256(b"nucleo2026").hexdigest(),
            "name": "Eduardo Lima de Sousa",
            "role": "admin"
        }
    }
    if sb:
        try:
            r = sb.table("usuarios").select("*").eq("ativo", True).execute()
            for u in (r.data or []):
                users[u["login"].lower()] = {
                    "pwd": u["senha_hash"],
                    "name": u["nome"],
                    "role": u["perfil"]
                }
        except: pass
    return users

def check_pwd(u, p):
    users = load_users()
    usr = users.get(u.lower())
    if not usr: return False
    return hmac.compare_digest(usr["pwd"], hashlib.sha256(p.encode()).hexdigest())

def get_role():
    return st.session_state.get("role", "operador")

def is_admin():
    return get_role() == "admin"

# ── HELPERS UI ────────────────────────────────────────────────────────────────
def fmt(v):
    """Formata valor monetário: 5230.0 → R$ 5.230,00"""
    try:
        return f"R$ {abs(float(v)):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except:
        return "R$ 0,00"

def buscar_cep(cep):
    """Busca endereço via API ViaCEP — gratuita, sem chave.
    Retorna dict com rua, bairro, cidade, uf ou None se inválido."""
    import requests
    cep_limpo = "".join(filter(str.isdigit, cep or ""))
    if len(cep_limpo) != 8:
        return None
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=4)
        d = r.json()
        if d.get("erro"):
            return None
        return {
            "rua": d.get("logradouro", ""),
            "bairro": d.get("bairro", ""),
            "cidade": d.get("localidade", ""),
            "uf": d.get("uf", ""),
        }
    except:
        return None

def parse_valor(s):
    """Converte entrada do usuário para float.
    Aceita: 2562 / 2562,00 / 2.562,00 / 2562.00
    Retorna float ou 0.0"""
    try:
        s = str(s).strip().replace("R$","").replace(" ","")
        # Remove pontos de milhar, troca vírgula decimal por ponto
        if "," in s and "." in s:
            # Ex: 2.562,00 → remover ponto, trocar vírgula
            s = s.replace(".","").replace(",",".")
        elif "," in s:
            # Ex: 2562,00 → trocar vírgula por ponto
            s = s.replace(",",".")
        return max(0.0, float(s))
    except:
        return 0.0

def input_valor(label, key, value=0.0, help_text=""):
    """Campo de valor monetário com formatação automática.
    O usuário digita: 2562 ou 2562,00 ou 2.562,00
    O sistema exibe: 2.562,00 embaixo em tempo real."""
    val_str = st.text_input(
        label,
        value=f"{value:,.2f}".replace(",","X").replace(".",",").replace("X",".") if value else "",
        placeholder="0,00",
        key=key,
        help=help_text or "Digite o valor. Ex: 2562,00 ou 2.562,00"
    )
    parsed = parse_valor(val_str)
    if val_str and parsed > 0:
        st.caption(f"✅ {fmt(parsed)}")
    elif val_str and val_str not in ["", "0,00", "0"]:
        st.caption("⚠️ Formato inválido")
    return parsed

def calc_comissao_projetada(margem, taxa_comissao=0.03, prazo_meses=48):
    """Estima comissão se o cliente fechar contrato com a margem disponível.
    taxa_comissao: % sobre o valor total do contrato (padrão 3%)"""
    if margem <= 0:
        return 0.0
    valor_contrato_estimado = margem * prazo_meses
    return round(valor_contrato_estimado * taxa_comissao, 2)

def validar_cpf(cpf):
    """Valida CPF e retorna True se válido"""
    d = "".join(filter(str.isdigit, cpf or ""))
    if len(d) != 11 or d == d[0]*11: return False
    for i in range(9,11):
        s = sum(int(d[j])*(i+1-j) for j in range(i))
        if int(d[i]) != (s*10%11)%10: return False
    return True

def mask_cpf_input(cpf):
    """Máscara de exibição: 523.1**.***-12 (oculta 6 dígitos do meio)"""
    d = "".join(filter(str.isdigit, cpf or ""))
    if len(d) == 11:
        return f"{d[0:3]}.***.{d[6:9]}-{d[9:11]}"
    return cpf

def mask_tel_input(tel):
    """Máscara de exibição: (86) *****-7312 (oculta 5 dígitos)"""
    d = "".join(filter(str.isdigit, tel or ""))
    if len(d) == 11:
        return f"({d[0:2]}) *****-{d[7:11]}"
    elif len(d) == 10:
        return f"({d[0:2]}) ****-{d[6:10]}"
    return tel

def kpi_html(label, value, sub="", color="green"):
    border = {"navy": "#1B3A6B", "red": "#C0392B", "yellow": "#E67E22"}.get(color, "#1A7A5E")
    sub_html = f'<span style="font-size:10px;color:#94A3B8">{sub}</span>' if sub else ""
    html = (
        f'<div style="border-radius:12px;padding:16px 12px 12px;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.08);border-top:3px solid {border};text-align:center;">'
        f'<div style="font-size:10px;color:#94A3B8;text-transform:uppercase;letter-spacing:.07em;font-weight:700;margin-bottom:5px">{label}</div>'
        f'<div style="font-size:22px;font-weight:800;color:#1B3A6B;line-height:1.1">{value}</div>'
        f'{sub_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def badge(text, color):
    cls = {"green":"b-green","yellow":"b-yellow","red":"b-red","blue":"b-blue","slate":"b-slate"}.get(color,"b-slate")
    return f'<span class="badge {cls}">{text}</span>'

def plotly_theme():
    return dict(
        plot_bgcolor="#0D1B35",
        paper_bgcolor="#0D1B35",
        margin=dict(l=0, r=10, t=8, b=0),
        font=dict(family="Inter, sans-serif", size=11, color="rgba(255,255,255,0.7)"),
        xaxis=dict(showgrid=False, showline=False, color="rgba(255,255,255,0.5)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", showline=False, color="rgba(255,255,255,0.5)"),
    )

def page_header(icon, title, subtitle):
    st.markdown(
        f'<div class="page-header"><div style="font-size:28px;line-height:1">{icon}</div>'
        f'<div><h2>{title}</h2><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True
    )

# ── LOGIN SCREEN ──────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""<style>
        [data-testid="stSidebar"]{display:none!important}
        [data-testid="collapsedControl"]{display:none!important}
        .stApp{background:#0A1628!important}
        [data-testid="stAppViewContainer"]>.main{background:#0A1628!important}
        [data-testid="stAppViewContainer"]>.main>.block-container{
            max-width:420px!important;padding:5rem 1rem 1rem!important;margin:0 auto!important}
        .stTextInput>div>div>input{
            background:rgba(255,255,255,0.1)!important;
            border:1px solid rgba(255,255,255,0.2)!important;
            color:white!important;border-radius:10px!important}
        .stTextInput>div>div>input::placeholder{color:rgba(255,255,255,0.45)!important}
        .stButton>button{
            background:#1A7A5E!important;border-radius:10px!important;
            font-weight:700!important;font-size:14px!important;padding:12px!important}
        .stButton>button:hover{background:#155f48!important}
    </style>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:32px">
        <svg width="60" height="60" viewBox="0 0 64 64" fill="none" style="margin-bottom:12px">
            <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="#1A7A5E" stroke-width="2" fill="none"/>
            <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="#1A7A5E" stroke-width="2" fill="none" transform="rotate(60 32 32)"/>
            <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="#1A7A5E" stroke-width="2" fill="none" transform="rotate(120 32 32)"/>
            <circle cx="32" cy="32" r="5.5" fill="#1A7A5E"/>
            <circle cx="32" cy="32" r="2.5" fill="white"/>
        </svg>
        <div style="font-size:28px;font-weight:800;color:white;letter-spacing:-0.5px">
            Núcleo <span style="color:#4ADE80">Crédito</span>
        </div>
        <div style="font-size:13px;color:rgba(255,255,255,0.5);font-style:italic;margin-top:6px">
            No centro da sua vida financeira.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Usuário", placeholder="seu usuário", label_visibility="collapsed")
        password = st.text_input("Senha", type="password", placeholder="••••••••", label_visibility="collapsed")
        submitted = st.form_submit_button("Entrar", use_container_width=True)

    st.markdown("<p style='text-align:center;font-size:10px;color:rgba(255,255,255,0.3);margin-top:12px'>🔒 Dados criptografados · LGPD Compliant</p>", unsafe_allow_html=True)

    if submitted:
        if check_pwd(username, password):
            users = load_users()
            st.session_state.logged_in = True
            st.session_state.username  = username
            st.session_state.uname     = users[username.lower()]["name"]
            st.session_state.role      = users[username.lower()]["role"]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# ── NAVEGAÇÃO ─────────────────────────────────────────────────────────────────
# Sidebar para desktop
with st.sidebar:
    st.markdown(f"""
    <div style="padding:24px 16px 20px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:8px">
        <div style="display:flex;align-items:center;gap:10px">
            <svg width="32" height="32" viewBox="0 0 64 64" fill="none">
                <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none"/>
                <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(60 32 32)"/>
                <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(120 32 32)"/>
                <circle cx="32" cy="32" r="5.5" fill="{GREEN}"/>
                <circle cx="32" cy="32" r="2.5" fill="white"/>
            </svg>
            <div>
                <div style="color:white;font-size:15px;font-weight:800">Núcleo Crédito</div>
                <div style="color:rgba(255,255,255,0.4);font-size:9px;font-style:italic">No centro da sua vida financeira.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Menu filtrado por perfil
    _role = st.session_state.get("role", "operador")
    if _role == "admin":
        _opcoes = [
            "📊  Dashboard",
            "👥  Clientes",
            "📋  Leads",
            "📄  Contratos",
            "🧮  Simulador",
            "🔔  Alertas",
            "📅  Agenda",
            "📧  Email Marketing",
            "🎯  Metas",
            "⚙️  Administração",
        ]
    else:
        _opcoes = [
            "👥  Clientes",
            "📋  Leads",
            "🧮  Simulador",
            "📅  Agenda",
        ]

    menu = st.radio(
        "Navegação",
        options=_opcoes,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

    # Rodapé com perfil + sair
    role_label = "Administrador" if st.session_state.get("role") == "admin" else "Operador"
    role_color = "#4ADE80" if st.session_state.get("role") == "admin" else "#60A5FA"
    inicial = st.session_state.uname[0].upper()

    col_perfil, col_sair = st.columns([3, 1])
    with col_perfil:
        st.markdown(f"""
        <div style="padding:10px 12px;border-top:1px solid rgba(255,255,255,0.08);
            display:flex;align-items:center;gap:10px">
            <div style="width:32px;height:32px;border-radius:50%;
                background:linear-gradient(135deg,#1A7A5E,#1B3A6B);
                display:flex;align-items:center;justify-content:center;
                font-size:13px;font-weight:800;color:white;flex-shrink:0">
                {inicial}
            </div>
            <div>
                <div style="color:white;font-size:12px;font-weight:700;line-height:1.2">
                    {st.session_state.uname.split()[0]}
                </div>
                <div style="font-size:9px;font-weight:700;color:{role_color};
                    text-transform:uppercase;letter-spacing:.06em">
                    {role_label}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_sair:
        st.markdown("<div style='padding-top:14px;border-top:1px solid rgba(255,255,255,0.08)'></div>",
                    unsafe_allow_html=True)
        if st.button("↪", key="logout", help="Sair do sistema"):
            st.session_state.logged_in = False
            st.rerun()


# ── PÁGINAS ───────────────────────────────────────────────────────────────────

# ── BRAND TOPBAR ──────────────────────────────────────────────────────────────
from datetime import timezone, timedelta
br_tz = timezone(timedelta(hours=-3))
today_str = datetime.now(br_tz).strftime('%d/%m/%Y')

st.markdown(f"""
<div class="brand-topbar">
    <div class="brand-topbar-left">
        <svg width="28" height="28" viewBox="0 0 64 64" fill="none">
            <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none"/>
            <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(60 32 32)"/>
            <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(120 32 32)"/>
            <circle cx="32" cy="32" r="5.5" fill="{GREEN}"/>
            <circle cx="32" cy="32" r="2.5" fill="white"/>
        </svg>
        <div>
            <div class="brand-topbar-title">Núcleo Crédito</div>
            <div class="brand-topbar-sub">No centro da sua vida financeira.</div>
        </div>
    </div>
    <div class="brand-topbar-right">{today_str} &nbsp;·&nbsp; {st.session_state.uname.split()[0]}</div>
</div>
""", unsafe_allow_html=True)

# ═══ DASHBOARD ═══
if "Dashboard" in menu:
    page_header("📊", "Dashboard de Performance", "Visão geral em tempo real")

    df  = load_clientes()
    dfl = load_leads()
    dfc = load_contratos()
    dfa = load_fu()

    tc  = len(df)
    at  = len(df[df["status"]=="Ativo"]) if not df.empty else 0
    mt  = df["margem"].clip(lower=0).sum() if not df.empty else 0
    op  = len(df[df["margem"]>300]) if not df.empty else 0
    tl  = len(dfl)
    cv  = len(dfl[dfl["status"]=="Convertido"]) if not dfl.empty else 0
    tx  = round(cv/tl*100, 1) if tl > 0 else 0
    car = dfc["valor"].sum() if not dfc.empty else 0
    fh  = 0
    if not dfa.empty:
        dfa["data_followup"] = pd.to_datetime(dfa["data_followup"]).dt.date
        fh = len(dfa[dfa["data_followup"] == date.today()])

    c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
    for col, (lbl, val, sub, cor) in zip(
        [c1,c2,c3,c4,c5,c6,c7,c8],
        [
            ("Clientes", tc, "", "navy"),
            ("Ativos", at, "", "green"),
            ("Margem Total", fmt(mt), "disponível", "green"),
            ("Oportunidades", op, ">R$ 300", "yellow"),
            ("Leads", tl, "", "navy"),
            ("Conversão", f"{tx}%", f"{cv} fechados", "green"),
            ("Carteira", fmt(car), "", "navy"),
            ("Agenda Hoje", fh, "follow-ups", "yellow" if fh > 0 else "navy"),
        ]
    ):
        with col:
            kpi_html(lbl, val, sub, cor)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-card"><div class="chart-title">🎯 Score de Propensão</div>', unsafe_allow_html=True)
            ds = df.sort_values("score", ascending=True)
            fig = go.Figure(go.Bar(
                x=ds["score"],
                y=ds["nome"].str.split().str[:2].str.join(" "),
                orientation="h",
                marker_color=[GREEN if s>=75 else YELLOW if s>=55 else NAVY for s in ds["score"]],
                marker_line_width=0,
                text=[f"{s}%" for s in ds["score"]],
                textposition="outside",
                textfont=dict(size=10)
            ))
            fig.update_layout(height=240, xaxis=dict(range=[0,115], **{k:v for k,v in plotly_theme()["xaxis"].items()}), **{k:v for k,v in plotly_theme().items() if k != "xaxis"})
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-card"><div class="chart-title">💰 Margem Disponível</div>', unsafe_allow_html=True)
            dm = df.sort_values("margem", ascending=True)
            fig2 = go.Figure(go.Bar(
                x=dm["margem"],
                y=dm["nome"].str.split().str[:2].str.join(" "),
                orientation="h",
                marker_color=[GREEN if m>300 else YELLOW if m>0 else RED for m in dm["margem"]],
                marker_line_width=0,
                text=[fmt(m) for m in dm["margem"]],
                textposition="outside",
                textfont=dict(size=10)
            ))
            fig2.add_vline(x=300, line_dash="dot", line_color=GREEN, line_width=1.5, annotation_text="R$300", annotation_font_size=9)
            fig2.update_layout(height=240, **plotly_theme())
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if not dfl.empty:
            col3, col4 = st.columns(2)
            with col3:
                st.markdown('<div class="chart-card"><div class="chart-title">📋 Leads por Canal</div>', unsafe_allow_html=True)
                cc = dfl["canal"].value_counts().reset_index()
                cc.columns = ["Canal", "Leads"]
                fig3 = px.bar(cc, x="Canal", y="Leads", color_discrete_sequence=[NAVY], text="Leads")
                fig3.update_traces(textposition="outside", marker_line_width=0)
                fig3.update_layout(height=220, **plotly_theme())
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col4:
                st.markdown('<div class="chart-card"><div class="chart-title">🔄 Status do Pipeline</div>', unsafe_allow_html=True)
                sc2 = dfl["status"].value_counts().reset_index()
                sc2.columns = ["Status", "Qtd"]
                fig4 = px.pie(sc2, values="Qtd", names="Status",
                    color_discrete_sequence=[GREEN, YELLOW, NAVY, RED], hole=0.55)
                fig4.update_traces(textinfo="percent+label", textfont_size=10)
                fig4.update_layout(height=220, showlegend=False, paper_bgcolor="white",
                    margin=dict(l=0,r=0,t=0,b=0), font=dict(family="Inter"))
                st.plotly_chart(fig4, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # Pagamentos próximos
        if not df.empty:
            dpg = df[df["dias"].notna()].copy()
            dpg["dias"] = dpg["dias"].astype(int)
            urg = dpg[dpg["dias"] <= 5].sort_values("dias")
            if len(urg) > 0:
                st.markdown('<div class="chart-card"><div class="chart-title">🗓 Pagamentos INSS — Próximos 5 dias</div>', unsafe_allow_html=True)
                for _, r in urg.iterrows():
                    cor = RED if r["dias"] <= 1 else YELLOW if r["dias"] <= 3 else GREEN
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:8px 0;border-bottom:1px solid #F1F5F9">
                        <div>
                            <span style="font-weight:600;color:{NAVY};font-size:13px">{r['nome'].split()[0]} {r['nome'].split()[1] if len(r['nome'].split())>1 else ''}</span>
                            <span style="font-size:11px;color:#94A3B8;margin-left:8px">{r['tel_d']}</span>
                        </div>
                        <div style="text-align:right">
                            <span style="font-weight:700;color:{cor};font-size:14px">{r['prox'].strftime('%d/%m') if r['prox'] else ''}</span>
                            <span style="font-size:10px;color:#94A3B8;margin-left:6px">em {r['dias']} dia(s)</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado. Vá para Clientes para começar.")

# ═══ CLIENTES ═══
elif "Clientes" in menu:
    page_header("👥", "Gestão de Clientes", "Base segura com dados criptografados — LGPD")

    # Botão de export no topo direito
    _df_exp = load_clientes()
    if not _df_exp.empty:
        _excel = exportar_clientes_excel(_df_exp)
        if _excel:
            st.download_button(
                label="📥 Exportar Clientes (.xlsx)",
                data=_excel,
                file_name=f"nucleo_credito_clientes_{date.today().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="exp_cli"
            )

    if st.button("＋ Cadastrar Novo Cliente", key="btn_new_cli"):
        st.session_state["show_form_cli"] = not st.session_state.get("show_form_cli", False)
    if st.session_state.get("show_form_cli", False):
        with st.form("form_cli", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("<div style='color:rgba(255,255,255,0.5);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px'>Identificação</div>", unsafe_allow_html=True)
                nome     = st.text_input("Nome Completo *")
                nome_soc = st.text_input("Nome Social", placeholder="Como prefere ser chamado/a")
                cpf_raw  = st.text_input("CPF *", placeholder="000.000.000-00",
                    help="Digite apenas os 11 números. Ex: 604.456.856-12")
                tel_raw  = st.text_input("Telefone *", placeholder="(00) 00000-0000",
                    help="Com DDD. Ex: (86) 99999-0001")
                email    = st.text_input("Email", placeholder="exemplo@email.com")
                dn       = st.date_input("Data de Nascimento", value=date(1960,1,1),
                                         min_value=date(1920,1,1), max_value=date(2005,1,1),
                                         format="DD/MM/YYYY")

                st.markdown("<div style='color:rgba(255,255,255,0.5);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin:8px 0 4px'>Endereço</div>", unsafe_allow_html=True)
                cep_input = st.text_input("CEP *", placeholder="00000-000", key="cep_cad",
                    help="Digite o CEP completo (8 números) e os campos abaixo preenchem automaticamente")
                _cep_digits = re.sub(r'\D','',cep_input or "")
                _end_auto = buscar_cep(cep_input) if len(_cep_digits)==8 else None
                if _end_auto:
                    st.success(f"✅ CEP {cep_input} localizado")
                elif len(_cep_digits)==8:
                    st.warning("CEP não encontrado na base — preencha o endereço manualmente abaixo")
                elif cep_input:
                    st.caption(f"Digite os 8 números do CEP ({len(_cep_digits)}/8)")

                ce1, ce2 = st.columns(2)
                with ce1:
                    end_rua = st.text_input("Rua/Logradouro",
                        value=_end_auto['rua'] if _end_auto else "", key="end_rua_cad")
                    end_bairro = st.text_input("Bairro",
                        value=_end_auto['bairro'] if _end_auto else "", key="end_bairro_cad")
                    end_cidade = st.text_input("Cidade",
                        value=_end_auto['cidade'] if _end_auto else "", key="end_cidade_cad")
                with ce2:
                    end_num = st.text_input("Número", placeholder="123", key="end_num_cad")
                    end_compl = st.text_input("Complemento", placeholder="Apto, casa (opcional)", key="end_compl_cad")
                    end_uf = st.text_input("UF",
                        value=_end_auto['uf'] if _end_auto else "", max_chars=2, key="end_uf_cad")
                end_cidade_uf = f"{end_cidade}/{end_uf}"

                st.markdown("<div style='color:rgba(255,255,255,0.5);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin:12px 0 4px'>Número do Benefício (NB)</div>", unsafe_allow_html=True)
                nb1, nb2 = st.columns(2)
                with nb1:
                    nb_principal = st.text_input("NB Principal *", placeholder="000.000.000-0",
                        help="Número do Benefício no INSS — identificador único")
            with c2:
                st.markdown("<div style='color:rgba(255,255,255,0.5);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px'>Benefício</div>", unsafe_allow_html=True)
                tipo_ben  = st.selectbox("Tipo de Benefício *", ['Aposentadoria por Idade (Urbana)', 'Aposentadoria por Idade da Pessoa com Deficiência', 'Aposentadoria por Idade Rural', 'Aposentadoria por Incapacidade Permanente (Urbana)', 'Aposentadoria por Incapacidade Permanente (Rural)', 'Aposentadoria por Incapacidade Permanente (Acidentária)', 'Aposentadoria por Tempo de Contribuição', 'Aposentadoria por Tempo de Contribuição da Pessoa com Deficiência', 'Aposentadoria por Tempo de Contribuição — Regra de Transição', 'Aposentadoria Especial', 'Aposentadoria Especial — Professor', 'Aposentadoria Especial — Aeronauta', 'Aposentadoria Rural — Segurado Especial', 'Aposentadoria Híbrida', 'Pensão por Morte (Urbana)', 'Pensão por Morte (Rural)', 'Pensão por Morte (Acidentária)', 'Pensão Especial — Síndrome da Talidomida', 'Pensão Especial — Síndrome Congênita do Zika Vírus', 'Auxílio por Incapacidade Temporária — Urbano (antigo Aux. Doença)', 'Auxílio por Incapacidade Temporária — Acidentário', 'Auxílio-Acidente (consignável)', 'Auxílio-Reclusão — Urbano (consignável)', 'Auxílio-Reclusão — Rural (consignável)', 'Auxílio-Inclusão', 'Salário-Maternidade — Urbano', 'Salário-Maternidade — Rural', 'Salário-Família', 'BPC/LOAS — Idoso (cartão consignado; empréstimo com restrições)', 'BPC/LOAS — Pessoa com Deficiência (cartão consignado; empréstimo com restrições)', 'Servidor Público Federal — RPPS', 'Servidor Público Estadual — RPPS', 'Servidor Público Municipal — RPPS', 'Militar das Forças Armadas', 'Policial Militar Estadual', 'Renda Mensal Vitalícia', 'Outro'])
                tem_2_ben = st.checkbox("Possui mais de um benefício? (ex: aposentado + pensionista)",
                    help="Cliente pode acumular benefícios, cada um com seu próprio NB")
                tipo_ben_2 = None
                if tem_2_ben:
                    _tipos_completos = ["Aposentadoria por Idade (Urbana)","Aposentadoria por Idade da Pessoa com Deficiência","Aposentadoria por Idade Rural","Aposentadoria por Incapacidade Permanente (Urbana)","Aposentadoria por Incapacidade Permanente (Rural)","Aposentadoria por Incapacidade Permanente (Acidentária)","Aposentadoria por Tempo de Contribuição","Aposentadoria por Tempo de Contribuição da Pessoa com Deficiência","Aposentadoria por Tempo de Contribuição — Regra de Transição","Aposentadoria Especial","Aposentadoria Especial — Professor","Aposentadoria Especial — Aeronauta","Aposentadoria Rural — Segurado Especial","Aposentadoria Híbrida","Pensão por Morte (Urbana)","Pensão por Morte (Rural)","Pensão por Morte (Acidentária)","Pensão Especial — Síndrome da Talidomida","Pensão Especial — Síndrome Congênita do Zika Vírus","Auxílio por Incapacidade Temporária — Urbano (antigo Aux. Doença)","Auxílio por Incapacidade Temporária — Acidentário","Auxílio-Acidente (consignável)","Auxílio-Reclusão — Urbano (consignável)","Auxílio-Reclusão — Rural (consignável)","Auxílio-Inclusão","Salário-Maternidade — Urbano","Salário-Maternidade — Rural","Salário-Família","BPC/LOAS — Idoso (cartão consignado; empréstimo com restrições)","BPC/LOAS — Pessoa com Deficiência (cartão consignado; empréstimo com restrições)","Servidor Público Federal — RPPS","Servidor Público Estadual — RPPS","Servidor Público Municipal — RPPS","Militar das Forças Armadas","Policial Militar Estadual","Renda Mensal Vitalícia","Outro"]
                    tipo_ben_2 = st.selectbox("Segundo Tipo de Benefício", _tipos_completos, key="tipo_ben_2_cad")
                    nb_secundario = st.text_input("NB do 2º Benefício", placeholder="000.000.000-0", key="nb2_cad")
                    ben2_valor = st.number_input("Valor do 2º Benefício (R$)", min_value=0.0, step=50.0, key="ben2_val_cad")
                    st.caption("💡 Cada benefício tem margem consignável calculada separadamente")
                else:
                    nb_secundario = ""
                    ben2_valor = 0.0

                _eh_bpc  = "BPC" in tipo_ben or "LOAS" in tipo_ben
                _eh_temp = any(x in tipo_ben for x in ["Temporária","Maternidade","Família","Inclusão"])
                if _eh_bpc:
                    st.warning("BPC/LOAS: cartão consignado OK. Empréstimo tradicional com restrições. Margem 35%.")
                elif _eh_temp:
                    st.info("Benefício temporário: consignado tradicional não recomendado.")
                else:
                    st.success("Benefício consignável — margem 40%.")
                ben = input_valor("Valor do Benefício (R$) *", key="cad_ben",
                    help_text="Ex: 2562,00 ou 2.562,00")
                par = input_valor("Parcelas Ativas (R$)", key="cad_par",
                    help_text="Ex: 320,50 — total de descontos já ativos")
                data_conc = st.date_input("Data de Concessão do Benefício",
                    value=date(2020,1,1), min_value=date(2000,1,1),
                    format="DD/MM/YYYY",
                    help="Importante: carência de 10 meses para consignado (PL 1037/2025)")
                bloq = st.checkbox("Benefício bloqueado para consignado?",
                    help="Após cada operação o INSS bloqueia — precisa desbloquear no Meu INSS")
                rep_legal = st.checkbox("Possui representante legal no INSS?",
                    help="Se SIM: não pode contratar consignado")
                if rep_legal:
                    st.error("Lead inelegível para consignado — possui representante legal.")
            with c3:
                st.markdown("<div style='color:rgba(255,255,255,0.5);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px'>Comercial</div>", unsafe_allow_html=True)
                canal  = st.selectbox("Canal de Entrada", ["Indicação","WhatsApp","Panfletagem","Rádio","Instagram","Google","Presencial","Outros"])
                int_   = st.selectbox("Produto de Interesse", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor","Desenrola Brasil","Empréstimo Pessoal"])
                status = st.selectbox("Status", ["Lead Quente","Em análise","Ativo"])
                obs    = st.text_area("Observações", height=120)

            # Validação CPF
            cpf_valido = validar_cpf(cpf_raw) if cpf_raw else True
            if cpf_raw and not cpf_valido:
                st.error("CPF inválido — verifique os dígitos verificadores.")

            if st.form_submit_button("✅ Cadastrar Cliente", use_container_width=True):
                if not nome or not ben:
                    st.error("Nome e Benefício são obrigatórios.")
                elif cpf_raw and not cpf_valido:
                    st.error("Corrija o CPF antes de salvar.")
                elif rep_legal:
                    st.error("Não é possível cadastrar: beneficiário com representante legal é inelegível.")
                else:
                    obs_final = obs
                    if bloq: obs_final = f"[BENEFÍCIO BLOQUEADO — desbloqueio no Meu INSS necessário] {obs}"
                    endereco_completo = f"{end_rua}, {end_num} {end_compl} - {end_bairro} - {end_cidade_uf} - CEP {cep_input}".strip()
                    obs_com_ben2 = obs_final
                    if tem_2_ben and tipo_ben_2:
                        obs_com_ben2 = f"[2º BENEFÍCIO: {tipo_ben_2} | NB: {nb_secundario} | Valor: {fmt(ben2_valor)}] {obs_final}"
                    ins_cli({"nome":nome,"nome_social":nome_soc,"cpf":cpf_raw,
                        "telefone":tel_raw,"email":email,"data_nasc":str(dn),
                        "beneficio":float(ben),"parcelas":float(par),"canal":canal,
                        "status":status,"interesse":int_,"tipo_beneficio":tipo_ben,
                        "data_concessao":str(data_conc),"representante_legal":rep_legal,
                        "endereco":endereco_completo,"numero_beneficio":nb_principal,
                        "observacoes":obs_com_ben2})
                    st.success(f"✅ {nome} cadastrado com sucesso!")
                    st.rerun()

    df = load_clientes()
    if not df.empty:
        cf1, cf2, cf3 = st.columns(3)
        _status_opts = sorted(df["status"].dropna().unique().tolist())
        _canal_opts  = sorted(df["canal"].dropna().unique().tolist())
        with cf1: fs = st.multiselect("Status", _status_opts, default=_status_opts)
        with cf2: fc = st.multiselect("Canal",  _canal_opts,  default=_canal_opts)
        with cf3: oo = st.checkbox("Apenas oportunidades (margem > R$ 300)")

        if not fs: fs = _status_opts
        if not fc: fc = _canal_opts

        dff = df[df["status"].isin(fs) & df["canal"].isin(fc)]
        if oo: dff = dff[dff["margem"] > 300]
        dff = dff.sort_values("score", ascending=False)

        st.markdown(f"<p style='color:#94A3B8;font-size:12px;margin:8px 0 12px'><b>{len(dff)}</b> cliente(s)</p>", unsafe_allow_html=True)

        for _, row in dff.iterrows():
            m = row["margem"]
            cc = "opp" if m > 300 else "danger" if m <= 0 else "warn"
            bm = badge("Oportunidade","green") if m > 300 else badge("Sem margem","red") if m <= 0 else badge("Margem baixa","yellow")
            bs = badge(row["status"], "blue")

            # Botão toggle para expandir cliente
            btn_key = f"show_cli_{row['id']}"
            col_btn, col_info = st.columns([3, 1])
            with col_btn:
                st.markdown(
                    f'<div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.08);'
                    f'border-radius:10px;padding:10px 16px;cursor:pointer;margin-bottom:6px">'
                    f'<span style="color:white;font-weight:600;font-size:13px">{row["nome"]}</span>'
                    f'<span style="color:rgba(255,255,255,0.4);font-size:11px;margin-left:12px">'
                    f'Score {row["score"]}%  ·  {fmt(m)}</span></div>',
                    unsafe_allow_html=True
                )
            with col_info:
                if st.button("Ver detalhes" if not st.session_state.get(btn_key) else "Fechar",
                             key=f"btn_{btn_key}"):
                    st.session_state[btn_key] = not st.session_state.get(btn_key, False)
                    st.rerun()

            if st.session_state.get(btn_key, False):
                # ── VISÃO 360° DO CLIENTE ──────────────────────────────────
                # Header do cliente
                m = row["margem"]
                pct_c = row["pct"]
                bar_c = "#4ADE80" if pct_c<60 else "#FBBF24" if pct_c<90 else "#EF4444"

                nome_exib = row.get('nome_social','') or row['nome']
                nome_comp = row['nome'] if row.get('nome_social') else ''
                pct_c = row['pct']
                bar_c = "#4ADE80" if pct_c<60 else "#FBBF24" if pct_c<90 else "#EF4444"
                borda = '#4ADE80' if m>300 else '#EF4444' if m<=0 else '#FBBF24'
                nome_soc_html = f"<div style='font-size:11px;color:rgba(255,255,255,0.3);margin-top:1px'>{nome_comp}</div>" if nome_comp else ""
                tipo_ben_html = f" · {row.get('tipo_beneficio','')}" if row.get('tipo_beneficio') else ""
                header_html = (
                    f'<div style="background:#0D1B35;border:1px solid rgba(74,222,128,0.2);border-radius:14px;padding:18px 20px;margin:8px 0;border-left:4px solid {borda}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px">'
                    f'<div>'
                    f'<div style="font-size:18px;font-weight:800;color:white">{nome_exib}</div>'
                    f'{nome_soc_html}'
                    f'<div style="font-size:12px;color:rgba(255,255,255,0.4);margin-top:3px">{row["tel_d"]} · {row.get("canal","")} · {row.get("interesse","")}{tipo_ben_html}</div>'
                    f'<div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">'
                    f'{badge(row["status"],"blue")}'
                    f'{badge(f'Score {row["score"]}%', "green" if row["score"]>=75 else "yellow" if row["score"]>=50 else "red")}'
                    f'{""+badge("Oportunidade","green") if m>300 else badge("Sem margem","red") if m<=0 else badge("Margem baixa","yellow")}'
                    f'</div></div>'
                    f'<div style="text-align:right">'
                    f'<div style="font-size:10px;color:rgba(255,255,255,0.3)">Margem disponível</div>'
                    f'<div style="font-size:26px;font-weight:800;color:{borda}">{fmt(m)}</div>'
                    f'<div style="font-size:10px;color:rgba(255,255,255,0.3)">Benefício: {fmt(row["beneficio"])}</div>'
                    f'<div style="font-size:10px;color:#4ADE80;margin-top:2px">💰 Comissão projetada: {fmt(calc_comissao_projetada(m))}</div>'
                    f'</div></div>'
                    f'<div style="margin-top:12px">'
                    f'<div style="display:flex;justify-content:space-between;font-size:10px;color:rgba(255,255,255,0.35);margin-bottom:4px"><span>Margem comprometida</span><span>{pct_c:.0f}%</span></div>'
                    f'<div style="background:rgba(255,255,255,0.07);border-radius:99px;height:6px;overflow:hidden">'
                    f'<div style="width:{pct_c}%;height:100%;background:{bar_c};border-radius:99px"></div>'
                    f'</div></div></div>'
                )
                st.markdown(header_html, unsafe_allow_html=True)

                # 4 abas da visão 360°
                t360_dados, t360_hist, t360_acao, t360_contrato = st.tabs([
                    "📋 Dados & KPIs", "📜 Histórico", "✏️ Ações", "📄 Contratos"
                ])

                with t360_dados:
                    # Grid de KPIs do cliente
                    g1,g2,g3,g4 = st.columns(4)
                    with g1: kpi_html("Benefício", fmt(row['beneficio']), "", "navy")
                    with g2: kpi_html("Margem disp.", fmt(m), "", "green" if m>300 else "red" if m<=0 else "yellow")
                    _dias_val = row.get('dias')
                    _dias_str = f"em {int(float(_dias_val))} dia(s)" if _dias_val is not None and str(_dias_val) not in ['nan','None',''] else ""
                    _prox_str = row['prox'].strftime('%d/%m/%Y') if row.get('prox') and str(row['prox']) not in ['NaT','None',''] else "—"
                    with g3: kpi_html("Próx. INSS", _prox_str, _dias_str, "navy")
                    with g4: kpi_html("Score", f"{row['score']}%", "propensão", "green" if row['score']>=75 else "yellow")

                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                    c_info1, c_info2 = st.columns(2)
                    with c_info1:
                        st.markdown(f"""
                        <div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.06);border-radius:11px;padding:14px 16px">
                            <div style="color:rgba(255,255,255,0.4);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px">Dados Pessoais</div>
                            <table style="width:100%;font-size:12px">
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">CPF</td><td style="color:white;text-align:right">{row['cpf_d']}</td></tr>
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Telefone</td><td style="color:white;text-align:right">{row['tel_d']}</td></tr>
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Canal</td><td style="color:white;text-align:right">{row.get('canal','—')}</td></tr>
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Interesse</td><td style="color:white;text-align:right">{row.get('interesse','—')}</td></tr>
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Status</td><td style="color:white;text-align:right">{row.get('status','—')}</td></tr>
                            </table>
                        </div>""", unsafe_allow_html=True)
                    with c_info2:
                        st.markdown(f"""
                        <div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.06);border-radius:11px;padding:14px 16px">
                            <div style="color:rgba(255,255,255,0.4);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px">Análise Financeira</div>
                            <table style="width:100%;font-size:12px">
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Margem total (40%)</td><td style="color:white;text-align:right">{fmt(row['beneficio']*0.4)}</td></tr>
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Parcelas ativas</td><td style="color:#EF4444;text-align:right">{fmt(row['parcelas'])}</td></tr>
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Margem livre</td><td style="color:{'#4ADE80' if m>0 else '#EF4444'};text-align:right;font-weight:700">{fmt(m)}</td></tr>
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Comprometido</td><td style="color:white;text-align:right">{pct_c:.0f}%</td></tr>
                                <tr><td style="color:rgba(255,255,255,0.4);padding:4px 0">Score propensão</td><td style="color:{'#4ADE80' if row['score']>=75 else '#FBBF24'};text-align:right;font-weight:700">{row['score']}%</td></tr>
                            </table>
                        </div>""", unsafe_allow_html=True)

                    if row.get('observacoes'):
                        st.markdown(f"""
                        <div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px 14px;margin-top:10px">
                            <div style="color:rgba(255,255,255,0.35);font-size:10px;font-weight:600;text-transform:uppercase;margin-bottom:5px">Observações</div>
                            <div style="color:rgba(255,255,255,0.7);font-size:12px">{row['observacoes']}</div>
                        </div>""", unsafe_allow_html=True)

                with t360_hist:
                    hist = load_hist(row["id"])
                    if not hist.empty:
                        for _, h in hist.iterrows():
                            tp_cor = {"Ligação":"#60A5FA","WhatsApp":"#4ADE80","Visita":"#C084FC","Email":"#FB923C"}.get(h.get('tipo',''),"#94A3B8")
                            st.markdown(f"""
                            <div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.06);border-radius:9px;
                                padding:10px 14px;margin-bottom:6px;border-left:3px solid {tp_cor}">
                                <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                                    <span style="color:{tp_cor};font-size:11px;font-weight:700">{h.get('tipo','')}</span>
                                    <span style="color:rgba(255,255,255,0.3);font-size:10px">{h.get('data','')}</span>
                                </div>
                                <div style="color:rgba(255,255,255,0.7);font-size:12px">{h.get('nota','')}</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:rgba(255,255,255,0.3);font-size:12px;padding:16px 0">Nenhum histórico registrado.</div>', unsafe_allow_html=True)

                with t360_acao:
                    ca_acao, cb_acao = st.columns(2)
                    with ca_acao:
                        st.markdown('<div style="color:rgba(255,255,255,0.6);font-size:12px;font-weight:600;margin-bottom:8px">Registrar Contato</div>', unsafe_allow_html=True)
                        with st.form(f"hist_{row['id']}"):
                            tp  = st.selectbox("Tipo", ["Ligação","WhatsApp","Visita","Email","Outro"], key=f"tp_{row['id']}")
                            nt  = st.text_area("Anotação", height=70, key=f"nt_{row['id']}")
                            if st.form_submit_button("📝 Salvar", use_container_width=True):
                                ins_hist({"cliente_id":row["id"],"tipo":tp,"nota":nt,"data":str(date.today())})
                                st.success("✅ Registrado!")
                                st.rerun()

                    with cb_acao:
                        st.markdown('<div style="color:rgba(255,255,255,0.6);font-size:12px;font-weight:600;margin-bottom:8px">Agendar Follow-up</div>', unsafe_allow_html=True)
                        with st.form(f"fu_{row['id']}"):
                            dfu = st.date_input("Data", value=date.today()+timedelta(days=1), key=f"dfu_{row['id']}")
                            mfu = st.text_input("Motivo", key=f"mfu_{row['id']}")
                            if st.form_submit_button("📅 Agendar", use_container_width=True):
                                ins_fu({"cliente_id":row["id"],"data_followup":str(dfu),"motivo":mfu})
                                st.success("✅ Agendado!")

                    if row.get("email"):
                        if st.button(f"📧 Enviar calendário INSS", key=f"em_{row['id']}"):
                            pg_d, dias_d = prox_pg(row["cpf_raw"])
                            html_email = (f'<div style="font-family:Inter,sans-serif;max-width:500px;margin:0 auto">'
                                f'<div style="background:#1B3A6B;padding:24px;border-radius:12px 12px 0 0">'
                                f'<h2 style="color:white;margin:0;font-size:18px">⚛ Núcleo Crédito</h2></div>'
                                f'<div style="background:white;padding:24px;border-radius:0 0 12px 12px">'
                                f'<p style="font-size:15px">Olá, <b>{row["nome"].split()[0]}</b>!</p>'
                                f'<p>Próximo INSS: <b style="color:#1A7A5E;font-size:18px">'
                                f'{pg_d.strftime("%d/%m/%Y") if pg_d else "Em breve"}</b></p>'
                                f'<a href="https://wa.me/5511952723015" style="background:#1A7A5E;color:white;'
                                f'padding:10px 24px;border-radius:99px;text-decoration:none;font-weight:600">'
                                f'💬 Falar no WhatsApp</a></div></div>')
                            ok_e, err_e = send_email_safe(row["email"], row["nome"], "Seu INSS — Núcleo Crédito", html_email)
                            if ok_e: st.success("✅ Enviado!")
                            else: st.error(f"Erro: {err_e}")

                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                    if st.button(f"✏️ Editar dados", key=f"edit_btn_{row['id']}"):
                        st.session_state[f"edit_cli_{row['id']}"] = not st.session_state.get(f"edit_cli_{row['id']}", False)

                    if st.session_state.get(f"edit_cli_{row['id']}", False):
                        st.markdown("""
                        <div style="background:#0D1B35;border:1px solid rgba(74,222,128,0.2);
                            border-radius:12px;padding:16px;margin-top:8px">
                            <div style="color:#4ADE80;font-size:12px;font-weight:700;margin-bottom:12px">
                                ✏️ Editar Dados do Cliente
                            </div>""", unsafe_allow_html=True)

                        with st.form(f"edit_cli_{row['id']}_form"):
                            ec1, ec2, ec3 = st.columns(3)
                            with ec1:
                                e_nome   = st.text_input("Nome completo", value=row["nome"])
                                e_social = st.text_input("Nome social", value=row.get("nome_social","") or "", help="Como prefere ser chamado/a")
                                e_cpf    = st.text_input("CPF", value=row["cpf_raw"] or "", placeholder="000.000.000-00")
                                e_tel    = st.text_input("Telefone", value=row["tel_raw"] or "", placeholder="(00) 00000-0000")
                                e_email  = st.text_input("Email", value=row.get("email","") or "")
                            with ec2:
                                _tipos = ['Aposentadoria por Idade (Urbana)', 'Aposentadoria por Idade da Pessoa com Deficiência', 'Aposentadoria por Idade Rural', 'Aposentadoria por Incapacidade Permanente (Urbana)', 'Aposentadoria por Incapacidade Permanente (Rural)', 'Aposentadoria por Incapacidade Permanente (Acidentária)', 'Aposentadoria por Tempo de Contribuição', 'Aposentadoria por Tempo de Contribuição da Pessoa com Deficiência', 'Aposentadoria por Tempo de Contribuição — Regra de Transição', 'Aposentadoria Especial', 'Aposentadoria Especial — Professor', 'Aposentadoria Especial — Aeronauta', 'Aposentadoria Rural — Segurado Especial', 'Aposentadoria Híbrida', 'Pensão por Morte (Urbana)', 'Pensão por Morte (Rural)', 'Pensão por Morte (Acidentária)', 'Pensão Especial — Síndrome da Talidomida', 'Pensão Especial — Síndrome Congênita do Zika Vírus', 'Auxílio por Incapacidade Temporária — Urbano (antigo Aux. Doença)', 'Auxílio por Incapacidade Temporária — Acidentário', 'Auxílio-Acidente (consignável)', 'Auxílio-Reclusão — Urbano (consignável)', 'Auxílio-Reclusão — Rural (consignável)', 'Auxílio-Inclusão', 'Salário-Maternidade — Urbano', 'Salário-Maternidade — Rural', 'Salário-Família', 'BPC/LOAS — Idoso (cartão consignado; empréstimo com restrições)', 'BPC/LOAS — Pessoa com Deficiência (cartão consignado; empréstimo com restrições)', 'Servidor Público Federal — RPPS', 'Servidor Público Estadual — RPPS', 'Servidor Público Municipal — RPPS', 'Militar das Forças Armadas', 'Policial Militar Estadual', 'Renda Mensal Vitalícia', 'Outro']
                                _tipo_atual = row.get("tipo_beneficio","Aposentadoria por Idade")
                                e_tipo   = st.selectbox("Tipo de Benefício", _tipos,
                                    index=_tipos.index(_tipo_atual) if _tipo_atual in _tipos else 0)
                                e_ben    = st.number_input("Benefício (R$)", value=float(row["beneficio"]), min_value=0.0, step=50.0)
                                e_par    = st.number_input("Parcelas ativas (R$)", value=float(row["parcelas"]), min_value=0.0, step=50.0)
                                e_status = st.selectbox("Status", ["Lead Quente","Em análise","Ativo","Inativo"],
                                    index=["Lead Quente","Em análise","Ativo","Inativo"].index(row["status"]) if row["status"] in ["Lead Quente","Em análise","Ativo","Inativo"] else 0)
                            with ec3:
                                e_canal  = st.selectbox("Canal", ["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"],
                                    index=["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"].index(row["canal"]) if row["canal"] in ["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"] else 0)
                                e_int    = st.selectbox("Interesse", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor","Empréstimo Pessoal"],
                                    index=["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor","Empréstimo Pessoal"].index(row["interesse"]) if row.get("interesse") in ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor","Empréstimo Pessoal"] else 0)
                                e_obs    = st.text_area("Observações", value=row.get("observacoes","") or "", height=100)

                            # Validação CPF na edição
                            e_cpf_ok = validar_cpf(e_cpf) if e_cpf else True
                            if e_cpf and not e_cpf_ok:
                                st.warning("CPF parece inválido — verifique antes de salvar")

                            if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                                upd_cli(row["id"], {
                                    "nome": e_nome, "nome_social": e_social,
                                    "email": e_email, "cpf": e_cpf, "telefone": e_tel,
                                    "beneficio": float(e_ben), "parcelas": float(e_par),
                                    "canal": e_canal, "status": e_status,
                                    "interesse": e_int, "tipo_beneficio": e_tipo,
                                    "observacoes": e_obs
                                })
                                st.success("✅ Dados atualizados!")
                                st.session_state[f"edit_cli_{row['id']}"] = False
                                st.rerun()

                        st.markdown('</div>', unsafe_allow_html=True)

                    # ── Upload de documentos direto na tela de Clientes ──────────
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    if st.button("📎 Documentos do cliente", key=f"doc_btn_{row['id']}"):
                        st.session_state[f"show_docs_{row['id']}"] = not st.session_state.get(f"show_docs_{row['id']}", False)

                    if st.session_state.get(f"show_docs_{row['id']}", False):
                        st.markdown('<div style="background:#0D1B35;border:1px solid rgba(96,165,250,0.2);border-radius:12px;padding:14px 16px;margin-top:6px">', unsafe_allow_html=True)
                        doc_tipos_cli = ["RG / CNH", "CPF", "Comprovante de Residência", "Extrato INSS / Carta de Concessão", "Contracheque / Holerite", "Proposta Assinada", "Contrato", "Outros"]
                        dc1, dc2 = st.columns([1,2])
                        with dc1:
                            doc_tipo_cli = st.selectbox("Tipo", doc_tipos_cli, key=f"dtype_cli_{row['id']}")
                        with dc2:
                            arquivo_cli = st.file_uploader("Arquivo", type=["pdf","jpg","jpeg","png"],
                                key=f"upload_cli_{row['id']}", label_visibility="visible")

                        if arquivo_cli and sb:
                            if st.button("Salvar documento", key=f"savdoc_cli_{row['id']}", use_container_width=True):
                                try:
                                    nome_arq_cli = f"clientes/{row['id']}/{doc_tipo_cli.replace(' ','_').replace('/','_')}_{arquivo_cli.name}"
                                    sb.storage.from_("documentos").upload(
                                        path=nome_arq_cli, file=arquivo_cli.getvalue(),
                                        file_options={"content-type": arquivo_cli.type, "upsert": "true"}
                                    )
                                    st.success(f"✅ {doc_tipo_cli} salvo!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")

                        if sb:
                            try:
                                pasta_cli = f"clientes/{row['id']}"
                                docs_cli = sb.storage.from_("documentos").list(pasta_cli)
                                if docs_cli:
                                    for doc_c in docs_cli:
                                        nome_doc_c = doc_c.get('name','')
                                        if not nome_doc_c: continue
                                        caminho_c = f"{pasta_cli}/{nome_doc_c}"
                                        url_c = sb.storage.from_("documentos").get_public_url(caminho_c)
                                        st.markdown(f'<a href="{url_c}" target="_blank" style="display:block;color:#60A5FA;font-size:12px;padding:6px 0;text-decoration:none">📄 {nome_doc_c}</a>', unsafe_allow_html=True)
                                else:
                                    st.caption("Nenhum documento enviado ainda.")
                            except:
                                st.caption("Bucket de documentos não configurado.")
                        st.markdown('</div>', unsafe_allow_html=True)

                    if st.button(f"🗑 Remover cliente", key=f"del_{row['id']}"):
                        del_cli(row["id"])
                        st.rerun()

                with t360_contrato:
                    # Upload de documentos
                    st.markdown('<div style="color:rgba(255,255,255,0.5);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px">Documentos do Cliente</div>', unsafe_allow_html=True)

                    doc_tipos = ["RG / CNH", "CPF", "Comprovante de Residência", "Extrato INSS / Carta de Concessão", "Contracheque / Holerite", "Proposta Assinada", "Contrato", "Outros"]

                    col_up1, col_up2, col_up3 = st.columns([3,1,2])
                    with col_up1:
                        doc_tipo = st.selectbox("Tipo de documento", doc_tipos,
                            key=f"dtype_{row['id']}")
                    with col_up2:
                        arquivo = st.file_uploader(
                            "x", type=["pdf","jpg","jpeg","png"],
                            key=f"upload_{row['id']}",
                            label_visibility="hidden"
                        )
                    with col_up3:
                        st.markdown('<div style="padding-top:28px;font-size:11px;color:rgba(255,255,255,0.3)">← clique para anexar</div>', unsafe_allow_html=True)

                    if arquivo and sb:
                        if st.button("📎 Salvar documento", key=f"savdoc_{row['id']}", use_container_width=True):
                            try:
                                nome_arq = f"clientes/{row['id']}/{doc_tipo.replace(' ','_').replace('/','_')}_{arquivo.name}"
                                sb.storage.from_("documentos").upload(
                                    path=nome_arq,
                                    file=arquivo.getvalue(),
                                    file_options={"content-type": arquivo.type, "upsert": "true"}
                                )
                                st.success(f"✅ {doc_tipo} salvo com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar: {e}")

                    # Listar documentos existentes
                    if sb:
                        try:
                            pasta = f"clientes/{row['id']}"
                            docs = sb.storage.from_("documentos").list(pasta)
                            if docs:
                                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                                for doc in docs:
                                    nome_doc = doc.get('name','')
                                    if not nome_doc: continue
                                    caminho = f"{pasta}/{nome_doc}"
                                    url = sb.storage.from_("documentos").get_public_url(caminho)
                                    tipo_label = nome_doc.split('_')[0].replace('_',' ') if '_' in nome_doc else nome_doc
                                    d1, d2 = st.columns([4,1])
                                    with d1:
                                        st.markdown(f"""
                                        <div style="background:rgba(255,255,255,0.04);border-radius:9px;padding:8px 12px;
                                            margin-bottom:5px;border-left:3px solid #60A5FA;display:flex;align-items:center;gap:8px">
                                            <span style="font-size:16px">📄</span>
                                            <div>
                                                <div style="color:white;font-size:12px;font-weight:600">{tipo_label}</div>
                                                <div style="color:rgba(255,255,255,0.35);font-size:10px">{nome_doc}</div>
                                            </div>
                                        </div>""", unsafe_allow_html=True)
                                    with d2:
                                        st.markdown(f"<a href='{url}' target='_blank' style='display:block;text-align:center;padding:8px;background:rgba(96,165,250,0.15);border-radius:8px;color:#60A5FA;font-size:11px;text-decoration:none;margin-top:2px'>Ver</a>", unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="color:rgba(255,255,255,0.3);font-size:12px;padding:12px 0">Nenhum documento enviado ainda.</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown('<div style="color:rgba(255,255,255,0.3);font-size:12px;padding:8px 0">Configure o bucket "documentos" no Supabase Storage para habilitar uploads.</div>', unsafe_allow_html=True)

                    st.markdown('<hr style="border-color:rgba(255,255,255,0.08);margin:14px 0">', unsafe_allow_html=True)
                    st.markdown('<div style="color:rgba(255,255,255,0.5);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px">Contratos do Cliente</div>', unsafe_allow_html=True)

                    # Contratos do cliente
                    try:
                        r_ct = sb.table("contratos").select("*").eq("cliente_id", row["id"]).execute() if sb else None
                        cts  = pd.DataFrame(r_ct.data) if r_ct and r_ct.data else pd.DataFrame()
                    except: cts = pd.DataFrame()

                    if not cts.empty:
                        total_ct = cts["valor"].sum()
                        st.markdown(f"""
                        <div style="display:flex;gap:10px;margin-bottom:12px">
                            <div style="background:#0D1B35;border:1px solid rgba(74,222,128,0.2);border-radius:10px;padding:10px 14px;flex:1;text-align:center">
                                <div style="color:rgba(255,255,255,0.35);font-size:10px">Contratos</div>
                                <div style="color:white;font-size:20px;font-weight:800">{len(cts)}</div>
                            </div>
                            <div style="background:#0D1B35;border:1px solid rgba(74,222,128,0.2);border-radius:10px;padding:10px 14px;flex:1;text-align:center">
                                <div style="color:rgba(255,255,255,0.35);font-size:10px">Total</div>
                                <div style="color:#4ADE80;font-size:20px;font-weight:800">{fmt(total_ct)}</div>
                            </div>
                            <div style="background:#0D1B35;border:1px solid rgba(74,222,128,0.2);border-radius:10px;padding:10px 14px;flex:1;text-align:center">
                                <div style="color:rgba(255,255,255,0.35);font-size:10px">Comissão est.</div>
                                <div style="color:#4ADE80;font-size:20px;font-weight:800">{fmt(total_ct*0.03)}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                        for _, ct in cts.iterrows():
                            st.markdown(f"""
                            <div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px 14px;margin-bottom:6px">
                                <div style="display:flex;justify-content:space-between">
                                    <span style="color:white;font-weight:600;font-size:13px">{ct.get('banco','—')}</span>
                                    <span style="color:#4ADE80;font-weight:700">{fmt(ct.get('valor',0))}</span>
                                </div>
                                <div style="color:rgba(255,255,255,0.35);font-size:11px;margin-top:3px">
                                    {ct.get('parcelas_total',0)}x · {ct.get('taxa_juros',0)}% a.m. · Início: {ct.get('data_inicio','—')}
                                </div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:rgba(255,255,255,0.3);font-size:12px;padding:16px 0">Nenhum contrato registrado para este cliente. Use a aba Contratos para registrar.</div>', unsafe_allow_html=True)


    else:
        st.info("Nenhum cliente cadastrado ainda.")

# ═══ LEADS ═══


elif "Contratos" in menu:
    page_header("📄", "Contratos", "Carteira ativa e controle de comissões")

    df_cli = load_clientes()
    dfc    = load_contratos()

    if not dfc.empty:
        tv = dfc["valor"].sum()
        c1, c2, c3 = st.columns(3)
        with c1: kpi_html("Carteira Total",     fmt(tv),           "",        "navy")
        with c2: kpi_html("Comissão Estimada",  fmt(tv*0.03),      "3%",      "green")
        with c3: kpi_html("Contratos Ativos",   len(dfc),          "",        "green")
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button("＋ Novo Contrato", key="btn_new_ct"):
        st.session_state["show_form_ct"] = not st.session_state.get("show_form_ct", False)
    if st.session_state.get("show_form_ct", False):
        if df_cli.empty:
            st.warning("Cadastre um cliente primeiro.")
        else:
            with st.form("form_ct", clear_on_submit=True):
                cm  = {r["nome"]: r["id"] for _, r in df_cli.iterrows()}
                c1, c2 = st.columns(2)
                with c1:
                    cs  = st.selectbox("Cliente", list(cm.keys()))
                    bco = st.selectbox("Banco / Instituição", ['001 - Banco do Brasil', '033 - Santander', '104 - Caixa Econômica Federal', '237 - Bradesco', '341 - Itaú Unibanco', '318 - Banco BMG', '074 - Banco Safra', '623 - Banco PAN', '389 - Banco Mercantil do Brasil', '707 - Banco Daycoval', '422 - Banco Safra S.A.', '394 - Banco Bradesco Financiamentos', '743 - Banco Semear', '290 - Parana Banco', '746 - Banco Modal', '047 - Banco Banese', '756 - Bancoob / Sicoob', '748 - Sicredi', '041 - Banrisul', '004 - Banco do Nordeste (BNB)', '021 - Banestes', '037 - Banco do Estado do Pará (Banpará)', '070 - BRB - Banco de Brasília', '085 - Cecred / Ailos', '136 - Unicred', '197 - Stone', '208 - BTG Pactual', '212 - Banco Original', '260 - Nu Pagamentos (Nubank)', '336 - Banco C6', '380 - PicPay', '403 - Cora', '604 - Banco Industrial do Brasil', '633 - Banco Rendimento', '643 - Banco Pine', '652 - Itaú Unibanco Holding', '655 - Votorantim (BV Financeira)', '077 - Banco Inter', '735 - Banco Neon', '739 - BCO Cetelem', '741 - Ribeirão Preto (BRSP)', '745 - Citibank', '329 - QI Tech', '531 - Banco Creditcorp', '274 - Money Plus', '082 - Banco Topázio', '097 - CreditSys', '121 - Banco Agibank', '190 - Servicoop', '461 - Asaas', '509 - Celcoin', '637 - Banco Sofisa', '654 - Banco A.J.Renner', '000 - Outro banco / Instituição'],
                        help="Digite para pesquisar pelo nome ou código")
                    val = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
                with c2:
                    pt  = st.number_input("Parcelas", min_value=1, max_value=108, value=36, step=1)
                    tx2 = st.number_input("Taxa (% a.m.)", min_value=0.5, max_value=5.0, value=1.8, step=0.1)
                    di  = st.date_input("Data Início")
                if st.form_submit_button("✅ Registrar", use_container_width=True):
                    ins_ct({"cliente_id":cm[cs],"banco":bco,"valor":float(val),"parcelas_total":int(pt),"taxa_juros":float(tx2),"data_inicio":str(di)})
                    st.success("Contrato registrado!")
                    st.rerun()

    if not dfc.empty:
        dfc["parcela"] = dfc.apply(lambda r: round(
            r["valor"]*(r["taxa_juros"]/100*(1+r["taxa_juros"]/100)**r["parcelas_total"])/
            ((1+r["taxa_juros"]/100)**r["parcelas_total"]-1), 2
        ) if r["parcelas_total"]>0 else 0, axis=1)
        dfc["comissao"] = (dfc["valor"]*0.03).round(2)

        st.markdown('<div class="chart-card"><div class="chart-title">📋 Carteira de Contratos</div>', unsafe_allow_html=True)
        # Header da tabela
        st.markdown("""
        <div style="display:grid;grid-template-columns:2fr 1.5fr 1fr 1fr 1fr 1fr 1fr;
            gap:8px;padding:8px 12px;background:rgba(255,255,255,0.04);
            border-radius:8px;margin-bottom:4px">
            <span style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:700;text-transform:uppercase">Cliente</span>
            <span style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:700;text-transform:uppercase">Banco</span>
            <span style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:700;text-transform:uppercase">Valor</span>
            <span style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:700;text-transform:uppercase">Parcelas</span>
            <span style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:700;text-transform:uppercase">Parcela/mês</span>
            <span style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:700;text-transform:uppercase">Comissão</span>
            <span style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:700;text-transform:uppercase">Início</span>
        </div>""", unsafe_allow_html=True)
        for _, r in dfc.iterrows():
            st.markdown(
                f'<div style="display:grid;grid-template-columns:2fr 1.5fr 1fr 1fr 1fr 1fr 1fr;'
                f'gap:8px;padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.05);'
                f'align-items:center">'
                f'<span style="font-size:12px;color:white;font-weight:600">{r.get("cliente_nome","")}</span>'
                f'<span style="font-size:12px;color:rgba(255,255,255,0.7)">{r.get("banco","")}</span>'
                f'<span style="font-size:12px;color:#4ADE80;font-weight:700">{fmt(r.get("valor",0))}</span>'
                f'<span style="font-size:12px;color:rgba(255,255,255,0.6)">{int(r.get("parcelas_total",0))}x</span>'
                f'<span style="font-size:12px;color:rgba(255,255,255,0.6)">{fmt(r.get("parcela",0))}</span>'
                f'<span style="font-size:12px;color:#4ADE80">{fmt(r.get("comissao",0))}</span>'
                f'<span style="font-size:11px;color:rgba(255,255,255,0.4)">{str(r.get("data_inicio",""))[:10]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Export contratos
        _excel_ct = exportar_contratos_excel(dfc)
        if _excel_ct:
            st.download_button(
                label="📥 Exportar Carteira (.xlsx)",
                data=_excel_ct,
                file_name=f"nucleo_credito_contratos_{date.today().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="exp_ct"
            )

# ═══ SIMULADOR ═══



elif "Simulador" in menu:
    page_header("🧮", "Simulador de Crédito", "Calcule margem, simule propostas e compare portabilidade")

    st.markdown("""<div style="background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.25);border-radius:11px;padding:12px 16px;margin-bottom:16px"><div style="color:#60A5FA;font-size:12px;font-weight:700;margin-bottom:6px">📋 Normas vigentes — MP 1.355 / Maio 2026</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px;color:rgba(255,255,255,0.6)"><div>✅ <b style="color:rgba(255,255,255,0.85)">Margem:</b> 40% do benefício</div><div>✅ <b style="color:rgba(255,255,255,0.85)">Prazo máximo:</b> 108 meses</div><div>✅ <b style="color:rgba(255,255,255,0.85)">Carência:</b> até 90 dias</div><div>✅ <b style="color:rgba(255,255,255,0.85)">Cartão consignado:</b> até 5% separado</div><div>⚠️ <b style="color:#FBBF24">Proibido:</b> fechamento por WhatsApp/telefone</div><div>⚠️ <b style="color:#FBBF24">Exige:</b> biometria facial no Meu INSS</div></div></div>""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["💳 Simulação de Crédito", "🔄 Calculadora de Portabilidade"])

    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown("#### Dados do Cliente")
            ben2 = st.number_input("Benefício (R$)", min_value=0.0, value=1412.0, step=50.0)
            pa2  = st.number_input("Parcelas Ativas (R$)", min_value=0.0, value=0.0, step=50.0)
            eh_bpc_sim = "BPC" in st.session_state.get("sim_tipo_ben","") or "LOAS" in st.session_state.get("sim_tipo_ben","")
            pct_sim = 0.35 if eh_bpc_sim else 0.40
            mc = ben2*pct_sim; md = max(0, mc-pa2)
            pct2 = min(100, round(pa2/mc*100, 1)) if mc > 0 else 0
            cor_md = GREEN if md > 300 else YELLOW if md > 0 else RED

            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:16px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-top:8px">
                <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #F1F5F9;font-size:13px">
                    <span style="color:#64748B">Margem consignável (40%)</span>
                    <span style="font-weight:600;color:{NAVY}">{fmt(mc)}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #F1F5F9;font-size:13px">
                    <span style="color:#64748B">Parcelas ativas</span>
                    <span style="font-weight:600;color:{RED}">{fmt(pa2)}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 0 4px;font-size:13px">
                    <span style="color:#64748B">Margem disponível</span>
                    <span style="font-size:22px;font-weight:800;color:{cor_md}">{fmt(md)}</span>
                </div>
                <div class="progress-bar-wrap">
                    <div class="progress-bar-fill" style="width:{pct2}%;background:{'#1A7A5E' if pct2<60 else '#E67E22' if pct2<90 else '#C0392B'}"></div>
                </div>
                <div style="font-size:10px;color:#94A3B8;margin-top:4px">Comprometido: {pct2:.0f}%</div>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("#### Simulação")
            val2  = st.number_input("Valor desejado (R$)", min_value=0.0, value=3000.0, step=500.0)
            prazo = st.select_slider("Prazo", options=[12,24,36,48,60,72,84,96,108], value=36)
            taxa3 = st.slider("Taxa (% a.m.)", 0.5, 3.5, 1.8, 0.1)

            if val2 > 0 and ben2 > 0:
                r2    = taxa3/100
                fator = (r2*(1+r2)**prazo)/((1+r2)**prazo-1)
                parc  = val2*fator; tot = parc*prazo; jur = tot-val2
                cabe  = parc <= md; cr = GREEN if cabe else RED
                msg   = "✅ Cabe na margem" if cabe else "❌ Excede a margem"

                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.07);border-top:4px solid {cr}">
                    <div style="text-align:center;padding:12px 0 16px">
                        <div style="font-size:11px;color:#94A3B8;margin-bottom:5px">Parcela mensal</div>
                        <div style="font-size:34px;font-weight:800;color:{cr}">{fmt(parc)}</div>
                        <div style="font-size:12px;font-weight:600;color:{cr};margin-top:4px">{msg}</div>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid #F1F5F9;font-size:13px">
                        <span style="color:#64748B">Total a pagar</span><span style="font-weight:600">{fmt(tot)}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid #F1F5F9;font-size:13px">
                        <span style="color:#64748B">Juros total</span><span style="font-weight:600;color:{RED}">{fmt(jur)}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid #F1F5F9;font-size:13px">
                        <span style="color:#64748B">Comissão estimada</span><span style="font-weight:600;color:{GREEN}">{fmt(val2*0.03)}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        if val2 > 0 and ben2 > 0:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="chart-card"><div class="chart-title">Comparativo de Prazos — 🟢 verde = cabe na margem</div>', unsafe_allow_html=True)
            pzs = [12,24,36,48,60,72,84,96,108]; r2 = taxa3/100
            pcs = [round(val2*(r2*(1+r2)**p)/((1+r2)**p-1), 2) for p in pzs]
            fig5 = go.Figure(go.Bar(
                x=[f"{p}m" for p in pzs], y=pcs,
                marker_color=[GREEN if p<=md else RED for p in pcs],
                marker_line_width=0,
                text=[fmt(p) for p in pcs], textposition="outside", textfont=dict(size=10)
            ))
            fig5.add_hline(y=md, line_dash="dot", line_color=GREEN, line_width=2,
                annotation_text=f"Margem {fmt(md)}", annotation_font_size=10)
            fig5.update_layout(height=260, **plotly_theme())
            st.plotly_chart(fig5, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Calculadora de Portabilidade")
        st.caption("Verifique se vale migrar o contrato para uma taxa menor.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Contrato Atual**")
            va  = st.number_input("Saldo devedor (R$)", min_value=0.0, value=8000.0, step=100.0, key="pva")
            pra = st.number_input("Parcelas restantes", min_value=1, max_value=84, value=48, key="ppra")
            txa = st.number_input("Taxa atual (% a.m.)", min_value=0.1, max_value=5.0, value=2.1, step=0.1, key="ptxa")
        with c2:
            st.markdown("**Nova Proposta**")
            txn = st.number_input("Nova taxa (% a.m.)", min_value=0.1, max_value=5.0, value=1.7, step=0.1, key="ptxn")
            prn = st.number_input("Novo prazo (meses)", min_value=1, max_value=108, value=48, key="pprn")

        if va > 0:
            ra = txa/100; rn = txn/100
            pca = va*(ra*(1+ra)**pra)/((1+ra)**pra-1)
            pcn = va*(rn*(1+rn)**prn)/((1+rn)**prn-1)
            eco = pca-pcn; ecot = pca*pra-pcn*prn; vale = eco > 0; ce = GREEN if vale else RED
            st.markdown(f"""
            <div style="background:{'#F0FDF4' if vale else '#FEF2F2'};border:1px solid {'#86EFAC' if vale else '#FECACA'};
                border-radius:12px;padding:20px;margin-top:16px">
                <div style="font-size:13px;font-weight:700;color:{ce};margin-bottom:14px">
                    {'✅ Portabilidade VALE A PENA' if vale else '❌ Portabilidade NÃO compensa'}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;text-align:center">
                    {"".join([f'<div><div style="font-size:10px;color:#64748B;margin-bottom:3px">{l}</div><div style="font-size:17px;font-weight:700;color:{c3}">{v}</div></div>' for l,v,c3 in [("PARCELA ATUAL",fmt(pca),RED),("NOVA PARCELA",fmt(pcn),GREEN),("ECONOMIA/MÊS",fmt(abs(eco)),ce)]])}
                </div>
                <div style="text-align:center;margin-top:12px;font-size:12px;color:#64748B">
                    Economia total no período: <strong style="color:{ce}">{fmt(abs(ecot))}</strong>
                </div>
            </div>""", unsafe_allow_html=True)

# ═══ ALERTAS ═══

elif "Leads" in menu:
    page_header("📋", "Funil de Vendas", "Pipeline completo — do primeiro contato ao pagamento")

    # ── KPIs do funil ──────────────────────────────────────────────────────────
    dfl = load_leads()
    if not dfl.empty and "etapa" not in dfl.columns:
        dfl["etapa"] = dfl["status"].map({
            "Novo": "Novo Lead", "Em negociação": "Em Contato",
            "Convertido": "Contrato Pago", "Perdido": "Perdido"
        }).fillna("Novo Lead")

    ETAPAS_FUNIL = ["Novo Lead","Em Contato","Proposta Enviada","Aguard. Retorno","Aprovado","Em Formalização","Contrato Pago","Perdido"]
    CORES_ETAPA  = {"Novo Lead":"#60A5FA","Em Contato":"#FBBF24","Proposta Enviada":"#C084FC",
                    "Aguard. Retorno":"#FB923C","Aprovado":"#4ADE80","Em Formalização":"#22D3EE","Contrato Pago":"#34D399","Perdido":"#F87171"}
    TEMP_CORES   = {"Quente":"#EF4444","Morno":"#F59E0B","Frio":"#60A5FA"}

    total_leads = len(dfl) if not dfl.empty else 0
    em_aberto   = len(dfl[(~dfl["etapa"].isin(["Contrato Pago","Perdido"])) & (dfl["status"] != "Convertido")]) if not dfl.empty else 0
    convertidos = len(dfl[dfl["etapa"]=="Contrato Pago"]) if not dfl.empty else 0
    taxa_conv   = round(convertidos/total_leads*100,1) if total_leads > 0 else 0
    vl_pipeline = dfl[~dfl["etapa"].isin(["Perdido"])]["valor_estimado"].sum() if not dfl.empty and "valor_estimado" in dfl.columns else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi_html("Total Leads", total_leads, "", "navy")
    with c2: kpi_html("Em Aberto", em_aberto, "negociações ativas", "yellow")
    with c3: kpi_html("Convertidos", convertidos, "contratos pagos", "green")
    with c4: kpi_html("Conversão", f"{taxa_conv}%", "total geral", "green")
    with c5: kpi_html("Pipeline", fmt(vl_pipeline), "valor estimado", "navy")

    # Valor perdido no mês atual
    if not dfl.empty:
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        perdidos_mes = dfl[(dfl["etapa"]=="Perdido")]
        if "updated_at" in perdidos_mes.columns:
            perdidos_mes_dt = pd.to_datetime(perdidos_mes["updated_at"], errors="coerce")
            perdidos_mes = perdidos_mes[(perdidos_mes_dt.dt.month==mes_atual) & (perdidos_mes_dt.dt.year==ano_atual)]
        valor_perdido_mes = perdidos_mes["valor_estimado"].sum() if not perdidos_mes.empty else 0

        c6, = st.columns(1)
        with c6:
            st.markdown(f"""
            <div style="background:#0D1B35;border:1px solid rgba(239,68,68,0.25);border-left:4px solid #EF4444;
                border-radius:12px;padding:12px 16px;margin-top:8px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase">Valor perdido este mês</div>
                        <div style="font-size:20px;font-weight:800;color:#EF4444">{fmt(valor_perdido_mes)}</div>
                    </div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.4);text-align:right">{len(perdidos_mes)} lead(s) perdido(s)<br>oportunidade de recuperação</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Tabs: Kanban | Lista | Novo Lead ───────────────────────────────────────
    tab_kanban, tab_lista, tab_novo, tab_reaproveitar = st.tabs(["🗂 Kanban", "📋 Lista Completa", "＋ Novo Lead", "♻️ Reaproveitar"])

    with tab_reaproveitar:
        st.markdown("""
        <div style="background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);
            border-radius:10px;padding:12px 16px;margin-bottom:16px">
            <div style="color:#60A5FA;font-size:12px;font-weight:700;margin-bottom:4px">
                ♻️ Leads perdidos que podem voltar
            </div>
            <div style="color:rgba(255,255,255,0.55);font-size:11px">
                Margem pode ter mudado desde a perda (reajuste INSS, quitação de outras dívidas).
                Revise antes de descartar definitivamente.
            </div>
        </div>
        """, unsafe_allow_html=True)

        perdidos_df = dfl[dfl["etapa"]=="Perdido"] if not dfl.empty else pd.DataFrame()

        if perdidos_df.empty:
            st.info("Nenhum lead perdido no momento. 🎉")
        else:
            # Priorizar os com motivo "Sem margem" — são os que mais mudam com reajuste
            motivo_filtro = st.selectbox("Filtrar por motivo", ["Todos"] + sorted(perdidos_df["motivo_perda"].dropna().unique().tolist()) if "motivo_perda" in perdidos_df.columns else ["Todos"])
            if motivo_filtro != "Todos" and "motivo_perda" in perdidos_df.columns:
                perdidos_df = perdidos_df[perdidos_df["motivo_perda"] == motivo_filtro]

            for _, lp in perdidos_df.iterrows():
                motivo = lp.get("motivo_perda", "Não informado") or "Não informado"
                dias_perdido = (datetime.now() - pd.to_datetime(lp.get("updated_at", datetime.now()), errors="coerce")).days
                sugestao = ""
                if motivo == "Sem margem disponível" and dias_perdido > 60:
                    sugestao = "💡 Pode ter passado por reajuste INSS — vale reconferir"

                rp1, rp2 = st.columns([4,1])
                with rp1:
                    st.markdown(f"""
                    <div style="background:#0D1B35;border:1px solid rgba(239,68,68,0.2);border-left:3px solid #EF4444;
                        border-radius:10px;padding:10px 14px;margin-bottom:6px">
                        <div style="color:white;font-size:13px;font-weight:700">{lp['nome']}</div>
                        <div style="color:rgba(255,255,255,0.4);font-size:11px">{motivo} · perdido há {dias_perdido} dias</div>
                        {f'<div style="color:#FBBF24;font-size:11px;margin-top:4px">{sugestao}</div>' if sugestao else ''}
                    </div>
                    """, unsafe_allow_html=True)
                with rp2:
                    if st.button("Reabrir", key=f"reab_{lp['id']}", use_container_width=True):
                        upd_lead_etapa(lp["id"], "Novo Lead", {
                            "temperatura": "Morno",
                            "ultimo_contato": datetime.now().isoformat(),
                            "observacoes": f"[REABERTO {date.today().strftime('%d/%m/%Y')}] {lp.get('observacoes','')}"
                        })
                        st.success(f"✅ {lp['nome']} reaberto!")
                        st.rerun()

    with tab_novo:
        with st.form("form_lead_novo", clear_on_submit=True):
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                ln  = st.text_input("Nome completo *")
                lt  = st.text_input("Telefone *")
                le  = st.text_input("Email")
                lcp = st.text_input("CPF")
            with c2:
                lc  = st.selectbox("Canal de entrada", ["WhatsApp","Indicação","Panfletagem","Rádio","Instagram","Google","Presencial","Outros"])
                li  = st.selectbox("Produto de interesse", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor","Empréstimo Pessoal"])
                lb  = st.number_input("Benefício / Salário (R$)", min_value=0.0, step=50.0)
                lv  = st.number_input("Valor estimado do negócio (R$)", min_value=0.0, step=100.0)
            with c3:
                let = st.selectbox("Etapa inicial", ETAPAS_FUNIL[:4])
                lte = st.selectbox("Temperatura", ["Quente","Morno","Frio"])
                ldr = st.date_input("Data prevista retorno", value=date.today()+timedelta(days=1))
                lob = st.text_area("Observações", height=68)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.form_submit_button("✅ Cadastrar Lead no Funil", use_container_width=True):
                if not ln or not lt:
                    st.error("Nome e telefone são obrigatórios.")
                else:
                    ins_lead({"nome":ln,"telefone":lt,"email":le if le else None,
                        "canal":lc,"interesse":li,"beneficio":float(lb),
                        "valor_estimado":float(lv),"status":let,"etapa":let,
                        "temperatura":lte,"data_retorno":str(ldr),"observacoes":lob,
                        "ultimo_contato":datetime.now().isoformat()})
                    st.success(f"✅ {ln} adicionado ao funil!")
                    st.rerun()

    with tab_kanban:
        if dfl.empty:
            st.info("Nenhum lead cadastrado. Use a aba '＋ Novo Lead'.")
        else:
            # Funil visual com % de conversão
            etapas_ativas = [e for e in ETAPAS_FUNIL if e != "Perdido"]
            dfl_ativo = dfl[dfl["status"] != "Convertido"]
            totais = {e: len(dfl_ativo[dfl_ativo["etapa"]==e]) for e in ETAPAS_FUNIL}

            # Barra de progresso do funil
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Distribuição do Funil</div>', unsafe_allow_html=True)
            funil_html = '<div style="display:flex;gap:4px;align-items:stretch;height:36px;border-radius:10px;overflow:hidden">'
            for etapa in etapas_ativas:
                cnt = totais.get(etapa, 0)
                pct = round(cnt/max(total_leads,1)*100)
                cor = CORES_ETAPA[etapa]
                if pct > 0:
                    funil_html += (f'<div style="flex:{pct};background:{cor};display:flex;align-items:center;'
                                   f'justify-content:center;font-size:10px;font-weight:700;color:white;'
                                   f'white-space:nowrap;padding:0 4px" title="{etapa}: {cnt}">'
                                   f'{cnt if pct>8 else ""}</div>')
            funil_html += '</div><div style="display:flex;gap:4px;margin-top:6px;flex-wrap:wrap">'
            for etapa in etapas_ativas:
                cnt = totais.get(etapa, 0)
                cor = CORES_ETAPA[etapa]
                funil_html += (f'<span style="font-size:10px;color:rgba(255,255,255,0.6);'
                               f'display:flex;align-items:center;gap:4px">'
                               f'<span style="width:8px;height:8px;border-radius:50%;background:{cor};display:inline-block"></span>'
                               f'{etapa} ({cnt})</span>')
            funil_html += '</div>'
            st.markdown(funil_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Saúde do Funil + Tempo médio por etapa ──────────────────────
            if not dfl_ativo.empty:
                dfl_ativo_calc = dfl_ativo.copy()
                dfl_ativo_calc["dias_na_etapa"] = (datetime.now() - pd.to_datetime(dfl_ativo_calc["updated_at"], errors="coerce")).dt.days.fillna(0)
                leads_parados = len(dfl_ativo_calc[dfl_ativo_calc["dias_na_etapa"] > 2])
                tempo_medio = dfl_ativo_calc["dias_na_etapa"].mean() if len(dfl_ativo_calc) > 0 else 0

                taxa_conv_hist = (len(dfl[dfl["status"]=="Convertido"]) / max(len(dfl),1)) * 100
                if taxa_conv_hist >= 30 and leads_parados <= 2:
                    saude_cor, saude_txt, saude_emoji = "#4ADE80", "Saudável", "🟢"
                elif taxa_conv_hist >= 15 or leads_parados <= 5:
                    saude_cor, saude_txt, saude_emoji = "#FBBF24", "Atenção", "🟡"
                else:
                    saude_cor, saude_txt, saude_emoji = "#EF4444", "Crítico", "🔴"

                st.markdown(f"""
                <div style="display:flex;gap:12px;margin-top:12px;flex-wrap:wrap">
                    <div style="flex:1;min-width:140px;background:#0D1B35;border:1px solid {saude_cor}40;
                        border-left:4px solid {saude_cor};border-radius:10px;padding:10px 14px">
                        <div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase">Saúde do Funil</div>
                        <div style="font-size:15px;font-weight:800;color:{saude_cor}">{saude_emoji} {saude_txt}</div>
                    </div>
                    <div style="flex:1;min-width:140px;background:#0D1B35;border:1px solid rgba(255,255,255,0.1);
                        border-radius:10px;padding:10px 14px">
                        <div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase">Tempo médio/etapa</div>
                        <div style="font-size:15px;font-weight:800;color:white">{tempo_medio:.1f} dias</div>
                    </div>
                    <div style="flex:1;min-width:140px;background:#0D1B35;border:1px solid rgba(255,255,255,0.1);
                        border-radius:10px;padding:10px 14px">
                        <div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase">Leads parados (+2d)</div>
                        <div style="font-size:15px;font-weight:800;color:{'#EF4444' if leads_parados>3 else 'white'}">{leads_parados}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Kanban por etapas (sem Perdido)
            n_cols = 4
            for row_start in range(0, len(etapas_ativas), n_cols):
                etapas_row = etapas_ativas[row_start:row_start+n_cols]
                cols = st.columns(len(etapas_row))
                for col_idx, etapa in enumerate(etapas_row):
                    grupo = dfl[(dfl["etapa"]==etapa) & (dfl["status"] != "Convertido")]
                    cor   = CORES_ETAPA[etapa]
                    with cols[col_idx]:
                        st.markdown(f"""
                        <div style="background:#0D1B35;border:1px solid {cor}30;border-top:3px solid {cor};
                            border-radius:12px;padding:12px;min-height:80px">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                                <span style="color:{cor};font-size:12px;font-weight:700">{etapa}</span>
                                <span style="background:{cor}20;color:{cor};padding:1px 8px;
                                    border-radius:99px;font-size:10px;font-weight:700">{len(grupo)}</span>
                            </div>""", unsafe_allow_html=True)

                        for _, row in grupo.iterrows():
                            temp = row.get("temperatura","Frio")
                            tc   = TEMP_CORES.get(temp,"#60A5FA")
                            vl   = row.get("valor_estimado",0) or 0
                            st.markdown(f"""
                            <div style="background:rgba(255,255,255,0.04);border-radius:9px;
                                padding:9px 11px;margin-bottom:7px;border-left:3px solid {tc}">
                                <div style="font-size:12px;font-weight:700;color:white;margin-bottom:2px">
                                    {row['nome'].split()[0]} {row['nome'].split()[1] if len(row['nome'].split())>1 else ''}
                                </div>
                                <div style="font-size:10px;color:rgba(255,255,255,0.45)">
                                    {row.get('interesse','')[:22]}
                                </div>
                                <div style="display:flex;justify-content:space-between;margin-top:5px;align-items:center">
                                    <span style="font-size:10px;font-weight:700;color:{tc}">{temp}</span>
                                    {f'<span style="font-size:10px;color:#4ADE80;font-weight:600">{fmt(vl)}</span>' if vl>0 else ''}
                                </div>
                            </div>""", unsafe_allow_html=True)

                            nova_etapa = st.selectbox(
                                "Mover",
                                ETAPAS_FUNIL,
                                index=ETAPAS_FUNIL.index(etapa),
                                key=f"et_{row['id']}",
                                label_visibility="collapsed"
                            )
                            if nova_etapa != etapa:
                                extra = {"ultimo_contato": datetime.now().isoformat()}
                                if nova_etapa == "Proposta Enviada":
                                    extra["data_proposta"] = str(date.today())
                                elif nova_etapa in ["Contrato Pago","Aprovado"]:
                                    extra["data_contato"] = str(date.today())
                                upd_lead_etapa(row["id"], nova_etapa, extra)
                                st.rerun()

                        st.markdown('</div>', unsafe_allow_html=True)

            # Perdidos separado
            perdidos = dfl[(dfl["etapa"]=="Perdido") & (dfl["status"] != "Convertido")]
            if len(perdidos) > 0:
                st.markdown(f"""
                <div style="background:#0D1B35;border:1px solid #F8717130;border-radius:12px;
                    padding:12px 16px;margin-top:8px">
                    <div style="color:#F87171;font-size:12px;font-weight:700;margin-bottom:8px">
                        ❌ Perdidos — {len(perdidos)} lead(s)
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:6px">""", unsafe_allow_html=True)
                for _, row in perdidos.iterrows():
                    st.markdown(f"""
                    <span style="background:rgba(248,113,113,0.1);border:1px solid #F8717130;
                        border-radius:7px;padding:4px 10px;font-size:11px;color:rgba(255,255,255,0.6)">
                        {row['nome'].split()[0]}
                    </span>""", unsafe_allow_html=True)
                st.markdown('</div></div>', unsafe_allow_html=True)

    with tab_lista:
        if dfl.empty:
            st.info("Nenhum lead cadastrado.")
        else:
            # Filtros
            cf1, cf2, cf3, cf4 = st.columns(4)
            with cf4: mostrar_conv = st.checkbox("Ver convertidos", value=False)
            with cf1: fet = st.multiselect("Etapa", ETAPAS_FUNIL, default=[e for e in ETAPAS_FUNIL if e not in ["Contrato Pago","Perdido"]])
            with cf2: ftp = st.multiselect("Temperatura", ["Quente","Morno","Frio"], default=["Quente","Morno","Frio"])
            with cf3: fca = st.multiselect("Canal", sorted(dfl["canal"].dropna().unique().tolist()), default=sorted(dfl["canal"].dropna().unique().tolist()))

            if not fet: fet = ETAPAS_FUNIL
            if not ftp: ftp = ["Quente","Morno","Frio"]
            if not fca: fca = dfl["canal"].dropna().unique().tolist()

            if mostrar_conv:
                # Mostra APENAS convertidos (status=Convertido)
                dff = dfl[dfl["status"] == "Convertido"] if not dfl.empty else dfl
            else:
                # Mostra leads ativos — exclui convertidos
                dff = dfl[
                    dfl["etapa"].isin(fet) &
                    dfl["canal"].isin(fca) &
                    dfl["temperatura"].isin(ftp) &
                    (dfl["status"] != "Convertido")
                ] if not dfl.empty else dfl
            dff = dff.sort_values(["temperatura","etapa"], key=lambda x: x.map({"Quente":0,"Morno":1,"Frio":2}).fillna(3) if x.name=="temperatura" else x)

            st.markdown(f"<p style='color:rgba(255,255,255,0.4);font-size:12px;margin:6px 0 10px'><b>{len(dff)}</b> lead(s)</p>", unsafe_allow_html=True)

            for _, row in dff.iterrows():
                et   = row.get("etapa","Novo Lead")
                cor  = CORES_ETAPA.get(et,"#60A5FA")
                temp = row.get("temperatura","Frio")
                tc   = TEMP_CORES.get(temp,"#60A5FA")
                vl   = row.get("valor_estimado",0) or 0

                ca, cb = st.columns([4,1])
                with ca:
                    st.markdown(f"""
                    <div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.06);
                        border-radius:11px;padding:12px 16px;border-left:4px solid {cor};margin-bottom:6px">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <div>
                                <div style="font-size:14px;font-weight:700;color:white">{row['nome']}</div>
                                <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:2px">
                                    {row.get('canal','')} · {row.get('interesse','')}
                                    {' · '+row.get('telefone','') if row.get('telefone') else ''}
                                </div>
                                <div style="margin-top:7px;display:flex;gap:6px;flex-wrap:wrap">
                                    <span style="background:{cor}20;color:{cor};padding:2px 9px;border-radius:99px;font-size:10px;font-weight:700">{et}</span>
                                    <span style="background:{tc}20;color:{tc};padding:2px 9px;border-radius:99px;font-size:10px;font-weight:700">{temp}</span>
                                    {f'<span style="color:#4ADE80;font-size:11px;font-weight:600">{fmt(vl)}</span>' if vl>0 else ''}
                                </div>
                            </div>
                            <div style="text-align:right">
                                <div style="font-size:10px;color:rgba(255,255,255,0.3)">Benefício</div>
                                <div style="font-size:16px;font-weight:800;color:white">{fmt(row.get('beneficio',0))}</div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with cb:
                    nova_et = st.selectbox("Etapa", ETAPAS_FUNIL,
                        index=ETAPAS_FUNIL.index(et) if et in ETAPAS_FUNIL else 0,
                        key=f"ls_et_{row['id']}", label_visibility="collapsed")
                    if nova_et != et:
                        if nova_et == "Perdido":
                            st.session_state[f"pedir_motivo_{row['id']}"] = True
                        else:
                            upd_lead_etapa(row["id"], nova_et, {"ultimo_contato": datetime.now().isoformat()})
                            st.rerun()

                    if st.session_state.get(f"pedir_motivo_{row['id']}"):
                        motivo_sel = st.selectbox("Motivo da perda", [
                            "Sem margem disponível",
                            "Concorrência ofereceu melhor",
                            "Desistiu / não tem mais interesse",
                            "Não responde / sem contato",
                            "Documentação reprovada",
                            "Representante legal (inelegível)",
                            "Benefício bloqueado no INSS",
                            "Outro"
                        ], key=f"motivo_sel_{row['id']}")
                        if st.button("Confirmar perda", key=f"conf_perda_{row['id']}", use_container_width=True):
                            upd_lead_etapa(row["id"], "Perdido", {
                                "ultimo_contato": datetime.now().isoformat(),
                                "motivo_perda": motivo_sel
                            })
                            st.session_state[f"pedir_motivo_{row['id']}"] = False
                            st.rerun()
                    nova_tp = st.selectbox("Temp", ["Quente","Morno","Frio"],
                        index=["Quente","Morno","Frio"].index(temp) if temp in ["Quente","Morno","Frio"] else 2,
                        key=f"ls_tp_{row['id']}", label_visibility="collapsed")
                    if nova_tp != temp:
                        sb.table("leads").update({"temperatura": nova_tp}).eq("id", row["id"]).execute()
                        st.rerun()

                    if et in ["Aprovado","Contrato Pago"] and row.get("etapa") != "convertido_cliente":
                        if st.button("👤 → Cliente", key=f"conv_{row['id']}", help="Converter para cliente"):
                            st.session_state[f"confirm_conv_{row['id']}"] = True
                    if st.session_state.get(f"confirm_conv_{row['id']}"):
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,#0D2B1F,#0A2318);
                            border:1px solid rgba(74,222,128,0.3);border-radius:12px;
                            padding:14px 16px;margin-top:8px">
                            <div style="color:#4ADE80;font-size:12px;font-weight:700;margin-bottom:4px">
                                👤 Converter para Cliente
                            </div>
                            <div style="color:rgba(255,255,255,0.7);font-size:12px">
                                <b style="color:white">{row['nome']}</b> será migrado para a base de clientes.
                                Os dados serão transferidos automaticamente.
                            </div>
                        </div>""", unsafe_allow_html=True)
                        cc1, cc2 = st.columns(2)
                        with cc1:
                            if st.button("Confirmar conversão", key=f"conv_ok_{row['id']}", use_container_width=True):
                                converter_lead_para_cliente(row)
                                st.session_state[f"confirm_conv_{row['id']}"] = False
                                st.success(f"✅ {row['nome'].split()[0]} convertido para cliente!")
                                st.rerun()
                        with cc2:
                            if st.button("Voltar", key=f"conv_no_{row['id']}", use_container_width=True):
                                st.session_state[f"confirm_conv_{row['id']}"] = False
                                st.rerun()


elif "Alertas" in menu:
    page_header("🔔", "Central de Alertas", "Inteligência automática — oportunidades e lembretes em tempo real")

    df_cli  = load_clientes()
    df_lds  = load_leads()
    df_alts = load_alertas()

    # Gerar alertas automáticos
    if not df_cli.empty or not df_lds.empty:
        gerar_alertas_automaticos(df_cli, df_lds)
        df_alts = load_alertas()  # recarrega após geração

    # ── KPIs ───────────────────────────────────────────────────────────────────
    urgentes  = len(df_alts[df_alts["prioridade"]=="urgente"])  if not df_alts.empty else 0
    altas     = len(df_alts[df_alts["prioridade"]=="alta"])     if not df_alts.empty else 0
    medias    = len(df_alts[df_alts["prioridade"]=="media"])    if not df_alts.empty else 0
    opp_inss  = len(df_cli[df_cli["dias"].notna() & (df_cli["dias"].astype(float)<=2)]) if not df_cli.empty else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_html("🚨 Urgentes",  urgentes, "ação imediata",  "red")
    with c2: kpi_html("⚡ Alta",       altas,    "hoje",           "yellow")
    with c3: kpi_html("📌 Médios",     medias,   "esta semana",    "navy")
    with c4: kpi_html("💰 INSS Hoje",  opp_inss, "oportunidade",   "green")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    tab_auto, tab_opp, tab_radar = st.tabs(["🤖 Alertas Automáticos", "💰 Oportunidades INSS", "🎯 Radar de Score"])

    with tab_auto:
        if df_alts.empty:
            st.markdown("""
            <div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.06);border-radius:12px;
                padding:32px;text-align:center">
                <div style="font-size:32px;margin-bottom:8px">✅</div>
                <div style="color:white;font-size:15px;font-weight:600">Tudo em ordem</div>
                <div style="color:rgba(255,255,255,0.4);font-size:12px;margin-top:4px">
                    Nenhum alerta pendente no momento
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            PRIOR_CONFIG = {
                "urgente": ("#EF4444","🚨","Urgente"),
                "alta":    ("#F59E0B","⚡","Alta"),
                "media":   ("#60A5FA","📌","Média"),
            }
            TIPO_CONFIG = {
                "lead_parado":      ("Lead parado",       "#FBBF24"),
                "inss_oportunidade":("INSS + Margem",     "#4ADE80"),
                "proposta_sem_resp":("Proposta sem resp.", "#C084FC"),
                "cliente_quente":   ("Cliente quente",    "#FB923C"),
            }

            for _, alt in df_alts.sort_values("prioridade", key=lambda x: x.map({"urgente":0,"alta":1,"media":2}).fillna(3)).iterrows():
                pr  = alt.get("prioridade","media")
                cor, icon, label = PRIOR_CONFIG.get(pr, ("#60A5FA","📌","Média"))
                tipo_label, tipo_cor = TIPO_CONFIG.get(alt.get("tipo",""), ("Alerta",cor))
                tempo = ""
                try:
                    criado = pd.to_datetime(alt["criado_em"])
                    if hasattr(criado,'tzinfo') and criado.tzinfo:
                        criado = criado.tz_localize(None)
                    h = int((datetime.now()-criado).total_seconds()/3600)
                    tempo = f"{h}h atrás" if h < 24 else f"{h//24}d atrás"
                except: pass

                ca, cb = st.columns([5,1])
                with ca:
                    st.markdown(f"""
                    <div style="background:#0D1B35;border:1px solid {cor}30;border-radius:11px;
                        padding:12px 16px;margin-bottom:7px;border-left:4px solid {cor}">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <div style="flex:1">
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                                    <span style="font-size:15px">{icon}</span>
                                    <span style="color:white;font-size:13px;font-weight:700">{alt['titulo']}</span>
                                </div>
                                <div style="color:rgba(255,255,255,0.5);font-size:11px">{alt.get('descricao','')}</div>
                                <div style="display:flex;gap:6px;margin-top:7px">
                                    <span style="background:{cor}20;color:{cor};padding:1px 8px;border-radius:99px;font-size:10px;font-weight:700">{label}</span>
                                    <span style="background:{tipo_cor}15;color:{tipo_cor};padding:1px 8px;border-radius:99px;font-size:10px;font-weight:600">{tipo_label}</span>
                                </div>
                            </div>
                            <div style="color:rgba(255,255,255,0.25);font-size:10px;white-space:nowrap;margin-left:12px">{tempo}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with cb:
                    if st.button("✓ Lido", key=f"alt_lido_{alt['id']}"):
                        marcar_alerta_lido(alt["id"])
                        st.rerun()

    with tab_opp:
        if df_cli.empty:
            st.info("Nenhum cliente cadastrado ainda.")
        else:
            opp  = df_cli[df_cli["margem"]>300].sort_values("score", ascending=False)
            bx   = df_cli[(df_cli["margem"]>0)&(df_cli["margem"]<=300)].sort_values("score", ascending=False)
            sm   = df_cli[df_cli["margem"]<=0]
            ph   = df_cli[df_cli["dias"].notna() & (df_cli["dias"].astype(float)<=2)]

            if len(ph) > 0:
                st.markdown(f"<div style='color:#EF4444;font-size:13px;font-weight:700;margin-bottom:10px'>🚨 INSS Cai Hoje ou Amanhã — Contatar Agora</div>", unsafe_allow_html=True)
                for _, row in ph.iterrows():
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#2B1A0D,#231408);border:1px solid rgba(239,68,68,0.3);
                        border-radius:12px;padding:14px 18px;margin-bottom:8px">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="color:white;font-weight:700;font-size:14px">{row['nome']}</div>
                                <div style="color:rgba(255,255,255,0.5);font-size:11px;margin-top:2px">
                                    {row['tel_d']} · {row.get('interesse','')} · Score {row['score']}%
                                </div>
                                <div style="margin-top:6px">
                                    <span style="background:rgba(239,68,68,0.15);color:#EF4444;padding:2px 9px;border-radius:99px;font-size:10px;font-weight:700">🚨 URGENTE</span>
                                    <span style="background:rgba(96,165,250,0.15);color:#60A5FA;padding:2px 9px;border-radius:99px;font-size:10px;font-weight:700;margin-left:4px">{row['status']}</span>
                                </div>
                            </div>
                            <div style="text-align:right">
                                <div style="color:rgba(255,255,255,0.3);font-size:10px">INSS em</div>
                                <div style="font-size:28px;font-weight:800;color:#EF4444">{int(row['dias'])} dia(s)</div>
                                <div style="color:rgba(255,255,255,0.4);font-size:11px">{row['prox'].strftime('%d/%m') if row['prox'] else ''}</div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)

            if len(opp) > 0:
                st.markdown(f"<div style='color:#4ADE80;font-size:13px;font-weight:700;margin:14px 0 10px'>💰 Oportunidades — Margem > R$ 300</div>", unsafe_allow_html=True)
                for _, row in opp.iterrows():
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#0D2B1F,#0A2318);border:1px solid rgba(74,222,128,0.2);
                        border-radius:11px;padding:12px 16px;margin-bottom:7px">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="color:white;font-weight:700;font-size:13px">{row['nome']}</div>
                                <div style="color:rgba(255,255,255,0.4);font-size:11px;margin-top:2px">
                                    {row['tel_d']} · {row.get('interesse','')} · {row.get('canal','')}
                                </div>
                                <div style="margin-top:6px">
                                    <span style="background:rgba(74,222,128,0.12);color:#4ADE80;padding:2px 9px;border-radius:99px;font-size:10px;font-weight:700">Score {row['score']}%</span>
                                    <span style="background:rgba(96,165,250,0.12);color:#60A5FA;padding:2px 9px;border-radius:99px;font-size:10px;margin-left:4px">{row['status']}</span>
                                </div>
                            </div>
                            <div style="text-align:right">
                                <div style="color:rgba(255,255,255,0.3);font-size:10px">Margem disponível</div>
                                <div style="font-size:22px;font-weight:800;color:#4ADE80">{fmt(row['margem'])}</div>
                                <div style="color:rgba(255,255,255,0.3);font-size:10px">Ben: {fmt(row['beneficio'])}</div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)

    with tab_radar:
        if df_cli.empty:
            st.info("Nenhum cliente cadastrado.")
        else:
            df_radar = df_cli.sort_values("score", ascending=False)
            for _, row in df_radar.iterrows():
                pct = row["score"]
                cor = "#4ADE80" if pct>=75 else "#FBBF24" if pct>=50 else "#F87171"
                st.markdown(f"""
                <div style="background:#0D1B35;border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px;padding:10px 14px;margin-bottom:6px">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                        <div>
                            <span style="color:white;font-weight:600;font-size:13px">{row['nome']}</span>
                            <span style="color:rgba(255,255,255,0.35);font-size:11px;margin-left:8px">{row['tel_d']}</span>
                        </div>
                        <span style="color:{cor};font-weight:800;font-size:15px">{pct}%</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.07);border-radius:99px;height:5px;overflow:hidden">
                        <div style="width:{pct}%;height:100%;background:{cor};border-radius:99px"></div>
                    </div>
                    <div style="font-size:10px;color:rgba(255,255,255,0.35);margin-top:4px">
                        Margem: {fmt(row['margem'])} · Ben: {fmt(row['beneficio'])} · {row.get('interesse','')}
                    </div>
                </div>""", unsafe_allow_html=True)


elif "Agenda" in menu:
    page_header("📅", "Agenda de Follow-ups", "Seus compromissos e lembretes de contato")

    # Form para novo agendamento direto na Agenda
    df_cli_ag = load_clientes()
    if not df_cli_ag.empty:
        if st.button("＋ Agendar Novo Follow-up", key="btn_new_fu"):
            st.session_state["show_form_fu"] = not st.session_state.get("show_form_fu", False)
        if st.session_state.get("show_form_fu", False):
            with st.form("form_agenda_nova", clear_on_submit=True):
                cli_ag = {r["nome"]: r["id"] for _, r in df_cli_ag.iterrows()}
                c1, c2 = st.columns(2)
                with c1:
                    cli_sel_ag = st.selectbox("Cliente", list(cli_ag.keys()))
                    data_ag = st.date_input("Data do Follow-up", value=date.today() + timedelta(days=1))
                with c2:
                    motivo_ag = st.text_area("Motivo / Observação", height=80)
                if st.form_submit_button("📅 Agendar Follow-up", use_container_width=True):
                    ins_fu({"cliente_id": cli_ag[cli_sel_ag], "data_followup": str(data_ag), "motivo": motivo_ag})
                    st.success(f"✅ Follow-up agendado para {data_ag.strftime('%d/%m/%Y')}!")
                    st.rerun()
    else:
        st.info("Cadastre clientes primeiro para poder agendar follow-ups.")

    dfa2 = load_fu()
    if not dfa2.empty:
        dfa2["data_followup"] = pd.to_datetime(dfa2["data_followup"]).dt.date
        hoje2 = date.today()
        venc  = dfa2[dfa2["data_followup"] < hoje2].sort_values("data_followup")
        hj    = dfa2[dfa2["data_followup"] == hoje2]
        prx   = dfa2[dfa2["data_followup"] > hoje2].sort_values("data_followup")

        for titulo, grupo, cor, bg in [
            ("🚨 Vencidos", venc, RED, "#FEF2F2"),
            ("📌 Hoje", hj, GREEN, "#F0FDF4"),
            ("📆 Próximos", prx, NAVY, "#F8FAFC"),
        ]:
            if len(grupo) == 0: continue
            st.markdown(f"<div style='font-size:13px;font-weight:700;color:{cor};margin:14px 0 8px'>{titulo} — {len(grupo)}</div>", unsafe_allow_html=True)
            for _, r in grupo.iterrows():
                ca2, cb2 = st.columns([4, 1])
                with ca2:
                    st.markdown(f"""
                    <div style="background:{bg};border-radius:10px;padding:10px 14px;
                        margin-bottom:6px;border-left:3px solid {cor}">
                        <span style="font-weight:700;color:{NAVY}">{r['cliente_nome']}</span>
                        <span style="font-size:10px;color:#94A3B8;margin-left:8px">{r['data_followup'].strftime('%d/%m/%Y') if cor!=GREEN else 'Hoje'}</span>
                        <br><span style="font-size:12px;color:#475569">{r['motivo']}</span>
                    </div>""", unsafe_allow_html=True)
                with cb2:
                    if st.button("✅ Feito", key=f"dfu_{r['id']}"):
                        del_fu(r["id"])
                        st.rerun()
    else:
        st.info("Nenhum follow-up agendado. Agende na aba Clientes.")

# ═══ EMAIL MARKETING ═══
elif "Email" in menu:
    page_header("📧", "Email Marketing", "Campanhas via Brevo — 300 emails/dia gratuitos")

    st.markdown("""
    <div style="background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.3);
        border-radius:10px;padding:12px 16px;margin-bottom:16px">
        <div style="color:#FCD34D;font-size:13px;font-weight:700;margin-bottom:4px">
            ⚠️ Configuração necessária para envio de emails
        </div>
        <div style="color:rgba(255,255,255,0.6);font-size:12px;line-height:1.6">
            Para os emails chegarem, você precisa verificar o domínio/email remetente no Brevo:<br>
            1. Acesse <b>app.brevo.com</b> → Configurações → Remetentes e domínios<br>
            2. Adicione e verifique: <b>nucleocastelo.credito@gmail.com</b><br>
            3. Clique no link de verificação que o Brevo enviar para esse email<br>
            Sem isso, os emails são rejeitados silenciosamente.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = load_clientes()
    dce = df[df["email"].notna() & (df["email"] != "")] if not df.empty else pd.DataFrame()

    c1, c2, c3 = st.columns(3)
    with c1: kpi_html("Com Email",   len(dce),  "",             "navy")
    with c2: kpi_html("Envios/Dia",  "300",     "plano gratuito","green")
    with c3: kpi_html("Custo Mensal","R$ 0,00", "Brevo free",   "green")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["📅 Calendário INSS", "💡 Dica Financeira", "📣 Campanha Livre", "🎯 Segmentação"])

    with t1:
        st.markdown("Envia o próximo pagamento INSS personalizado para cada cliente.")
        if dce.empty:
            st.warning("Nenhum cliente com email cadastrado.")
        else:
            sel = st.multiselect("Selecionar clientes", dce["nome"].tolist(), default=dce["nome"].tolist())
            if st.button("📧 Enviar Calendário INSS", use_container_width=True):
                env = 0
                for _, row in dce[dce["nome"].isin(sel)].iterrows():
                    pg_d, dias_d = prox_pg(row["cpf_raw"])
                    html = f'<div style="font-family:Inter,sans-serif;max-width:560px;margin:0 auto"><div style="background:{NAVY};padding:24px;border-radius:12px 12px 0 0"><h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:28px;border-radius:0 0 12px 12px"><p style="font-size:16px">Olá, <b>{row["nome"].split()[0]}</b>!</p><div style="background:#F0FDF4;border-radius:10px;padding:16px;text-align:center;margin:16px 0"><div style="font-size:11px;color:#16A34A;font-weight:600;text-transform:uppercase">Próximo Pagamento INSS</div><div style="font-size:28px;font-weight:800;color:{NAVY}">{pg_d.strftime("%d/%m/%Y") if pg_d else "Em breve"}</div>{f"<div style=color:#64748B;font-size:13px>Em {dias_d} dia(s)</div>" if dias_d is not None else ""}</div><a href="https://wa.me/5511952723015" style="display:inline-block;background:{GREEN};color:white;padding:12px 28px;border-radius:99px;text-decoration:none;font-weight:600">💬 Falar no WhatsApp</a></div></div>'
                    ok_e, err_e = send_email_safe(row["email"], row["nome"], "Seu INSS — Núcleo Crédito", html)
                    if ok_e: env += 1
                st.success(f"✅ {env} email(s) enviado(s)!")

    with t2:
        DICAS = [
            ("Proteja seu benefício", "Nunca forneça sua senha do INSS por telefone ou WhatsApp. Golpistas fingem ser funcionários de bancos para roubar seu benefício. Em caso de dúvida, nos contate diretamente."),
            ("Portabilidade pode economizar muito", "Se você tem um contrato com taxa acima de 2%, pode migrar para uma taxa menor sem nenhum custo. Isso pode reduzir sua parcela mensal significativamente."),
            ("O que é margem consignável?", "É o valor máximo que pode ser descontado do seu benefício pelo INSS — até 40%. Consulte quanto você ainda tem disponível gratuitamente."),
            ("Janeiro: melhor mês para crédito", "Com o reajuste anual do INSS, sua margem aumenta. Aproveite para obter melhores condições de crédito ou reduzir parcelas existentes."),
        ]
        ds = st.selectbox("Escolha a dica", [d[0] for d in DICAS])
        db = next(d[1] for d in DICAS if d[0] == ds)
        st.info(db)
        if not dce.empty:
            sel2 = st.multiselect("Clientes", dce["nome"].tolist(), default=dce["nome"].tolist(), key="ds2")
            if st.button("📧 Enviar Dica", use_container_width=True):
                env2 = 0
                for _, row in dce[dce["nome"].isin(sel2)].iterrows():
                    html = f'<div style="font-family:Inter,sans-serif;max-width:560px;margin:0 auto"><div style="background:{NAVY};padding:24px;border-radius:12px 12px 0 0"><h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:28px;border-radius:0 0 12px 12px"><p>Olá, <b>{row["nome"].split()[0]}</b>!</p><div style="border-left:4px solid {GREEN};padding:14px 18px;background:#F8FFFE;border-radius:0 8px 8px 0;margin:16px 0"><b style="color:{NAVY}">{ds}</b><p style="color:#475569;margin-top:8px;line-height:1.6">{db}</p></div><a href="https://wa.me/5511952723015" style="background:{GREEN};color:white;padding:12px 28px;border-radius:99px;text-decoration:none;font-weight:600">💬 Tirar dúvidas</a></div></div>'
                    ok_e, err_e = send_email_safe(row["email"], row["nome"], f"💡 {ds} — Núcleo Crédito", html)
                    if ok_e: env2 += 1
                st.success(f"✅ {env2} email(s) enviado(s)!")

    with t3:
        ca3 = st.text_input("Assunto do email")
        ct3 = st.text_input("Título da mensagem")
        cc3 = st.text_area("Corpo da mensagem", height=100)
        if not dce.empty:
            sel3 = st.multiselect("Clientes", dce["nome"].tolist(), key="ds3")
            if st.button("📣 Enviar Campanha", use_container_width=True):
                if not ca3 or not cc3:
                    st.error("Preencha assunto e mensagem.")
                else:
                    env3 = 0
                    for _, row in dce[dce["nome"].isin(sel3)].iterrows():
                        html = f'<div style="font-family:Inter,sans-serif;max-width:560px;margin:0 auto"><div style="background:{NAVY};padding:24px;border-radius:12px 12px 0 0"><h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:28px;border-radius:0 0 12px 12px"><p>Olá, <b>{row["nome"].split()[0]}</b>!</p><h3 style="color:{NAVY}">{ct3}</h3><p style="color:#475569;line-height:1.6">{cc3}</p><a href="https://wa.me/5511952723015" style="background:{GREEN};color:white;padding:12px 28px;border-radius:99px;text-decoration:none;font-weight:600">💬 WhatsApp</a></div></div>'
                        ok_e, err_e = send_email_safe(row["email"], row["nome"], ca3, html)
                    if ok_e: env3 += 1
                    st.success(f"✅ {env3} email(s) enviado(s)!")

# ═══ METAS ═══
    with t4:
        st.markdown("""
        <div style="background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);
            border-radius:10px;padding:12px 16px;margin-bottom:16px">
            <div style="color:#60A5FA;font-size:12px;font-weight:700;margin-bottom:4px">
                🎯 Campanha segmentada por perfil do cliente
            </div>
            <div style="color:rgba(255,255,255,0.55);font-size:11px">
                Selecione o segmento e envie mensagem personalizada para o público certo.
            </div>
        </div>
        """, unsafe_allow_html=True)

        df_seg = load_clientes()
        if df_seg.empty:
            st.info("Nenhum cliente cadastrado.")
        else:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                seg_tipo = st.selectbox("Segmentar por", [
                    "Tipo de Benefício",
                    "Canal de Origem",
                    "Status",
                    "Margem Disponível",
                    "Score de Propensão",
                ])

            # Filtro dinâmico por segmento
            if seg_tipo == "Tipo de Benefício":
                tipos_disp = sorted(df_seg["tipo_beneficio"].dropna().unique().tolist()) if "tipo_beneficio" in df_seg.columns else []
                with col_s2:
                    sel_seg = st.multiselect("Tipo(s)", tipos_disp, default=tipos_disp[:3] if tipos_disp else [])
                df_filtrado = df_seg[df_seg["tipo_beneficio"].isin(sel_seg)] if sel_seg else pd.DataFrame()

            elif seg_tipo == "Canal de Origem":
                canais = sorted(df_seg["canal"].dropna().unique().tolist())
                with col_s2:
                    sel_seg = st.multiselect("Canal(is)", canais, default=canais)
                df_filtrado = df_seg[df_seg["canal"].isin(sel_seg)] if sel_seg else pd.DataFrame()

            elif seg_tipo == "Status":
                statuses = sorted(df_seg["status"].dropna().unique().tolist())
                with col_s2:
                    sel_seg = st.multiselect("Status", statuses, default=statuses)
                df_filtrado = df_seg[df_seg["status"].isin(sel_seg)] if sel_seg else pd.DataFrame()

            elif seg_tipo == "Margem Disponível":
                with col_s2:
                    faixa = st.selectbox("Faixa", ["Acima de R$ 300", "Acima de R$ 500", "Acima de R$ 1.000", "Qualquer margem positiva"])
                faixas = {"Acima de R$ 300": 300, "Acima de R$ 500": 500, "Acima de R$ 1.000": 1000, "Qualquer margem positiva": 1}
                df_filtrado = df_seg[df_seg["margem"] >= faixas[faixa]]

            elif seg_tipo == "Score de Propensão":
                with col_s2:
                    score_min = st.slider("Score mínimo", 0, 100, 70)
                df_filtrado = df_seg[df_seg["score"] >= score_min]

            # Preview do segmento
            dce_seg = df_filtrado[df_filtrado["email"].notna() & (df_filtrado["email"] != "")] if not df_filtrado.empty else pd.DataFrame()

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            c_s1, c_s2, c_s3 = st.columns(3)
            with c_s1: kpi_html("No segmento", len(df_filtrado) if not df_filtrado.empty else 0, "", "navy")
            with c_s2: kpi_html("Com email", len(dce_seg), "podem receber", "green")
            with c_s3:
                margem_media = df_filtrado["margem"].mean() if not df_filtrado.empty else 0
                kpi_html("Margem média", fmt(margem_media), "do segmento", "green" if margem_media > 300 else "yellow")

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            # Preview da lista
            if not df_filtrado.empty:
                with st.expander(f"+ Ver {len(df_filtrado)} cliente(s) do segmento"):
                    for _, r in df_filtrado.head(20).iterrows():
                        tem_email = "✉️" if r.get("email") else "—"
                        st.markdown(
                            f'<div style="padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05);'
                            f'font-size:12px;color:rgba(255,255,255,0.7);display:flex;justify-content:space-between">'
                            f'<span>{r["nome"]}</span>'
                            f'<span style="color:rgba(255,255,255,0.35)">{r.get("tipo_beneficio","")[:30]} {tem_email}</span></div>',
                            unsafe_allow_html=True
                        )

            # Formulário de envio segmentado
            if not dce_seg.empty:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                with st.form("form_seg_email"):
                    assunto_seg = st.text_input("Assunto do email", placeholder="Ex: Oportunidade especial para aposentados por idade")
                    titulo_seg  = st.text_input("Título da mensagem", placeholder="Ex: Seu benefício pode render mais!")
                    corpo_seg   = st.text_area("Corpo da mensagem", height=100,
                        placeholder="Ex: Olá! Como beneficiário de aposentadoria por idade, você tem direito a condições especiais...")

                    if st.form_submit_button(f"🎯 Enviar para {len(dce_seg)} cliente(s) do segmento", use_container_width=True):
                        if not assunto_seg or not corpo_seg:
                            st.error("Preencha assunto e corpo da mensagem.")
                        else:
                            env_seg = 0
                            for _, r in dce_seg.iterrows():
                                html_seg = (
                                    f'<div style="font-family:Inter,sans-serif;max-width:560px;margin:0 auto">'
                                    f'<div style="background:#1B3A6B;padding:24px;border-radius:12px 12px 0 0">'
                                    f'<h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div>'
                                    f'<div style="background:white;padding:28px;border-radius:0 0 12px 12px">'
                                    f'<p>Olá, <b>{r["nome"].split()[0]}</b>!</p>'
                                    f'<h3 style="color:#1B3A6B">{titulo_seg}</h3>'
                                    f'<p style="color:#475569;line-height:1.6">{corpo_seg}</p>'
                                    f'<div style="background:#F0FDF4;border-radius:10px;padding:12px 16px;margin:16px 0;font-size:12px;color:#166534">'
                                    f'Benefício: <b>{r.get("tipo_beneficio","")}</b> · '
                                    f'Margem disponível: <b>{fmt(r.get("margem",0))}</b></div>'
                                    f'<a href="https://wa.me/5511952723015" style="background:#1A7A5E;color:white;'
                                    f'padding:12px 28px;border-radius:99px;text-decoration:none;font-weight:600">'
                                    f'💬 Falar no WhatsApp</a></div></div>'
                                )
                                ok_s, _ = send_email_safe(r["email"], r["nome"], assunto_seg, html_seg)
                                if ok_s: env_seg += 1
                            st.success(f"✅ {env_seg} email(s) enviado(s) para o segmento!")
            else:
                st.warning("Nenhum cliente neste segmento possui email cadastrado.")

elif "Metas" in menu:
    page_header("🎯", "Painel de Metas", "Acompanhe seu progresso mensal")

    c1, c2, c3 = st.columns(3)
    with c1: mc2 = st.number_input("Meta de contratos/mês", min_value=1, value=30, step=5)
    with c2: ml  = st.number_input("Meta de leads/mês", min_value=1, value=50, step=5)
    with c3: mcm = st.number_input("Meta de comissão (R$)", min_value=0.0, value=3000.0, step=500.0)

    dfl2 = load_leads()
    dfc2 = load_contratos()
    lm   = len(dfl2); ctm = len(dfc2)
    com  = dfc2["valor"].sum()*0.03 if not dfc2.empty else 0

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    for lbl, atual, meta, cor2 in [
        ("Contratos Fechados", ctm, mc2, GREEN),
        ("Leads Gerados", lm, ml, NAVY),
        ("Comissão (R$)", com, mcm, YELLOW),
    ]:
        pct3 = min(100, round(atual/meta*100, 1)) if meta > 0 else 0
        vf   = fmt(atual) if "R$" in lbl else str(int(atual))
        mf   = fmt(meta)  if "R$" in lbl else str(int(meta))
        falta = fmt(abs(meta-atual)) if "R$" in lbl else str(int(max(0, meta-atual)))

        st.markdown(f"""
        <div class="meta-bar-wrap">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:13px;font-weight:600;color:{NAVY}">{lbl}</span>
                <span style="font-size:12px;color:#64748B">{vf} / {mf} <span style="color:#94A3B8;font-size:11px">({pct3}%)</span></span>
            </div>
            <div class="meta-bar-track">
                <div class="meta-bar-fill" style="width:{pct3}%;background:{cor2}"></div>
            </div>
            <div style="font-size:11px;color:{'#16A34A' if pct3>=100 else '#94A3B8'}">
                {'🎉 Meta atingida!' if pct3>=100 else f'Faltam {falta} para a meta'}
            </div>
        </div>""", unsafe_allow_html=True)

    if ctm > 0 and mc2 > 0:
        dias_uteis = max(1, 22 - date.today().day)
        ritmo = max(0, (mc2 - ctm) / dias_uteis)
        st.markdown(f"""
        <div style="background:#EFF6FF;border-radius:10px;padding:12px 16px;margin-top:6px;border:1px solid #BFDBFE">
            <span style="font-size:13px;color:{NAVY};font-weight:600">📈 Ritmo necessário: </span>
            <span style="font-size:13px;color:#3B82F6">{ritmo:.1f} contrato(s)/dia nos próximos {dias_uteis} dias úteis</span>
        </div>""", unsafe_allow_html=True)

# ═══ ADMINISTRAÇÃO ═══
elif "Administração" in menu:
    if not is_admin():
        st.error("Acesso restrito ao administrador.")
        st.stop()

    page_header("⚙️", "Painel de Administração", "Gestão de usuários e acessos do sistema")

    # ── KPIs
    if sb:
        try:
            r_us = sb.table("usuarios").select("*").execute()
            total_us = len(r_us.data or [])
            ativos_us = len([u for u in (r_us.data or []) if u.get("ativo")])
        except:
            total_us = ativos_us = 0
    else:
        total_us = ativos_us = 0

    c1, c2, c3 = st.columns(3)
    with c1: kpi_html("Usuários Cadastrados", total_us + 1, "inclui admin", "navy")
    with c2: kpi_html("Usuários Ativos", ativos_us + 1, "", "green")
    with c3: kpi_html("Seu Perfil", "Admin", "acesso total", "green")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Cadastrar novo usuário
    if st.button("＋ Novo Usuário", key="btn_new_user"):
        st.session_state["show_form_user"] = not st.session_state.get("show_form_user", False)

    if st.session_state.get("show_form_user", False):
        with st.form("form_usuario", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nu_nome  = st.text_input("Nome completo")
                nu_login = st.text_input("Login (sem espaços)")
                nu_senha = st.text_input("Senha inicial", type="password")
            with c2:
                nu_perfil = st.selectbox("Perfil de acesso", ["operador", "admin"])
                nu_email  = st.text_input("Email (opcional)")
                nu_obs    = st.text_input("Observação (ex: função)")

            st.markdown(f"""
            <div style="background:rgba(74,222,128,0.08);border-radius:8px;padding:10px 14px;margin:8px 0;font-size:12px;color:rgba(255,255,255,0.6)">
                <b style="color:#4ADE80">Perfil Operador:</b> acessa Clientes, Leads, Simulador e Agenda<br>
                <b style="color:#4ADE80">Perfil Admin:</b> acesso total + gerenciar usuários
            </div>""", unsafe_allow_html=True)

            if st.form_submit_button("✅ Cadastrar Usuário", use_container_width=True):
                if not nu_nome or not nu_login or not nu_senha:
                    st.error("Nome, login e senha são obrigatórios.")
                elif nu_login.lower() == "eduardo":
                    st.error("Login reservado.")
                else:
                    try:
                        sb.table("usuarios").insert({
                            "nome": nu_nome,
                            "login": nu_login.lower().strip(),
                            "senha_hash": hashlib.sha256(nu_senha.encode()).hexdigest(),
                            "perfil": nu_perfil,
                            "email": nu_email,
                            "observacao": nu_obs,
                            "ativo": True
                        }).execute()
                        st.success(f"✅ Usuário {nu_nome} cadastrado com perfil {nu_perfil}!")
                        st.session_state["show_form_user"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    # ── Lista de usuários
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="chart-card"><div class="chart-title">👥 Usuários Cadastrados</div>', unsafe_allow_html=True)

    # Admin fixo
    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;
        padding:10px 14px;background:rgba(74,222,128,0.08);border-radius:9px;margin-bottom:6px;
        border-left:3px solid #1A7A5E">
        <div>
            <span style="color:white;font-weight:700;font-size:13px">Eduardo Lima de Sousa</span>
            <span style="color:rgba(255,255,255,0.4);font-size:11px;margin-left:10px">@eduardo</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
            <span style="background:rgba(74,222,128,0.15);color:#4ADE80;padding:2px 10px;
                border-radius:99px;font-size:10px;font-weight:700">ADMIN</span>
            <span style="background:rgba(74,222,128,0.15);color:#4ADE80;padding:2px 10px;
                border-radius:99px;font-size:10px;font-weight:700">● Ativo</span>
        </div>
    </div>""", unsafe_allow_html=True)

    if sb:
        try:
            r_lista = sb.table("usuarios").select("*").order("created_at", desc=True).execute()
            for u in (r_lista.data or []):
                ativo = u.get("ativo", True)
                cor_status = "#4ADE80" if ativo else "#EF4444"
                label_status = "● Ativo" if ativo else "○ Inativo"
                cor_perfil = "#60A5FA" if u["perfil"] == "admin" else "rgba(255,255,255,0.5)"

                ca, cb = st.columns([3, 1])
                with ca:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:rgba(255,255,255,0.04);border-radius:9px;
                        border-left:3px solid {'#1A7A5E' if ativo else '#374151'}">
                        <div>
                            <span style="color:white;font-weight:600;font-size:13px">{u['nome']}</span>
                            <span style="color:rgba(255,255,255,0.4);font-size:11px;margin-left:10px">@{u['login']}</span>
                            {f'<span style="color:rgba(255,255,255,0.3);font-size:10px;margin-left:8px">{u.get("observacao","")}</span>' if u.get("observacao") else ""}
                        </div>
                        <div style="display:flex;gap:8px;align-items:center">
                            <span style="background:rgba(96,165,250,0.12);color:{cor_perfil};padding:2px 10px;
                                border-radius:99px;font-size:10px;font-weight:700">{u['perfil'].upper()}</span>
                            <span style="color:{cor_status};font-size:11px;font-weight:600">{label_status}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                with cb:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        label_btn = "Desativar" if ativo else "Ativar"
                        if st.button(label_btn, key=f"tog_{u['id']}"):
                            sb.table("usuarios").update({"ativo": not ativo}).eq("id", u["id"]).execute()
                            st.rerun()
                    with col_b:
                        if st.button("Excluir", key=f"del_u_{u['id']}"):
                            sb.table("usuarios").delete().eq("id", u["id"]).execute()
                            st.success(f"Usuário removido.")
                            st.rerun()
        except Exception as e:
            st.error(f"Erro ao carregar usuários: {e}")

    st.markdown('</div>', unsafe_allow_html=True)