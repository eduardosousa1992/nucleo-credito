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

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}

/* ── Fundo geral ── */
.stApp {{
    background: #EEF2F7;
}}
/* ── Área de conteúdo principal ── */
[data-testid="stAppViewContainer"] > .main {{
    background: #EEF2F7;
}}
/* ── Header de marca acima do conteúdo ── */
.brand-topbar {{
    background: linear-gradient(90deg, {NAVY} 0%, #0F2347 100%);
    padding: 12px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    border-radius: 0 0 16px 16px;
    box-shadow: 0 2px 12px rgba(27,58,107,0.2);
}}
.brand-topbar-left {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.brand-topbar-title {{
    color: white;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: -0.3px;
}}
.brand-topbar-sub {{
    color: rgba(255,255,255,0.45);
    font-size: 10px;
    font-style: italic;
}}
.brand-topbar-right {{
    color: rgba(255,255,255,0.6);
    font-size: 12px;
}}

/* ── Esconde elementos nativos desnecessários ── */
header[data-testid="stHeader"] {{ display: none !important; }}
footer {{ display: none !important; }}
#MainMenu {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background: {NAVY} !important;
    min-width: 220px !important;
    max-width: 220px !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}

/* Botão hamburguer nativo - SEMPRE VISÍVEL */
[data-testid="collapsedControl"] {{
    color: white !important;
    background: {NAVY} !important;
    border-radius: 0 8px 8px 0 !important;
    position: fixed !important;
    top: 50% !important;
    left: 0 !important;
    z-index: 9999 !important;
    width: 28px !important;
    height: 48px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.15) !important;
}}
[data-testid="collapsedControl"]:hover {{
    background: {GREEN} !important;
    width: 32px !important;
}}

