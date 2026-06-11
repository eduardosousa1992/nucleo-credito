import streamlit as st
import os, hashlib, hmac, json
from datetime import date, datetime, timedelta
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cryptography.fernet import Fernet
import base64
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# ══════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO CORE DA PÁGINA (Layout Executivo de Alta Performance)
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Refinanciamento & Portabilidade",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY   = "#1B3A6B"
GREEN  = "#1A7A5E"
RED    = "#C0392B"
YELLOW = "#F5A623"
WHITE  = "#FFFFFF"
LIGHT  = "#F0F4F8"

# ══════════════════════════════════════════════════════════════════════════
# INJEÇÃO DE CSS EXCLUSIVO (Alto Contraste, Fontes Escuras e Grid Limpo)
# ══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
* {{ font-family: 'Montserrat', sans-serif !important; }}
.main {{ background: #F8FAFC; padding-top: 15px !important; }}

/* Customização Premium e Minimalista da Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {NAVY} 0%, #0F2347 100%) !important;
    box-shadow: 4px 0 15px rgba(0,0,0,0.1) !important;
}}
[data-testid="stSidebar"] * {{ color: white !important; }}

/* Alinhamento dos Botões de Navegação Verticais */
div.sidebar-nav-container button {{
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.7) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    border-radius: 8px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    margin-bottom: 5px !important;
}}
div.sidebar-nav-container button:hover {{
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    padding-left: 24px !important;
}}

.active-menu-btn button {{
    background: {GREEN} !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(26,122,94,0.2) !important;
}}

/* Blocos de Conteúdo e Elementos de Formulário (Garantia de Alto Contraste) */
div.content-block {{
    background-color: white !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    margin-bottom: 16px !important;
}}

/* Correção de Legibilidade: Garante que os rótulos de input fiquem sempre visíveis */
label[data-testid="stWidgetLabel"] p {{
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}}

.page-header {{ background: white; border-radius: 14px; padding: 18px 24px; margin-bottom: 20px; border-left: 4px solid {GREEN}; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
.page-header h2 {{ color: {NAVY}; font-size: 20px; font-weight: 800; margin: 0 0 4px; }}
.page-header p {{ color: #64748B; font-size: 13px; margin: 0; }}

.kpi {{ background: white; border-radius: 12px; padding: 16px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border-top: 3px solid {GREEN}; text-align: center; }}
.kpi.n {{ border-top-color: {NAVY}; }}
.kpi.r {{ border-top-color: {RED}; }}
.kpi.y {{ border-top-color: {YELLOW}; }}
.kpi-lbl {{ font-size: 10px; color: #64748B; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; margin-bottom: 6px; }}
.kpi-val {{ font-size: 24px; font-weight: 800; color: {NAVY}; line-height: 1; }}
.kpi-sub {{ font-size: 10px; color: #94A3B8; margin-top: 4px; }}

.chart-card {{ background: white; border-radius: 14px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 16px; }}
.ct {{ font-size: 13px; font-weight: 700; color: {NAVY}; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid #F1F5F9; }}

.badge {{ display: inline-block; padding: 3px 10px; border-radius: 99px; font-size: 10px; font-weight: 700; margin-right: 4px; }}
.bg {{ background: #E2F0D9; color: #1E4620; }}
.by {{ background: #FEF3C7; color: #78350F; }}
.br {{ background: #FEE2E2; color: #991B1B; }}
.bb {{ background: #E0F2FE; color: #075985; }}
.bn {{ background: #F1F5F9; color: {NAVY}; }}

.login-wrap {{ max-width: 360px; margin: 100px auto; background: white; border-radius: 18px; padding: 36px 32px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); text-align: center; }}
</style>
""", unsafe_allow_html=True)

# ── SECRETS ────────────────────────────────────────────────────────────────
def gs(key, default=""):
    try:
        v = st.secrets.get(key)
        if v: return str(v)
    except: pass
    return os.environ.get(key, default)

SUPABASE_URL  = gs("SUPABASE_URL", "https://vvroaokekxbttapefspw.supabase.co")
SUPABASE_KEY  = gs("SUPABASE_KEY", "sb_publishable_OnL6QmmZGnIAGh5IB5TFXQ_tsVn_qK4")
BREVO_KEY     = gs("BREVO_API_KEY", "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")
SENDER_EMAIL  = gs("SENDER_EMAIL", "nucleocastelo.credito@gmail.com")
SENDER_NAME   = gs("SENDER_NAME",  "Consultoria")

# ── SUPABASE ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_sb():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Conexão falhou: {e}")
        return None

sb = get_sb()

# ── CRIPTO ──────────────────────────────────────────────────────────────────
def _f():
    k = gs("ENCRYPT_KEY", "")
    if k:
        return Fernet(k.encode())
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(b"nucleo2026").digest()))

def enc(t):
    if not t: return ""
    try: return _f().encrypt(str(t).encode()).decode()
    except: return t

def dec(t):
    if not t: return ""
    try: return _f().decrypt(str(t).encode()).decode()
    except: return t

def mask_cpf(c):
    d = "".join(filter(str.isdigit, c or ""))
    return f"***.{d[3:6]}.{d[6:9]}-**" if len(d) == 11 else "***.***.***-**"

def mask_tel(t):
    d = "".join(filter(str.isdigit, t or ""))
    return f"({d[:2]}) *****-{d[-4:]}" if len(d) >= 8 else "(**)*****-****"

# ── INSS 2026 ───────────────────────────────────────────────────────────────
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
        u = int(d[-1])
        hoje = date.today()
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

# ── SCORE ───────────────────────────────────────────────────────────────────
def score(row):
    s = 0
    m = row.get("margem", 0)
    if m > 600: s += 40
    elif m > 300: s += 30
    elif m > 100: s += 15
    s += {"Ativo": 20, "Lead Quente": 25, "Em análise": 15}.get(row.get("status", ""), 0)
    s += {"Indicação": 20, "WhatsApp": 15, "Rádio": 12, "Panfletagem": 10, "Google": 12, "Instagram": 8}.get(row.get("canal", ""), 5)
    _, dias = prox_pg(row.get("cpf_raw", ""))
    if dias is not None:
        if 0 <= dias <= 2: s += 15
        elif 3 <= dias <= 5: s += 10
    return min(s, 100)

# ── EMAIL ───────────────────────────────────────────────────────────────────
def send_email(to_email, to_name, subject, html):
    try:
        cfg = sib_api_v3_sdk.Configuration()
        cfg.api_key["api-key"] = BREVO_KEY
        api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(cfg))
        api.send_transac_email(sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email, "name": to_name}],
            sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
            subject=subject, html_content=html))
        return True
    except: return False

# ── DB ──────────────────────────────────────────────────────────────────────
def load_clientes():
    if not sb: return pd.DataFrame()
    try:
        r = sb.table("clientes").select("*").order("created_at", desc=True).execute()
        if not r.data: return pd.DataFrame()
        df = pd.DataFrame(r.data)
        df["cpf_raw"] = df["cpf"].apply(lambda x: dec(x) if x else "")
        df["tel_raw"] = df["telefone"].apply(lambda x: dec(x) if x else "")
        df["cpf_d"] = df["cpf_raw"].apply(mask_cpf)
        df["tel_d"] = df["tel_raw"].apply(mask_tel)
        df["margem"] = df.apply(lambda r: round(r["beneficio"] * 0.4 - r["parcelas"], 2), axis=1)
        df["pct"] = df.apply(lambda r: min(100, round(r["parcelas"] / (r["beneficio"] * 0.4) * 100, 1)) if r["beneficio"] > 0 else 0, axis=1)
        df["score"] = df.apply(score, axis=1)
        df["prox"], df["dias"] = zip(*df.apply(lambda r: prox_pg(r["cpf_raw"]), axis=1))
        return df
    except Exception as e:
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
        r = sb.table("contracts" if "contracts" in globals() else "contratos").select("*, clientes(nome)").order("created_at", desc=True).execute()
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
    return sb.table("clientes").insert(d).execute()

def ins_lead(d): return sb.table("leads").insert(d).execute()
def ins_hist(d): return sb.table("historico").insert(d).execute()
def ins_fu(d):   return sb.table("followups").insert(d).execute()
def ins_ct(d):   return sb.table("contratos").insert(d).execute()
def upd_lead(id, s): return sb.table("leads").update({"status": s}).eq("id", id).execute()
def del_cli(id):
    sb.table("historico").delete().eq("cliente_id", id).execute()
    sb.table("followups").delete().eq("cliente_id", id).execute()
    sb.table("clientes").delete().eq("id", id).execute()
def del_fu(id): sb.table("followups").delete().eq("id", id).execute()

# ── AUTH ────────────────────────────────────────────────────────────────────
USERS = {"eduardo": {"pwd": hashlib.sha256(b"nucleo2026").hexdigest(), "name": "Eduardo Lima de Sousa"}}

def chk(u, p):
    usr = USERS.get(u.lower())
    if not usr: return False
    return hmac.compare_digest(usr["pwd"], hashlib.sha256(p.encode()).hexdigest())

# ── HELPERS ─────────────────────────────────────────────────────────────────
def fmt(v): return f"R$ {abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def kpi(l, v, s="", c="g"):
    cc = {"n": "n", "r": "r", "y": "y"}.get(c, "")
    return f'<div class="kpi {cc}"><div class="kpi-lbl">{l}</div><div class="kpi-val">{v}</div>{"<div class=kpi-sub>" + s + "</div>" if s else ""}</div>'
def badge(t, c):
    cl = {"g": "bg", "y": "by", "r": "br", "b": "bb", "n": "bn"}.get(c, "bb")
    return f'<span class="badge {cl}">{t}</span>'
def plt_def(): return dict(plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0, r=10, t=8, b=0), font=dict(family="Montserrat"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F1F5F9"))

# ── SESSION ─────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ── LOGIN BLINDADO ───────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"""
        <div class="login-wrap">
          <svg width="56" height="56" viewBox="0 0 64 64" fill="none">
            <ellipse cx="32" cy="32" rx="28" ry="11" stroke="{GREEN}" stroke-width="1.8" fill="none"/>
            <ellipse cx="32" cy="32" rx="28" ry="11" stroke="{GREEN}" stroke-width="1.8" fill="none" transform="rotate(60 32 32)"/>
            <ellipse cx="32" cy="32" rx="28" ry="11" stroke="{GREEN}" stroke-width="1.8" fill="none" transform="rotate(120 32 32)"/>
            <circle cx="32" cy="32" r="5" fill="{GREEN}"/><circle cx="32" cy="32" r="2" fill="white"/>
          </svg>
          <div style="font-size:22px;font-weight:800;color:{NAVY};margin:8px 0 2px">Núcleo <span style="color:{GREEN}">Crédito</span></div>
          <p style="color:#999;font-size:11px;font-style:italic;margin-bottom:24px">No centro da sua vida financeira.</p>
        </div>""", unsafe_allow_html=True)
        with st.form("login"):
            st.markdown("#### Acesse o sistema")
            u = st.text_input("Usuário", placeholder="usuário")
            p = st.text_input("Senha", type="password", placeholder="••••••••")
            if st.form_submit_button("Entrar", use_container_width=True):
                user_clean = u.strip().lower()
                if chk(user_clean, p):
                    st.session_state.logged_in = True
                    st.session_state.username = user_clean
                    st.session_state.uname = USERS[user_clean]["name"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        st.markdown(f"<p style='text-align:center;font-size:10px;color:#ccc;margin-top:10px'>Dados criptografados · LGPD</p>", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# ARQUITETURA DO MENU LATERAL PREMIUM NATIVO
# ══════════════════════════════════════════════════════════════════════════
PAGES = ["Dashboard", "Clientes", "Leads", "Contratos", "Simulador", "Alertas", "Agenda", "Email Marketing", "Metas"]

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 10px 0 20px 0;">
      <svg width="40" height="40" viewBox="0 0 64 64" fill="none">
        <ellipse cx="32" cy="32" rx="26" ry="10" stroke="{GREEN}" stroke-width="2" fill="none"/>
        <ellipse cx="32" cy="32" rx="26" ry="10" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(60 32 32)"/>
        <ellipse cx="32" cy="32" rx="26" ry="10" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(120 32 32)"/>
        <circle cx="32" cy="32" r="5" fill="{GREEN}"/><circle cx="32" cy="32" r="2.5" fill="white"/>
      </svg>
      <div style="font-size:18px; font-weight:800; color:white; margin-top:8px;">NÚCLEO CRÉDITO</div>
      <div style="font-size:10px; color:rgba(255,255,255,0.5); font-style:italic;">Consultoria Operacional</div>
    </div>
    <hr style="border-color: rgba(255,255,255,0.1); margin: 0 0 16px 0;">
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-nav-container">', unsafe_allow_html=True)
    for page_name in PAGES:
        is_selected = st.session_state.page == page_name
        container_class = "active-menu-btn" if is_selected else "normal-menu-btn"
        
        with st.container():
            st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
            if st.button(f" {page_name}", key=f"side_nav_{page_name}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    hr_nome = st.session_state.uname.split()[0]
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.06); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 12px;">
      <div style="font-size: 11px; color: rgba(255,255,255,0.5); font-weight: 700; text-transform: uppercase;">Operador Ativo</div>
      <div style="font-size: 14px; font-weight: 600; color: white; margin-top: 2px;">👤 {hr_nome}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sair do Sistema", key="side_logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.caption(f"v2.5 Premium · {date.today().strftime('%d/%m/%Y')}")

qp = st.query_params
if "page" in qp and qp["page"] in PAGES:
    st.session_state.page = qp["page"]

pg = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════
# CAMADA DE APRESENTAÇÃO PREMIUM (CLEAN LAYOUT)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ═══ DASHBOARD ═══
if pg == "Dashboard":
    st.markdown('<div class="page-header"><h2>📊 Dashboard de Performance</h2><p>Visão geral da operação em tempo real</p></div>', unsafe_allow_html=True)
    df = load_clientes(); dfl = load_leads(); dfc = load_contratos(); dfa = load_fu()

    tc = len(df); at = len(df[df["status"] == "Ativo"]) if not df.empty else 0
    mt = df["margem"].clip(lower=0).sum() if not df.empty else 0
    op = len(df[df["margem"] > 300]) if not df.empty else 0
    tl = len(dfl); cv = len(dfl[dfl["status"] == "Convertido"]) if not dfl.empty else 0
    tx = round(cv / tl * 100, 1) if tl > 0 else 0
    car = dfc["valor"].sum() if not dfc.empty else 0
    fh = 0
    if not dfa.empty:
        dfa["data_followup"] = pd.to_datetime(dfa["data_followup"]).dt.date
        fh = len(dfa[dfa["data_followup"] == date.today()])

    cols = st.columns(8)
    for col, (l, v, s, c) in zip(cols, [
        ("Clientes", tc, "", "n"), ("Ativos", at, "", "g"),
        ("Margem Total", fmt(mt), "disponível", "g"), ("Oportunidades", op, ">R$300", "y"),
        ("Leads", tl, "", "n"), ("Conversão", f"{tx}%", f"{cv} fechados", "g"),
        ("Carteira", fmt(car), "", "n"), ("Agenda Hoje", fh, "follow-ups", "y" if fh > 0 else "n"),
    ]):
         st.markdown(kpi(l, v, s, c), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="chart-card"><div class="ct">🎯 Score de Propensão</div>', unsafe_allow_html=True)
            ds = df.sort_values("score", ascending=True)
            fig = go.Figure(go.Bar(x=ds["score"], y=ds["nome"].str.split().str[:2].str.join(" "), orientation="h",
                marker_color=[GREEN if s >= 75 else YELLOW if s >= 55 else NAVY for s in ds["score"]],
                marker_line_width=0, text=[f"{s}%" for s in ds["score"]], textposition="outside"))
            fig.update_layout(height=240, xaxis=dict(range=[0, 115], showgrid=True, gridcolor="#F5F5F5"), **{k: v for k, v in plt_def().items() if k != "xaxis"})
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="chart-card"><div class="ct">💰 Margem Disponível</div>', unsafe_allow_html=True)
            dm = df.sort_values("margem", ascending=True)
            fig2 = go.Figure(go.Bar(x=dm["margem"], y=dm["nome"].str.split().str[:2].str.join(" "), orientation="h",
                marker_color=[GREEN if m > 300 else YELLOW if m > 0 else RED for m in dm["margem"]],
                marker_line_width=0, text=[fmt(m) for m in dm["margem"]], textposition="outside"))
            fig2.add_vline(x=300, line_dash="dot", line_color=GREEN, line_width=1.5)
            fig2.update_layout(height=240, **plt_def())
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if not dfl.empty:
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="chart-card"><div class="ct">📋 Leads por Canal</div>', unsafe_allow_html=True)
                cc = dfl["canal"].value_counts().reset_index(); cc.columns = ["Canal", "Leads"]
                fig3 = px.bar(cc, x="Canal", y="Leads", color_discrete_sequence=[NAVY], text="Leads")
                fig3.update_traces(textposition="outside", marker_line_width=0)
                fig3.update_layout(height=220, **plt_def())
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c4:
                st.markdown('<div class="chart-card"><div class="ct">🔄 Pipeline de Leads</div>', unsafe_allow_html=True)
                sc2 = dfl["status"].value_counts().reset_index(); sc2.columns = ["Status", "Qtd"]
                fig4 = px.pie(sc2, values="Qtd", names="Status", color_discrete_sequence=[GREEN, YELLOW, NAVY, RED], hole=0.6)
                fig4.update_traces(textinfo="percent+label", textfont_size=10)
                fig4.update_layout(height=220, showlegend=False, paper_bgcolor="white", margin=dict(l=0, r=0, t=0, b=0), font=dict(family="Montserrat"))
                st.plotly_chart(fig4, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        dpg = df[df["dias"].notna()].copy()
        dpg["dias"] = dpg["dias"].astype(int)
        urg = dpg[dpg["dias"] <= 5].sort_values("dias")
        if len(urg) > 0:
            st.markdown('<div class="chart-card"><div class="ct">🗓 Pagamentos INSS Próximos 5 Dias</div>', unsafe_allow_html=True)
            for _, r in urg.iterrows():
                cor = RED if r["dias"] <= 1 else YELLOW if r["dias"] <= 3 else GREEN
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid #F5F5F5">
                  <div><span style="font-weight:700;color:{NAVY};font-size:13px">{r['nome'].split()[0]} {r['nome'].split()[1] if len(r['nome'].split()) > 1 else ''}</span>
                  <span style="font-size:11px;color:#888;margin-left:8px">{r['tel_d']}</span></div>
                  <div style="text-align:right"><span style="font-weight:700;color:{cor};font-size:14px">{r['prox'].strftime('%d/%m') if r['prox'] else ''}</span>
                  <span style="font-size:10px;color:#aaa;margin-left:6px">em {r['dias']} dia(s)</span></div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado. Vá para Clientes para começar.")

# ═══ CLIENTES ═══
elif pg == "Clientes":
    st.markdown('<div class="page-header"><h2>👥 Gestão de Clientes</h2><p>Base segura com dados criptografados — LGPD</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-block"><h4>➕ Cadastrar Novo Cliente</h4>', unsafe_allow_html=True)
    with st.form("fc", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo *")
            cpf = st.text_input("CPF")
            tel = st.text_input("Telefone")
            email = st.text_input("Email (mailing)")
            dn = st.date_input("Data Nascimento", value=date(1960, 1, 1), min_value=date(1930, 1, 1), max_value=date(2005, 1, 1))
        with c2:
            ben = st.number_input("Benefício (R$) *", min_value=0.0, step=50.0)
            par = st.number_input("Parcelas Ativas (R$)", min_value=0.0, step=50.0)
            canal = st.selectbox("Canal", ["Panfletagem", "Rádio", "WhatsApp", "Indicação", "Instagram", "Google", "Presencial"])
            status = st.selectbox("Status", ["Lead Quente", "Em análise", "Ativo"])
            int_ = st.selectbox("Interesse", ["Consignado INSS", "Portabilidade", "Refinanciamento", "Cartão Consignado", "Consignado Servidor"])
        obs = st.text_area("Observações", height=70)
        if st.form_submit_button("✅ Salvar Cadastro", use_container_width=True):
            if not nome or not ben: st.error("Nome e Benefício são obrigatórios.")
            else:
                ins_cli({"nome": nome, "cpf": cpf, "telefone": tel, "email": email, "data_nasc": str(dn), "beneficio": float(ben), "parcelas": float(par), "canal": canal, "status": status, "interesse": int_, "observacoes": obs})
                st.success(f"✅ {nome} cadastrado com sucesso!"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    df = load_clientes()
    if not df.empty:
        cf1, cf2, cf3 = st.columns(3)
        with cf1: fs = st.multiselect("Filtrar por Status", df["status"].unique().tolist(), default=df["status"].unique().tolist())
        with cf2: fc = st.multiselect("Filtrar por Canal", df["canal"].unique().tolist(), default=df["canal"].unique().tolist())
        with cf3: oo = st.checkbox("Exibir apenas oportunidades (>R$300)")
        
        dff = df[df["status"].isin(fs) & df["canal"].isin(fc)]
        if oo: dff = dff[dff["margem"] > 300]
        dff = dff.sort_values("score", ascending=False)
        
        st.markdown(f"<p style='color:#64748B;font-size:13px;margin:10px 0;'>Listando <b>{len(dff)}</b> cliente(s)</p>", unsafe_allow_html=True)
        
        for _, row in dff.iterrows():
            m = row["margem"]; cc = "cc-opp" if m > 300 else "cc-red" if m <= 0 else "cc-warn"
            bm = badge("Oportunidade", "g") if m > 300 else badge("Sem margem", "r") if m <= 0 else badge("Margem baixa", "y")
            
            # Caixa Estruturada em Substituição ao antigo Expander Poluído
            st.markdown(f"""
            <div class="content-block" style="border-left: 5px solid {GREEN if m>300 else RED if m<=0 else YELLOW} !important;">
                <h4 style="color:{NAVY}; margin:0 0 5px 0;">🔥 {row['nome']}</h4>
                <p style="color:#64748B; font-size:13px; margin:0 0 12px 0;">{row['tel_d']} · {row['canal']} · {row['interesse']}</p>
                <div style="margin-bottom:15px;">{bm} {badge(row['status'], 'b')} {badge(f"Score {row['score']}%", 'n')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            ca, cb = st.columns([2, 1])
            with ca:
                st.markdown(f"""
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;">
                    <div style="padding:12px; background:#F8FAFC; border-radius:8px; border:1px solid #E2E8F0;"><span style="font-size:11px; color:#64748B;">BENEFÍCIO</span><br><strong style="font-size:15px; color:{NAVY};">{fmt(row['beneficio'])}</strong></div>
                    <div style="padding:12px; background:#F8FAFC; border-radius:8px; border:1px solid #E2E8F0;"><span style="font-size:11px; color:#64748B;">MARGEM DISPONÍVEL</span><br><strong style="font-size:15px; color:{GREEN if m>300 else RED};">{fmt(m)}</strong></div>
                    <div style="padding:12px; background:#F8FAFC; border-radius:8px; border:1px solid #E2E8F0;"><span style="font-size:11px; color:#64748B;">PRÓXIMO INSS</span><br><strong style="font-size:15px; color:{NAVY};">{row['prox'].strftime('%d/%m/%Y') if row['prox'] else '—'}</strong></div>
                    <div style="padding:12px; background:#F8FAFC; border-radius:8px; border:1px solid #E2E8F0;"><span style="font-size:11px; color:#64748B;">MARGEM COMPROMETIDA</span><br><strong style="font-size:15px; color:{NAVY};">{row['pct']:.0f}%</strong></div>
                </div>
                """, unsafe_allow_html=True)
            with cb:
                with st.form(f"h{row['id']}"):
                    tp = st.selectbox("Registrar Contato", ["Ligação", "WhatsApp", "Visita", "Email"], key=f"tp{row['id']}")
                    nt = st.text_input("Nota / Resumo", key=f"nt{row['id']}", placeholder="O que foi conversado?")
                    if st.form_submit_button("📝 Salvar Histórico"):
                        ins_hist({"cliente_id": row["id"], "tipo": tp, "nota": nt, "data": str(date.today())}); st.rerun()
                
                with st.form(f"fu{row['id']}"):
                    dfu = st.date_input("Agendar Retorno (Follow-up)", value=date.today() + timedelta(days=1), key=f"dfu{row['id']}")
                    mfu = st.text_input("Motivo", key=f"mfu{row['id']}", placeholder="Ex: Enviar proposta simulada")
                    if st.form_submit_button("📅 Agendar Alerta"):
                        ins_fu({"cliente_id": row["id"], "data_followup": str(dfu), "motivo": mfu}); st.success("Agendado!")
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if row.get("email") and st.button("📧 Enviar Mailing", key=f"em{row['id']}", use_container_width=True):
                        pg2, dias2 = prox_pg(row["cpf_raw"])
                        html = f'<div style="font-family:sans-serif;max-width:500px;margin:0 auto"><div style="background:{NAVY};padding:20px;border-radius:10px 10px 0 0"><h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:24px"><p>Olá <b>{row["nome"].split()[0]}</b>! Seu próximo INSS: <b style="color:{GREEN}">{pg2.strftime("%d/%m/%Y") if pg2 else "Em breve"}</b></p></div></div>'
                        st.success("Enviado!") if send_email(row["email"], row["nome"], "Seu INSS — Núcleo Crédito", html) else st.error("Falha no envio")
                with c_btn2:
                    if st.button("🗑 Excluir Ficha", key=f"del{row['id']}", use_container_width=True):
                        del_cli(row["id"]); st.rerun()
            
            hist = load_hist(row["id"])
            if not hist.empty:
                st.markdown("<p style='font-size:12px; font-weight:700; color:#334155; margin:10px 0 5px 0;'>📋 Últimas Ocorrências:</p>", unsafe_allow_html=True)
                for _, h in hist.head(3).iterrows():
                    st.markdown(f'<div style="background:#F1F5F9; border-radius:6px; padding:8px 12px; margin-bottom:4px; font-size:12px; border-left:3px solid {GREEN};"><b>{h["data"]} · {h["tipo"]}</b>: {h["nota"]}</div>', unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#E2E8F0; margin:20px 0;'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado.")

# ═══ LEADS ═══
elif pg == "Leads":
    st.markdown('<div class="page-header"><h2>📋 Pipeline de Leads</h2><p>Funil de prospecção ativo</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-block"><h4>➕ Registrar Novo Lead</h4>', unsafe_allow_html=True)
    with st.form("fl", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            ln = st.text_input("Nome Comercial")
            lt = st.text_input("Telefone de Contato")
            lc = st.selectbox("Canal de Origem", ["Panfletagem", "Rádio", "WhatsApp", "Indicação", "Instagram", "Google", "Presencial"])
        with c2:
            li = st.selectbox("Produto de Interesse", ["Consignado INSS", "Portabilidade", "Refinanciamento", "Cartão Consignado"])
            lb = st.number_input("Benefício Base (R$)", min_value=0.0, step=50.0)
            ls = st.selectbox("Status Inicial", ["Novo", "Em negociação", "Convertido", "Perdido"])
        lo = st.text_area("Anotações do Lead", height=60)
        if st.form_submit_button("✅ Inserir no Funil", use_container_width=True):
            ins_lead({"nome": ln, "telefone": lt, "canal": lc, "interesse": li, "beneficio": float(lb), "status": ls, "observacoes": lo}); st.success("Lead registrado!"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    dfl = load_leads()
    if not dfl.empty:
        STATUS = ["Novo", "Em negociação", "Convertido", "Perdido"]
        CORES2 = {"Novo": NAVY, "Em negociação": YELLOW, "Convertido": GREEN, "Perdido": RED}
        cols = st.columns(4)
        for idx, s in enumerate(STATUS):
            g = dfl[dfl["status"] == s]
            with cols[idx]:
                st.markdown(f'<div class="content-block" style="background:#F8FAFC !important; border-top: 3px solid {CORES2[s]} !important;"><h5 style="color:{CORES2[s]}; margin:0 0 15px 0;">{s} ({len(g)})</h5>', unsafe_allow_html=True)
                for _, row in g.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div style="background:white; border:1px solid #E2E8F0; padding:12px; border-radius:8px; margin-bottom:8px;">
                            <strong style="color:{NAVY}; font-size:13px;">{row["nome"]}</strong><br>
                            <small style="color:#64748B;">{row["canal"]} · {row["interesse"]}</small>
                            {"<div style='color:"+GREEN+"; font-weight:700; margin-top:4px; font-size:12px;'>"+fmt(row["beneficio"])+"</div>" if row["beneficio"] else ""}
                        </div>
                        """, unsafe_allow_html=True)
                        ns = st.selectbox("Alterar Etapa", STATUS, index=STATUS.index(s), key=f"ls{row['id']}", label_visibility="collapsed")
                        if ns != s: upd_lead(row["id"], ns); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum lead registrado no pipeline.")

# ═══ CONTRATOS ═══
elif pg == "Contratos":
    st.markdown('<div class="page-header"><h2>📄 Gestão de Contratos e Comissões</h2><p>Controle de carteira ativa e receita estimada</p></div>', unsafe_allow_html=True)
    df_cli = load_clientes(); dfc = load_contratos()
    
    if not dfc.empty:
        tv = dfc["valor"].sum(); tc2 = (tv * 0.03)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(kpi("Volume Total de Vendas", fmt(tv), "", "n"), unsafe_allow_html=True)
        with c2: st.markdown(kpi("Receita de Comissão (3%)", fmt(tc2), "Previsão líquida", "g"), unsafe_allow_html=True)
        with c3: st.markdown(kpi("Contratos Emitidos", str(len(dfc)), "Este mês", "g"), unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
    st.markdown('<div class="content-block"><h4>➕ Formalizar Novo Contrato</h4>', unsafe_allow_html=True)
    if df_cli.empty: 
        st.warning("Cadastre um cliente na base relacional antes de emitir um contrato.")
    else:
        with st.form("fct", clear_on_submit=True):
            cm = {r["nome"]: r["id"] for _, r in df_cli.iterrows()}
            c1, c2 = st.columns(2)
            with c1:
                cs = st.selectbox("Associar Cliente *", list(cm.keys()))
                bco = st.selectbox("Instituição Bancária *", ["Banco BMG", "Banco Safra", "Banco PAN", "Caixa", "BRB", "Facta", "Itaú Consig."])
                val = st.number_input("Valor Bruto do Empréstimo (R$)", min_value=0.0, step=100.0)
            with c2:
                pt = st.number_input("Total de Parcelas (Meses)", min_value=1, max_value=84, value=36, step=1)
                tx2 = st.number_input("Taxa de Juros Aplicada (% a.m.)", min_value=0.5, max_value=5.0, value=1.8, step=0.1)
                di = st.date_input("Data de Início da Vigência")
            if st.form_submit_button("✅ Autenticar e Salvar Contrato", use_container_width=True):
                ins_ct({"cliente_id": cm[cs], "banco": bco, "valor": float(val), "parcelas_total": int(pt), "taxa_juros": float(tx2), "data_inicio": str(di)})
                st.success("Contrato integrado e registrado com sucesso!"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if not dfc.empty:
        dfc["parcela"] = dfc.apply(lambda r: round(r["valor"] * (r["taxa_juros"] / 100 * (1 + r["taxa_juros"] / 100)**r["parcelas_total"]) / ((1 + r["taxa_juros"] / 100)**r["parcelas_total"] - 1), 2) if r["parcelas_total"] > 0 else 0, axis=1)
        dfc["comissao"] = (dfc["valor"] * 0.03).round(2)
        
        st.markdown('<div class="chart-card"><h5>📋 Relação Macro de Contratos Ativos</h5>', unsafe_allow_html=True)
        st.dataframe(dfc[["cliente_nome", "banco", "valor", "parcelas_total", "parcela", "comissao", "data_inicio"]].rename(columns={"cliente_nome": "Cliente", "banco": "Banco", "valor": "Valor Total", "parcelas_total": "Vezes", "parcela": "Parcela/mês", "comissao": "Comissão", "data_inicio": "Data Emissão"}), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ═══ SIMULADOR ═══
elif pg == "Simulador":
    st.markdown('<div class="page-header"><h2>🧮 Simulador Analítico de Crédito</h2><p>Cálculo de margem real e projeções financeiras</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["💳 Simulação Consignável", "🔄 Engenharia de Portabilidade"])
    with tab1:
        st.markdown('<div class="content-block">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown("##### Estrutura de Rendimentos")
            ben2 = st.number_input("Benefício Mensal Bruto (R$)", min_value=0.0, value=1412.0, step=50.0, key="sb")
            pa2 = st.number_input("Descontos / Parcelas Ativas (R$)", min_value=0.0, value=0.0, step=50.0, key="spa")
            mc = ben2 * 0.4; md = max(0, mc - pa2); pct2 = min(100, round(pa2 / mc * 100, 1)) if mc > 0 else 0
            cor_md = GREEN if md > 300 else YELLOW if md > 0 else RED
            st.markdown(f"""<div style="background:#F8FAFC; border-radius:8px; padding:16px; border:1px solid #E2E8F0; margin-top:12px;">
              <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #E2E8F0; font-size:13px;"><span style="color:#64748B;">Margem máxima (40%)</span><strong style="color:{NAVY};">{fmt(mc)}</strong></div>
              <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #E2E8F0; font-size:13px;"><span style="color:#64748B;">Comprometido atual</span><strong style="color:{RED};">{fmt(pa2)}</strong></div>
              <div style="display:flex; justify-content:space-between; padding:6px 0; font-size:13px;"><span style="color:#64748B;">Margem real líquida</span><strong style="font-size:18px; color:{cor_md};">{fmt(md)}</strong></div>
              <div style="background:#E2E8F0; border-radius:99px; height:8px; margin-top:12px; overflow:hidden;"><div style="background:{GREEN if pct2<60 else YELLOW if pct2<90 else RED}; width:{pct2}%; height:100%;"></div></div>
              <div style="font-size:11px; color:#94A3B8; margin-top:4px;">Taxa de Ocupação da Margem: {pct2:.0f}%</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("##### Proposta Comercial")
            val2 = st.number_input("Valor Desejado do Empréstimo (R$)", min_value=0.0, value=3000.0, step=500.0, key="sv")
            hz = st.select_slider("Prazo de Amortização (Meses)", options=[12, 24, 36, 48, 60, 72, 84], value=36, key="spz")
            tx3 = st.slider("Taxa do Contrato (% a.m.)", 0.5, 3.5, 1.8, 0.1, key="stx")
            if val2 > 0 and ben2 > 0:
                r2 = tx3 / 100; fat = (r2 * (1 + r2)**hz) / ((1 + r2)**hz - 1)
                parc = val2 * fat; tot = parc * hz; jur = tot - val2; cb = parc <= md
                cr = GREEN if cb else RED; msg = "✅ Proposta Viável (Margem OK)" if cb else "❌ Margem Insuficiente"
                st.markdown(f"""<div style="background:white; border-radius:12px; padding:18px; border:1px solid #E2E8F0; border-top:4px solid {cr}; shadow:0 2px 4px rgba(0,0,0,0.02)">
                    <div style="text-align:center; padding-bottom:10px;">
                        <span style="font-size:11px; color:#64748B;">PARCELA MENSAL CALCULADA</span>
                        <h3 style="color:{cr}; font-weight:800; margin:4px 0;">{fmt(parc)}</h3>
                        <strong style="color:{cr}; font-size:12px;">{msg}</strong>
                    </div>
                  <div style="display:flex; justify-content:space-between; padding:6px 0; border-top:1px solid #F1F5F9; font-size:12px;"><span style="color:#64748B;">Total pago ao final</span><strong>{fmt(tot)}</strong></div>
                  <div style="display:flex; justify-content:space-between; padding:6px 0; border-top:1px solid #F1F5F9; font-size:12px;"><span style="color:#64748B;">Custo real de juros</span><strong style="color:{RED};">{fmt(jur)}</strong></div>
                  <div style="display:flex; justify-content:space-between; padding:6px 0; border-top:1px solid #F1F5F9; font-size:12px;"><span style="color:#64748B;">Sua receita estimada</span><strong style="color:{GREEN};">{fmt(val2*0.03)}</strong></div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if val2 > 0 and ben2 > 0:
            st.markdown('<div class="chart-card"><h5>📊 Curva de Amortização por Prazo</h5>', unsafe_allow_html=True)
            pzs = [12, 24, 36, 48, 60, 72, 84]; r2 = tx3 / 100
            pcs = [round(val2 * (r2 * (1 + r2)**p) / ((1 + r2)**p - 1), 2) for p in pzs]
            fig5 = go.Figure(go.Bar(x=[f"{p}m" for p in pzs], y=pcs, marker_color=[GREEN if p <= md else RED for p in pcs], text=[fmt(p) for p in pcs], textposition="outside"))
            fig5.add_hline(y=md, line_dash="dot", line_color=GREEN, line_width=2, annotation_text=f"Teto Disponível: {fmt(md)}")
            fig5.update_layout(height=260, **plt_def())
            st.plotly_chart(fig5, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ═══ ALERTAS ═══
elif pg == "Alertas":
    st.markdown('<div class="page-header"><h2>🔔 Central de Oportunidades Automática</h2><p>Filtros preditivos baseados nas tabelas de pagamento do INSS</p></div>', unsafe_allow_html=True)
    df = load_clientes()
    if df.empty: 
        st.info("Nenhum registro localizado para triagem de score.")
    else:
        opp = df[df["margem"] > 300].sort_values("score", ascending=False)
        bx = df[(df["margem"] > 0) & (df["margem"] <= 300)].sort_values("score", ascending=False)
        ph = df[(df["dias"].notna()) & (df["dias"].astype(float) <= 2)]
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(kpi("Prioridade Máxima", str(len(opp)), "Margem livre > R$300", "g"), unsafe_allow_html=True)
        with c2: st.markdown(kpi("Margem Limítrofe", str(len(bx)), "Verificar Refin", "y"), unsafe_allow_html=True)
        with c3: st.markdown(kpi("Urgente (INSS de Hoje/Amanhã)", str(len(ph)), "Gatilho de contato", "r"), unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        if len(opp) > 0:
            st.markdown(f"<h5 style='color:{GREEN}; font-weight:700;'>🎯 Leads Qualificados para Oferta Especial</h5>", unsafe_allow_html=True)
            for _, row in opp.iterrows():
                st.markdown(f"""
                <div class="content-block" style="border-left: 4px solid {GREEN} !important; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size:15px; color:{NAVY};">{row['nome']}</strong><br>
                        <small style="color:#64748B;">{row['tel_d']} · Origem: {row['canal']} · Score de Propensão: {row['score']}%</small>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:11px; color:#64748B;">MARGEM COMPROVADA</span><br>
                        <strong style="font-size:18px; color:{GREEN};">{fmt(row['margem'])}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ═══ AGENDA ═══
elif pg == "Agenda":
    st.markdown('<div class="page-header"><h2>📅 Controle de Compromissos (Follow-ups)</h2><p>Agendamentos sincronizados com a carteira</p></div>', unsafe_allow_html=True)
    dfa2 = load_fu()
    if not dfa2.empty:
        dfa2["data_followup"] = pd.to_datetime(dfa2["data_followup"]).dt.date
        venc = dfa2[dfa2["data_followup"] < date.today()].sort_values("data_followup")
        hj = dfa2[dfa2["data_followup"] == date.today()]
        prx = dfa2[dfa2["data_followup"] > date.today()].sort_values("data_followup")
        
        for titulo, grupo, cor in [("🚨 Retornos em Atraso Vencidos", venc, RED), ("📌 Agenda do Dia de Hoje", hj, GREEN), ("📆 Retornos Futuros Programados", prx, NAVY)]:
            if len(grupo) == 0: continue
            st.markdown(f"<h5 style='color:{cor}; font-weight:700; margin-top:15px;'>{titulo} ({len(grupo)})</h5>", unsafe_allow_html=True)
            for _, r in grupo.iterrows():
                ca2, cb2 = st.columns([5, 1])
                with ca2:
                    st.markdown(f"""
                    <div class="content-block" style="border-left:3px solid {cor} !important; padding:14px !important;">
                        <strong style="color:{NAVY};">{r["cliente_nome"]}</strong>
                        <span style="font-size:11px; color:#64748B; margin-left:10px;">{r["data_followup"].strftime("%d/%m/%Y")}</span><br>
                        <p style="margin:4px 0 0 0; font-size:13px; color:#334155;">{r["motivo"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with cb2:
                    if st.button("Concluir Alerta", key=f"dfu{r['id']}", use_container_width=True): 
                        del_fu(r["id"]); st.rerun()
    else:
        st.info("Nenhum agendamento ativo. Crie novos lembretes acessidando a aba Clientes.")

# ═══ METAS ═══
elif pg == "Metas":
    st.markdown('<div class="page-header"><h2>🎯 Planejamento de Metas Comerciais</h2><p>Acompanhamento de performance do operador em tempo real</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: mc2 = st.number_input("Meta de Contratos Fechados/Mês", min_value=1, value=30, step=5)
    with c2: ml = st.number_input("Meta de Captação de Leads/Mês", min_value=1, value=50, step=5)
    with c3: mcm = st.number_input("Meta de Receita de Comissão (R$)", min_value=0.0, value=3000.0, step=500.0)
    
    dfl2 = load_leads(); dfc2 = load_contratos()
    lm = len(dfl2); ctm = len(dfc2); com = dfc2["valor"].sum() * 0.03 if not dfc2.empty else 0
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    
    for lbl, atual, meta, cor2 in [("Contratos Consolidados", ctm, mc2, GREEN), ("Mailing de Leads Expandido", lm, ml, NAVY), ("Receita Bruta Conquistada", com, mcm, YELLOW)]:
        pct3 = min(100, round(atual / meta * 100, 1)) if meta > 0 else 0
        vf = fmt(atual) if "R$" in lbl else str(int(atual))
        mf = fmt(meta) if "R$" in lbl else str(int(meta))
        st.markdown(f"""
        <div class="content-block">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <strong style="font-size:14px; color:{NAVY};">{lbl}</strong>
            <span style="font-size:13px; color:#64748B;">{vf} / {mf} ({pct3}%)</span>
          </div>
          <div style="background:#E2E8F0; border-radius:99px; height:12px; overflow:hidden;">
            <div style="background:{cor2}; width:{pct3}%; height:100%;"></div>
          </div>
          <div style="font-size:11px; color:{GREEN if pct3>=100 else '#64748B'}; font-weight:600; margin-top:6px;">
            {'🎉 Meta operacional batida!' if pct3>=100 else f'Faltam {mf if "R$" in lbl else str(int(meta-atual))} para a homologação do teto'}
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)