/* Radio do menu lateral */
[data-testid="stSidebar"] .stRadio > label {{
    display: none !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
    padding: 8px 12px !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.75) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    margin: 0 !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.12) !important;
    color: white !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {{
    background: rgba(255,255,255,0.18) !important;
    color: white !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] .stRadio input[type="radio"] {{
    display: none !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] p {{
    color: inherit !important;
    font-size: 13px !important;
    margin: 0 !important;
}}

/* ── CARDS KPI ── */
.kpi-card {{
    background: white;
    border-radius: 14px;
    padding: 18px 16px 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    border-top: 3px solid {GREEN};
    text-align: center;
    height: 100%;
}}
.kpi-card.navy {{ border-top-color: {NAVY}; }}
.kpi-card.red   {{ border-top-color: {RED}; }}
.kpi-card.yellow {{ border-top-color: {YELLOW}; }}
.kpi-lbl {{
    font-size: 10px;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 700;
    margin-bottom: 6px;
}}
.kpi-val {{
    font-size: 24px;
    font-weight: 800;
    color: {NAVY};
    line-height: 1.1;
}}
.kpi-sub {{
    font-size: 10px;
    color: #CBD5E1;
    margin-top: 4px;
}}

/* ── CHART CARD ── */
.chart-card {{
    background: white;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    margin-bottom: 16px;
}}
.chart-title {{
    font-size: 13px;
    font-weight: 700;
    color: {NAVY};
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #F1F5F9;
    display: flex;
    align-items: center;
    gap: 6px;
}}

/* ── PAGE HEADER ── */
.page-header {{
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    border-left: 4px solid {GREEN};
    display: flex;
    align-items: center;
    gap: 14px;
}}
.page-header-icon {{
    font-size: 28px;
    line-height: 1;
}}
.page-header h2 {{
    color: {NAVY};
    font-size: 18px;
    font-weight: 800;
    margin: 0 0 2px;
    letter-spacing: -0.3px;
}}
.page-header p {{
    color: #94A3B8;
    font-size: 12px;
    margin: 0;
}}

/* ── ALERT BOX ── */
.alert-opp {{
    background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
    border: 1px solid #86EFAC;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
}}
.alert-urgent {{
    background: linear-gradient(135deg, #FFF7ED, #FFEDD5);
    border: 1px solid #FED7AA;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
}}
.alert-row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}}
.alert-name {{
    font-size: 14px;
    font-weight: 700;
    color: {NAVY};
}}
.alert-sub {{
    font-size: 11px;
    color: #64748B;
    margin-top: 2px;
}}
.alert-value {{
    font-size: 22px;
    font-weight: 800;
    color: {GREEN};
    text-align: right;
}}
.alert-value-label {{
    font-size: 10px;
    color: #94A3B8;
    text-align: right;
    margin-bottom: 2px;
}}

/* ── BADGE ── */
.badge {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 99px;
    font-size: 10px;
    font-weight: 700;
    margin-right: 4px;
}}
.b-green  {{ background:#DCFCE7; color:#166534; }}
.b-yellow {{ background:#FEF9C3; color:#854D0E; }}
.b-red    {{ background:#FEE2E2; color:#991B1B; }}
.b-blue   {{ background:#DBEAFE; color:#1E40AF; }}
.b-slate  {{ background:#F1F5F9; color:#475569; }}

/* ── CLIENTE CARD ── */
.cli-card {{
    background: white;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-left: 4px solid #E2E8F0;
}}
.cli-card.opp    {{ border-left-color: {GREEN}; }}
.cli-card.warn   {{ border-left-color: {YELLOW}; }}
.cli-card.danger {{ border-left-color: {RED}; }}

/* ── KANBAN ── */
.kanban-col {{
    background: #F8FAFC;
    border-radius: 12px;
    padding: 12px;
    min-height: 120px;
}}
.kanban-header {{
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.kanban-card {{
    background: white;
    border-radius: 9px;
    padding: 10px 12px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-left: 3px solid #E2E8F0;
}}

/* ── META BAR ── */
.meta-bar-wrap {{
    background: white;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.meta-bar-track {{
    background: #F1F5F9;
    border-radius: 99px;
    height: 10px;
    overflow: hidden;
    margin: 8px 0 4px;
}}
.meta-bar-fill {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.4s ease;
}}

/* ── BOTÕES ── */
.stButton > button {{
    background: {NAVY} !important;
    color: white !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 9px 18px !important;
    transition: all 0.15s !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    background: #152D54 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(27,58,107,0.25) !important;
}}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {{
    border-radius: 9px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}}
.stSelectbox > div > div {{
    border-radius: 9px !important;
    border: 1.5px solid #E2E8F0 !important;
}}

/* ── LOGIN ── */
.login-wrap {{
    max-width: 380px;
    margin: 60px auto 0;
    background: white;
    border-radius: 20px;
    padding: 40px 36px 36px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.10);
    text-align: center;
}}

/* ── HIST CARD ── */
.hist-item {{
    background: #F8FAFC;
    border-radius: 9px;
    padding: 9px 13px;
    margin-bottom: 6px;
    border-left: 3px solid {GREEN};
    font-size: 12px;
}}
.hist-meta {{
    font-size: 10px;
    color: #94A3B8;
    margin-bottom: 3px;
}}

/* ── PROGRESSO ── */
.progress-bar-wrap {{
    background: #F1F5F9;
    border-radius: 99px;
    height: 6px;
    overflow: hidden;
    margin-top: 6px;
}}
.progress-bar-fill {{
    height: 100%;
    border-radius: 99px;
}}
</style>
""", unsafe_allow_html=True)

# ── SECRETS ──────────────────────────────────────────────────────────────────
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
    d = "".join(filter(str.isdigit, c or ""))
    return f"***.{d[3:6]}.{d[6:9]}-**" if len(d) == 11 else "***.***.***-**"

def mask_tel(t):
    d = "".join(filter(str.isdigit, t or ""))
    return f"({d[:2]}) *****-{d[-4:]}" if len(d) >= 8 else "(**)*****-****"

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
    m = row.get("margem", 0)
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
        df["margem"]  = df.apply(lambda r: round(r["beneficio"]*0.4 - r["parcelas"], 2), axis=1)
        df["pct"]     = df.apply(lambda r: min(100, round(r["parcelas"]/(r["beneficio"]*0.4)*100, 1)) if r["beneficio"] > 0 else 0, axis=1)
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

def ins_lead(d):   sb.table("leads").insert(d).execute()
def ins_hist(d):   sb.table("historico").insert(d).execute()
def ins_fu(d):     sb.table("followups").insert(d).execute()
def ins_ct(d):     sb.table("contratos").insert(d).execute()
def upd_lead(id, s): sb.table("leads").update({"status": s}).eq("id", id).execute()
def del_cli(id):
    for t in ["historico","followups","clientes"]:
        sb.table(t).delete().eq("cliente_id" if t != "clientes" else "id", id).execute()
def del_fu(id): sb.table("followups").delete().eq("id", id).execute()

# ── EMAIL ─────────────────────────────────────────────────────────────────────
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
        return True
    except: return False

# ── AUTH ──────────────────────────────────────────────────────────────────────
USERS = {
    "eduardo": {
        "pwd": hashlib.sha256(b"nucleo2026").hexdigest(),
        "name": "Eduardo Lima de Sousa"
    }
}

def check_pwd(u, p):
    usr = USERS.get(u.lower())
    if not usr: return False
    return hmac.compare_digest(usr["pwd"], hashlib.sha256(p.encode()).hexdigest())

# ── HELPERS UI ────────────────────────────────────────────────────────────────
def fmt(v):
    return f"R$ {abs(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")

def kpi_html(label, value, sub="", color="green"):
    # Uses st.metric natively - no HTML - no </div> issues
    st.metric(label=label, value=value, help=sub if sub else None)

def badge(text, color):
    cls = {"green":"b-green","yellow":"b-yellow","red":"b-red","blue":"b-blue","slate":"b-slate"}.get(color,"b-slate")
    return f'<span class="badge {cls}">{text}</span>'

def plotly_theme():
    return dict(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=10, t=8, b=0),
        font=dict(family="Inter, sans-serif", size=11),
        xaxis=dict(showgrid=False, showline=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", showline=False),
    )

def page_header(icon, title, subtitle):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-icon">{icon}</div>
        <div>
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </div>
    </div>""", unsafe_allow_html=True)

# ── LOGIN SCREEN ──────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""<style>
        [data-testid="stSidebar"]{display:none!important}
        [data-testid="collapsedControl"]{display:none!important}
        .stApp{background:linear-gradient(160deg,#1B3A6B 0%,#0D1F3C 55%,#0F4A38 100%)!important}
        [data-testid="stAppViewContainer"]>.main{background:transparent!important}
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
            st.session_state.logged_in = True
            st.session_state.username  = username
            st.session_state.uname     = USERS[username.lower()]["name"]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown(f"""
    <div style="padding:24px 16px 16px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:8px">
        <div style="display:flex;align-items:center;gap:10px">
            <svg width="32" height="32" viewBox="0 0 64 64" fill="none">
                <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none"/>
                <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(60 32 32)"/>
                <ellipse cx="32" cy="32" rx="27" ry="10.5" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(120 32 32)"/>
                <circle cx="32" cy="32" r="5.5" fill="{GREEN}"/>
                <circle cx="32" cy="32" r="2.5" fill="white"/>
            </svg>
            <div>
                <div style="color:white;font-size:15px;font-weight:800;letter-spacing:-0.3px">Núcleo Crédito</div>
                <div style="color:rgba(255,255,255,0.4);font-size:9px;font-style:italic">No centro da sua vida financeira.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Menu navegação
    menu = st.radio(
        "Navegação",
        options=[
            "📊  Dashboard",
            "👥  Clientes",
            "📋  Leads",
            "📄  Contratos",
            "🧮  Simulador",
            "🔔  Alertas",
            "📅  Agenda",
            "📧  Email Marketing",
            "🎯  Metas",
        ],
        label_visibility="collapsed"
    )

    # Rodapé da sidebar
    st.markdown(f"""
    <div style="position:fixed;bottom:0;left:0;width:220px;padding:16px;border-top:1px solid rgba(255,255,255,0.08)">
        <div style="display:flex;align-items:center;gap:8px">
            <div style="width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,0.15);display:flex;align-items:center;justify-content:center;font-size:12px">
                {st.session_state.uname[0]}
            </div>
            <div>
                <div style="color:white;font-size:12px;font-weight:600">{st.session_state.uname.split()[0]}</div>
                <div style="color:rgba(255,255,255,0.4);font-size:10px">Admin</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    if st.button("🚪 Sair", key="logout"):
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

    with st.expander("➕ Cadastrar Novo Cliente"):
        with st.form("form_cli", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nome  = st.text_input("Nome Completo *")
                cpf   = st.text_input("CPF (será criptografado)")
                tel   = st.text_input("Telefone (será criptografado)")
                email = st.text_input("Email (para mailing)")
                dn    = st.date_input("Data Nascimento", value=date(1960,1,1),
                                      min_value=date(1930,1,1), max_value=date(2005,1,1))
            with c2:
                ben    = st.number_input("Benefício / Salário (R$) *", min_value=0.0, step=50.0)
                par    = st.number_input("Parcelas Ativas (R$)", min_value=0.0, step=50.0)
                canal  = st.selectbox("Canal", ["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"])
                status = st.selectbox("Status", ["Lead Quente","Em análise","Ativo"])
                int_   = st.selectbox("Interesse", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor"])
            obs = st.text_area("Observações", height=60)

            if st.form_submit_button("✅ Cadastrar Cliente", use_container_width=True):
                if not nome or not ben:
                    st.error("Nome e Benefício são obrigatórios.")
                else:
                    ins_cli({"nome":nome,"cpf":cpf,"telefone":tel,"email":email,
                        "data_nasc":str(dn),"beneficio":float(ben),"parcelas":float(par),
                        "canal":canal,"status":status,"interesse":int_,"observacoes":obs})
                    st.success(f"✅ {nome} cadastrado!")
                    st.rerun()

    df = load_clientes()
    if not df.empty:
        cf1, cf2, cf3 = st.columns(3)
        with cf1: fs = st.multiselect("Status", df["status"].unique().tolist(), default=df["status"].unique().tolist())
        with cf2: fc = st.multiselect("Canal",  df["canal"].unique().tolist(),  default=df["canal"].unique().tolist())
        with cf3: oo = st.checkbox("Apenas oportunidades (margem > R$ 300)")

        dff = df[df["status"].isin(fs) & df["canal"].isin(fc)]
        if oo: dff = dff[dff["margem"] > 300]
        dff = dff.sort_values("score", ascending=False)

        st.markdown(f"<p style='color:#94A3B8;font-size:12px;margin:8px 0 12px'><b>{len(dff)}</b> cliente(s)</p>", unsafe_allow_html=True)

        for _, row in dff.iterrows():
            m = row["margem"]
            cc = "opp" if m > 300 else "danger" if m <= 0 else "warn"
            bm = badge("Oportunidade","green") if m > 300 else badge("Sem margem","red") if m <= 0 else badge("Margem baixa","yellow")
            bs = badge(row["status"], "blue")

            with st.expander(f"{'🔥' if row['score']>=75 else '⚡' if row['score']>=55 else '●'} {row['nome']}  ·  Score {row['score']}%  ·  {fmt(m)}"):
                ca, cb = st.columns([2, 1])

                with ca:
                    st.markdown(f"""
                    <div class="cli-card {cc}">
                        <div style="font-size:14px;font-weight:700;color:{NAVY}">{row['nome']}</div>
                        <div style="font-size:11px;color:#64748B;margin:3px 0 8px">{row['tel_d']} &nbsp;·&nbsp; {row['canal']} &nbsp;·&nbsp; {row['interesse']}</div>
                        <div>{bm} {bs} <span class="badge b-slate">Score {row['score']}%</span></div>
                    </div>""", unsafe_allow_html=True)

                    g1, g2, g3, g4 = st.columns(4)
                    for gcol, lbl, val, cor in [
                        (g1, "Benefício",    fmt(row['beneficio']), NAVY),
                        (g2, "Margem disp.", fmt(m), GREEN if m>300 else RED if m<=0 else YELLOW),
                        (g3, "Próx. INSS",   row['prox'].strftime('%d/%m/%Y') if row['prox'] else "—", NAVY),
                        (g4, "Comprometido", f"{row['pct']:.0f}%", NAVY),
                    ]:
                        with gcol:
                            st.markdown(f"""
                            <div style="background:#F8FAFC;border-radius:9px;padding:8px 10px;text-align:center">
                                <div style="font-size:9px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:.05em">{lbl}</div>
                                <div style="font-size:13px;font-weight:700;color:{cor};margin-top:2px">{val}</div>
                            </div>""", unsafe_allow_html=True)

                    # Barra de comprometimento
                    pct_c = row['pct']
                    bar_color = GREEN if pct_c < 60 else YELLOW if pct_c < 90 else RED
                    st.markdown(f"""
                    <div style="margin-top:10px">
                        <div class="progress-bar-wrap">
                            <div class="progress-bar-fill" style="width:{pct_c}%;background:{bar_color}"></div>
                        </div>
                        <div style="font-size:10px;color:#94A3B8;margin-top:3px">Margem comprometida: {pct_c:.0f}%</div>
                    </div>""", unsafe_allow_html=True)

                with cb:
                    st.markdown("**Registrar contato**")
                    with st.form(f"hist_{row['id']}"):
                        tp  = st.selectbox("Tipo", ["Ligação","WhatsApp","Visita","Email","Outro"], key=f"tp_{row['id']}")
                        nt  = st.text_area("Anotação", height=60, key=f"nt_{row['id']}")
                        if st.form_submit_button("📝 Salvar", use_container_width=True):
                            ins_hist({"cliente_id":row["id"],"tipo":tp,"nota":nt,"data":str(date.today())})
                            st.success("✅ Registrado!")
                            st.rerun()

                    with st.form(f"fu_{row['id']}"):
                        dfu = st.date_input("Agendar follow-up", value=date.today()+timedelta(days=1), key=f"dfu_{row['id']}")
                        mfu = st.text_input("Motivo", key=f"mfu_{row['id']}")
                        if st.form_submit_button("📅 Agendar", use_container_width=True):
                            ins_fu({"cliente_id":row["id"],"data_followup":str(dfu),"motivo":mfu})
                            st.success("✅ Agendado!")

                    if row.get("email"):
                        if st.button(f"📧 Enviar INSS", key=f"em_{row['id']}"):
                            pg_d, dias_d = prox_pg(row["cpf_raw"])
                            html = f'<div style="font-family:Inter,sans-serif;max-width:500px;margin:0 auto"><div style="background:{NAVY};padding:24px;border-radius:12px 12px 0 0"><h2 style="color:white;margin:0;font-size:18px">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:24px;border-radius:0 0 12px 12px"><p style="font-size:15px">Olá, <b>{row["nome"].split()[0]}</b>!</p><p>Seu próximo pagamento INSS: <b style="color:{GREEN};font-size:18px">{pg_d.strftime("%d/%m/%Y") if pg_d else "Em breve"}</b></p><a href="https://wa.me/5511952723015" style="display:inline-block;background:{GREEN};color:white;padding:10px 24px;border-radius:99px;text-decoration:none;font-weight:600">💬 Falar no WhatsApp</a></div></div>'
                            if send_email(row["email"], row["nome"], "Seu INSS — Núcleo Crédito", html):
                                st.success("✅ Enviado!")
                            else:
                                st.error("Erro no envio.")

                    if st.button(f"🗑 Remover cliente", key=f"del_{row['id']}"):
                        del_cli(row["id"])
                        st.rerun()

                # Histórico
                hist = load_hist(row["id"])
                if not hist.empty:
                    st.markdown("**Histórico de atendimento**")
                    for _, h in hist.iterrows():
                        st.markdown(f"""
                        <div class="hist-item">
                            <div class="hist-meta">{h['data']} &nbsp;·&nbsp; {h['tipo']}</div>
                            {h['nota']}
                        </div>""", unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado ainda.")

# ═══ LEADS ═══
elif "Leads" in menu:
    page_header("📋", "Pipeline de Leads", "Funil de vendas visual — Kanban")

    with st.expander("➕ Novo Lead"):
        with st.form("form_lead", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                ln = st.text_input("Nome")
                lt = st.text_input("Telefone")
                lc = st.selectbox("Canal", ["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"])
            with c2:
                li = st.selectbox("Interesse", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado"])
                lb = st.number_input("Benefício (R$)", min_value=0.0, step=50.0)
                ls = st.selectbox("Status", ["Novo","Em negociação","Convertido","Perdido"])
            lo = st.text_area("Observações", height=50)
            if st.form_submit_button("✅ Registrar Lead", use_container_width=True):
                ins_lead({"nome":ln,"telefone":lt,"canal":lc,"interesse":li,"beneficio":float(lb),"status":ls,"observacoes":lo})
                st.success("Lead registrado!")
                st.rerun()

    dfl = load_leads()
    if not dfl.empty:
        STATUS  = ["Novo","Em negociação","Convertido","Perdido"]
        ICONES  = {"Novo":"🔵","Em negociação":"🟡","Convertido":"✅","Perdido":"❌"}
        CORES_K = {"Novo":NAVY,"Em negociação":YELLOW,"Convertido":GREEN,"Perdido":RED}

        cols = st.columns(4)
        for idx, s in enumerate(STATUS):
            grupo = dfl[dfl["status"] == s]
            with cols[idx]:
                st.markdown(f"""
                <div class="kanban-col">
                    <div class="kanban-header">
                        <span style="color:{CORES_K[s]}">{ICONES[s]} {s}</span>
                        <span style="background:#E2E8F0;color:#64748B;padding:1px 7px;border-radius:99px;font-size:10px">{len(grupo)}</span>
                    </div>
                """, unsafe_allow_html=True)

                for _, row in grupo.iterrows():
                    st.markdown(f"""
                    <div class="kanban-card" style="border-left-color:{CORES_K[s]}">
                        <div style="font-size:12px;font-weight:600;color:{NAVY}">{row['nome']}</div>
                        <div style="font-size:10px;color:#94A3B8;margin-top:2px">{row['canal']} · {row['interesse']}</div>
                        {"<div style='font-size:11px;color:"+GREEN+";font-weight:600;margin-top:4px'>"+fmt(row['beneficio'])+"</div>" if row['beneficio'] else ""}
                    </div>""", unsafe_allow_html=True)

                    ns = st.selectbox(
                        "Mover para",
                        STATUS,
                        index=STATUS.index(s),
                        key=f"ls_{row['id']}",
                        label_visibility="collapsed"
                    )
                    if ns != s:
                        upd_lead(row["id"], ns)
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum lead registrado.")

# ═══ CONTRATOS ═══
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

    with st.expander("➕ Novo Contrato"):
        if df_cli.empty:
            st.warning("Cadastre um cliente primeiro.")
        else:
            with st.form("form_ct", clear_on_submit=True):
                cm  = {r["nome"]: r["id"] for _, r in df_cli.iterrows()}
                c1, c2 = st.columns(2)
                with c1:
                    cs  = st.selectbox("Cliente", list(cm.keys()))
                    bco = st.selectbox("Banco", ["Banco BMG","Banco Safra","Banco PAN","Caixa","BRB","Facta","Itaú Consig."])
                    val = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
                with c2:
                    pt  = st.number_input("Parcelas", min_value=1, max_value=84, value=36, step=1)
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
        st.dataframe(
            dfc[["cliente_nome","banco","valor","parcelas_total","parcela","comissao","data_inicio"]].rename(columns={
                "cliente_nome":"Cliente","banco":"Banco","valor":"Valor (R$)",
                "parcelas_total":"Parcelas","parcela":"Parcela/mês","comissao":"Comissão","data_inicio":"Início"
            }),
            use_container_width=True, hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

# ═══ SIMULADOR ═══
elif "Simulador" in menu:
    page_header("🧮", "Simulador de Crédito", "Calcule margem, simule propostas e compare portabilidade")

    tab1, tab2 = st.tabs(["💳 Simulação de Crédito", "🔄 Calculadora de Portabilidade"])

    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown("#### Dados do Cliente")
            ben2 = st.number_input("Benefício (R$)", min_value=0.0, value=1412.0, step=50.0)
            pa2  = st.number_input("Parcelas Ativas (R$)", min_value=0.0, value=0.0, step=50.0)
            mc = ben2*0.4; md = max(0, mc-pa2)
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
            prazo = st.select_slider("Prazo", options=[12,24,36,48,60,72,84], value=36)
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
            pzs = [12,24,36,48,60,72,84]; r2 = taxa3/100
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
            prn = st.number_input("Novo prazo (meses)", min_value=1, max_value=84, value=48, key="pprn")

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
elif "Alertas" in menu:
    page_header("🔔", "Alertas de Oportunidade", "Radar inteligente por score de propensão")

    df = load_clientes()
    if df.empty:
        st.info("Nenhum cliente cadastrado ainda.")
        st.stop()

    opp = df[df["margem"]>300].sort_values("score", ascending=False)
    bx  = df[(df["margem"]>0)&(df["margem"]<=300)].sort_values("score", ascending=False)
    sm  = df[df["margem"]<=0]
    ph  = df[df["dias"].notna() & (df["dias"].astype(float)<=2)]

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_html("Prioridade Alta", len(opp), "margem>R$300", "green")
    with c2: kpi_html("Atenção",         len(bx),  "margem baixa", "yellow")
    with c3: kpi_html("Sem Margem",      len(sm),  "portabilidade","red")
    with c4: kpi_html("INSS Hoje/Amanhã",len(ph),  "urgente","yellow" if len(ph)>0 else "navy")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if len(ph) > 0:
        st.markdown(f"<div style='font-size:13px;font-weight:700;color:{RED};margin-bottom:10px'>🚨 INSS Cai Hoje ou Amanhã — Contatar Agora</div>", unsafe_allow_html=True)
        for _, row in ph.iterrows():
            st.markdown(f"""
            <div class="alert-urgent">
                <div class="alert-row">
                    <div>
                        <div class="alert-name">{row['nome']}</div>
                        <div class="alert-sub">{row['tel_d']} · {row['interesse']} · Score {row['score']}%</div>
                        <div style="margin-top:6px">{badge("🚨 URGENTE","red")} {badge(row['status'],"blue")}</div>
                    </div>
                    <div>
                        <div class="alert-value-label">INSS em</div>
                        <div style="font-size:26px;font-weight:800;color:{RED}">{int(row['dias'])} dia(s)</div>
                        <div style="font-size:11px;color:#94A3B8">{row['prox'].strftime('%d/%m') if row['prox'] else ''}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    if len(opp) > 0:
        st.markdown(f"<div style='font-size:13px;font-weight:700;color:{GREEN};margin:14px 0 10px'>🟢 Contatar Esta Semana — {len(opp)} cliente(s)</div>", unsafe_allow_html=True)
        for _, row in opp.iterrows():
            high = row["score"] >= 75
            st.markdown(f"""
            <div class="alert-{'urgent' if high else 'opp'}">
                <div class="alert-row">
                    <div>
                        <div class="alert-name">{row['nome']}</div>
                        <div class="alert-sub">{row['tel_d']} · {row['interesse']} · {row['canal']}</div>
                        <div style="margin-top:6px">
                            {badge("🔥 Máxima","yellow") if high else badge("Oportunidade","green")}
                            {badge(f"Score {row['score']}%","slate")}
                            {badge(row['status'],"blue")}
                        </div>
                    </div>
                    <div style="text-align:right">
                        <div class="alert-value-label">Margem disponível</div>
                        <div class="alert-value">{fmt(row['margem'])}</div>
                        <div style="font-size:11px;color:#94A3B8">Benefício: {fmt(row['beneficio'])}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    if len(bx) > 0:
        st.markdown(f"<div style='font-size:13px;font-weight:700;color:{YELLOW};margin:14px 0 10px'>🟡 Margem Baixa — {len(bx)} cliente(s)</div>", unsafe_allow_html=True)
        for _, row in bx.iterrows():
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:10px 14px;margin-bottom:6px;
                border-left:3px solid {YELLOW};box-shadow:0 1px 3px rgba(0,0,0,0.05);
                display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span style="font-weight:600;color:{NAVY}">{row['nome']}</span>
                    <span style="font-size:11px;color:#94A3B8;margin-left:8px">{row['tel_d']}</span>
                </div>
                <span style="font-weight:600;color:{YELLOW}">{fmt(row['margem'])} disponível</span>
            </div>""", unsafe_allow_html=True)

    if len(sm) > 0:
        st.markdown(f"<div style='font-size:13px;font-weight:700;color:{RED};margin:14px 0 10px'>🔴 Sem Margem — Indicar Portabilidade — {len(sm)}</div>", unsafe_allow_html=True)
        for _, row in sm.iterrows():
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:10px 14px;margin-bottom:6px;
                border-left:3px solid {RED};box-shadow:0 1px 3px rgba(0,0,0,0.05);
                display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:600;color:{NAVY}">{row['nome']}</span>
                <span style="font-size:11px;color:{RED}">Verificar portabilidade</span>
            </div>""", unsafe_allow_html=True)

# ═══ AGENDA ═══
elif "Agenda" in menu:
    page_header("📅", "Agenda de Follow-ups", "Seus compromissos e lembretes de contato")

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

    df = load_clientes()
    dce = df[df["email"].notna() & (df["email"] != "")] if not df.empty else pd.DataFrame()

    c1, c2, c3 = st.columns(3)
    with c1: kpi_html("Com Email",   len(dce),  "",             "navy")
    with c2: kpi_html("Envios/Dia",  "300",     "plano gratuito","green")
    with c3: kpi_html("Custo Mensal","R$ 0,00", "Brevo free",   "green")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📅 Calendário INSS", "💡 Dica Financeira", "📣 Campanha Livre"])

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
                    if send_email(row["email"], row["nome"], "Seu INSS — Núcleo Crédito", html): env += 1
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
                    if send_email(row["email"], row["nome"], f"💡 {ds} — Núcleo Crédito", html): env2 += 1
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
                        if send_email(row["email"], row["nome"], ca3, html): env3 += 1
                    st.success(f"✅ {env3} email(s) enviado(s)!")

# ═══ METAS ═══
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