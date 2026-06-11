import streamlit as st
import os, hashlib, hmac
from datetime import date, datetime, timedelta
from supabase import create_client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cryptography.fernet import Fernet
import base64
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# ── CONFIG ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Núcleo Crédito", page_icon="⚛", layout="wide",
                   initial_sidebar_state="collapsed")

NAVY="#1B3A6B"; GREEN="#1A7A5E"; RED="#C0392B"; YELLOW="#F5A623"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
*{{font-family:'Montserrat',sans-serif!important}}
.main{{background:#F0F4F8;padding-top:0!important}}
header[data-testid="stHeader"]{{display:none}}
footer{{display:none}}
#MainMenu{{display:none}}
[data-testid="stSidebarContent"]{{display:none}}
[data-testid="collapsedControl"]{{display:none}}

.topbar{{
  position:fixed;top:0;left:0;right:0;z-index:9999;
  background:linear-gradient(90deg,{NAVY} 0%,#0F2347 100%);
  height:56px;display:flex;align-items:center;
  padding:0 24px;box-shadow:0 2px 12px rgba(0,0,0,0.25);
  gap:0;
}}
.topbar-logo{{
  display:flex;align-items:center;gap:10px;
  text-decoration:none;margin-right:32px;flex-shrink:0;
}}
.topbar-logo-text{{line-height:1}}
.topbar-logo-name{{
  color:white;font-size:16px;font-weight:800;
  letter-spacing:-0.3px;display:block;
}}
.topbar-logo-sub{{
  color:rgba(255,255,255,0.45);font-size:9px;
  font-style:italic;display:block;margin-top:1px;
}}
.topbar-nav{{
  display:flex;align-items:center;gap:2px;flex:1;
}}
.nav-btn{{
  background:transparent;border:none;
  color:rgba(255,255,255,0.65);
  font-family:'Montserrat',sans-serif;
  font-size:12px;font-weight:600;
  padding:8px 14px;border-radius:8px;
  cursor:pointer;transition:all .15s;
  white-space:nowrap;
}}
.nav-btn:hover{{
  background:rgba(255,255,255,0.12);
  color:white;
}}
.nav-btn.active{{
  background:rgba(255,255,255,0.18);
  color:white;
}}
.topbar-right{{
  display:flex;align-items:center;gap:12px;margin-left:auto;
}}
.topbar-user{{
  color:rgba(255,255,255,0.7);font-size:12px;font-weight:500;
}}
.topbar-logout{{
  background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.2);
  color:white;font-family:'Montserrat',sans-serif;
  font-size:11px;font-weight:600;padding:5px 12px;
  border-radius:6px;cursor:pointer;
}}

.main-content{{margin-top:72px;padding:0 8px;}}

.page-header{{
  background:white;border-radius:14px;padding:18px 24px;
  margin-bottom:18px;border-left:4px solid {GREEN};
  box-shadow:0 2px 8px rgba(0,0,0,0.05);
}}
.page-header h2{{color:{NAVY};font-size:18px;font-weight:800;margin:0 0 3px}}
.page-header p{{color:#888;font-size:12px;margin:0}}

.kpi{{
  background:white;border-radius:12px;padding:16px 14px;
  box-shadow:0 2px 6px rgba(0,0,0,0.05);
  border-top:3px solid {GREEN};text-align:center;
}}
.kpi.n{{border-top-color:{NAVY}}}
.kpi.r{{border-top-color:{RED}}}
.kpi.y{{border-top-color:{YELLOW}}}
.kpi-lbl{{font-size:9px;color:#999;text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:5px}}
.kpi-val{{font-size:22px;font-weight:800;color:{NAVY};line-height:1}}
.kpi-sub{{font-size:9px;color:#bbb;margin-top:4px}}

.chart-card{{
  background:white;border-radius:14px;padding:18px 20px;
  box-shadow:0 2px 6px rgba(0,0,0,0.05);margin-bottom:14px;
}}
.ct{{font-size:12px;font-weight:700;color:{NAVY};
  margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #F0F0F0}}

.badge{{display:inline-block;padding:2px 9px;border-radius:99px;font-size:10px;font-weight:700;margin-right:3px}}
.bg{{background:#E8F5F0;color:#0F6E56}}
.by{{background:#FFF3CD;color:#856404}}
.br{{background:#FDECEA;color:#A32D2D}}
.bb{{background:#E6F1FB;color:#185FA5}}
.bn{{background:#EBF0F8;color:{NAVY}}}

.client-card{{
  background:white;border-radius:12px;padding:14px 18px;
  margin-bottom:8px;box-shadow:0 2px 5px rgba(0,0,0,0.04);
  border-left:4px solid #E0E0E0;
}}
.cc-opp{{border-left-color:{GREEN}}}
.cc-warn{{border-left-color:{YELLOW}}}
.cc-red{{border-left-color:{RED}}}

.login-wrap{{
  max-width:360px;margin:80px auto;background:white;
  border-radius:18px;padding:36px 32px;
  box-shadow:0 8px 40px rgba(0,0,0,0.12);text-align:center;
}}
.stButton>button{{
  background:{NAVY}!important;color:white!important;border:none!important;
  border-radius:9px!important;padding:9px 18px!important;
  font-family:'Montserrat',sans-serif!important;
  font-weight:700!important;font-size:12px!important;width:100%!important;
}}
</style>
""", unsafe_allow_html=True)

# ── SECRETS ────────────────────────────────────────────────────────────────
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
    return f"***.{d[3:6]}.{d[6:9]}-**" if len(d)==11 else "***.***.***-**"

def mask_tel(t):
    d = "".join(filter(str.isdigit, t or ""))
    return f"({d[:2]}) *****-{d[-4:]}" if len(d)>=8 else "(**)*****-****"

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
MESES=["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

def prox_pg(cpf_raw):
    try:
        d="".join(filter(str.isdigit,cpf_raw or ""))
        if not d: return None,None
        u=int(d[-1]); hoje=date.today()
        mes=MESES[hoje.month-1]
        if u in INSS and mes in INSS[u]:
            pg=datetime.strptime(INSS[u][mes],"%Y-%m-%d").date()
            if pg<hoje:
                pm=MESES[hoje.month%12]
                if pm in INSS[u]:
                    pg=datetime.strptime(INSS[u][pm],"%Y-%m-%d").date()
            return pg,(pg-hoje).days
    except: pass
    return None,None

# ── SCORE ───────────────────────────────────────────────────────────────────
def score(row):
    s=0
    m=row.get("margem",0)
    if m>600: s+=40
    elif m>300: s+=30
    elif m>100: s+=15
    s+={"Ativo":20,"Lead Quente":25,"Em análise":15}.get(row.get("status",""),0)
    s+={"Indicação":20,"WhatsApp":15,"Rádio":12,"Panfletagem":10,"Google":12,"Instagram":8}.get(row.get("canal",""),5)
    _,dias=prox_pg(row.get("cpf_raw",""))
    if dias is not None:
        if 0<=dias<=2: s+=15
        elif 3<=dias<=5: s+=10
    return min(s,100)

# ── EMAIL ───────────────────────────────────────────────────────────────────
def send_email(to_email,to_name,subject,html):
    try:
        cfg=sib_api_v3_sdk.Configuration(); cfg.api_key["api-key"]=BREVO_KEY
        api=sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(cfg))
        api.send_transac_email(sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email":to_email,"name":to_name}],
            sender={"email":SENDER_EMAIL,"name":SENDER_NAME},
            subject=subject,html_content=html))
        return True
    except: return False

# ── DB ──────────────────────────────────────────────────────────────────────
def load_clientes():
    if not sb: return pd.DataFrame()
    try:
        r=sb.table("clientes").select("*").order("created_at",desc=True).execute()
        if not r.data: return pd.DataFrame()
        df=pd.DataFrame(r.data)
        df["cpf_raw"]=df["cpf"].apply(lambda x: dec(x) if x else "")
        df["tel_raw"]=df["telefone"].apply(lambda x: dec(x) if x else "")
        df["cpf_d"]=df["cpf_raw"].apply(mask_cpf)
        df["tel_d"]=df["tel_raw"].apply(mask_tel)
        df["margem"]=df.apply(lambda r: round(r["beneficio"]*0.4-r["parcelas"],2),axis=1)
        df["pct"]=df.apply(lambda r: min(100,round(r["parcelas"]/(r["beneficio"]*0.4)*100,1)) if r["beneficio"]>0 else 0,axis=1)
        df["score"]=df.apply(score,axis=1)
        df["prox"],df["dias"]=zip(*df.apply(lambda r: prox_pg(r["cpf_raw"]),axis=1))
        return df
    except Exception as e:
        st.error(f"Erro: {e}"); return pd.DataFrame()

def load_leads():
    if not sb: return pd.DataFrame()
    try:
        r=sb.table("leads").select("*").order("created_at",desc=True).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except: return pd.DataFrame()

def load_contratos():
    if not sb: return pd.DataFrame()
    try:
        r=sb.table("contratos").select("*, clientes(nome)").order("created_at",desc=True).execute()
        if not r.data: return pd.DataFrame()
        df=pd.DataFrame(r.data)
        df["cliente_nome"]=df["clientes"].apply(lambda x: x["nome"] if isinstance(x,dict) else "")
        return df
    except: return pd.DataFrame()

def load_hist(cid):
    if not sb: return pd.DataFrame()
    try:
        r=sb.table("historico").select("*").eq("cliente_id",cid).order("created_at",desc=True).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except: return pd.DataFrame()

def load_fu():
    if not sb: return pd.DataFrame()
    try:
        r=sb.table("followups").select("*, clientes(nome)").order("data_followup").execute()
        if not r.data: return pd.DataFrame()
        df=pd.DataFrame(r.data)
        df["cliente_nome"]=df["clientes"].apply(lambda x: x["nome"] if isinstance(x,dict) else "")
        return df
    except: return pd.DataFrame()

def ins_cli(d):
    d["cpf"]=enc(d.get("cpf","")); d["telefone"]=enc(d.get("telefone",""))
    return sb.table("clientes").insert(d).execute()

def ins_lead(d): return sb.table("leads").insert(d).execute()
def ins_hist(d): return sb.table("historico").insert(d).execute()
def ins_fu(d):   return sb.table("followups").insert(d).execute()
def ins_ct(d):   return sb.table("contratos").insert(d).execute()
def upd_lead(id,s): return sb.table("leads").update({"status":s}).eq("id",id).execute()
def del_cli(id):
    sb.table("historico").delete().eq("cliente_id",id).execute()
    sb.table("followups").delete().eq("cliente_id",id).execute()
    sb.table("clientes").delete().eq("id",id).execute()
def del_fu(id): sb.table("followups").delete().eq("id",id).execute()

# ── AUTH ────────────────────────────────────────────────────────────────────
USERS={"eduardo":{"pwd":hashlib.sha256(b"nucleo2026").hexdigest(),"name":"Eduardo Lima de Sousa"}}

def chk(u,p):
    usr=USERS.get(u.lower())
    if not usr: return False
    return hmac.compare_digest(usr["pwd"],hashlib.sha256(p.encode()).hexdigest())

# ── HELPERS ─────────────────────────────────────────────────────────────────
def fmt(v): return f"R$ {abs(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
def kpi(l,v,s="",c="g"):
    cc={"n":"n","r":"r","y":"y"}.get(c,"")
    return f'<div class="kpi {cc}"><div class="kpi-lbl">{l}</div><div class="kpi-val">{v}</div>{"<div class=kpi-sub>"+s+"</div>" if s else ""}</div>'
def badge(t,c):
    cl={"g":"bg","y":"by","r":"br","b":"bb","n":"bn"}.get(c,"bb")
    return f'<span class="badge {cl}">{t}</span>'
def plt_def(): return dict(plot_bgcolor="white",paper_bgcolor="white",margin=dict(l=0,r=10,t=8,b=0),font=dict(family="Montserrat"),xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor="#F5F5F5"))

# ── SESSION ─────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
if "page" not in st.session_state:
    st.session_state.page="Dashboard"

# ── LOGIN ────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    col1,col2,col3=st.columns([1,1,1])
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
            u=st.text_input("Usuário", placeholder="usuário")
            p=st.text_input("Senha", type="password", placeholder="••••••••")
            if st.form_submit_button("Entrar", use_container_width=True):
                if chk(u,p):
                    st.session_state.logged_in=True
                    st.session_state.username=u
                    st.session_state.uname=USERS[u.lower()]["name"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        st.markdown(f"<p style='text-align:center;font-size:10px;color:#ccc;margin-top:10px'>Dados criptografados · LGPD</p>",unsafe_allow_html=True)
    st.stop()

# ── TOP NAV ──────────────────────────────────────────────────────────────────
PAGES=["Dashboard","Clientes","Leads","Contratos","Simulador","Alertas","Agenda","Email Marketing","Metas"]
ICONS={"Dashboard":"📊","Clientes":"👥","Leads":"📋","Contratos":"📄","Simulador":"🧮","Alertas":"🔔","Agenda":"📅","Email Marketing":"📧","Metas":"🎯"}

pg=st.session_state.page

nav_btns="".join([
    f'<button class="nav-btn {"active" if pg==p else ""}" onclick="window.location.href=\'?page={p}\'">{ICONS[p]} {p}</button>'
    for p in PAGES
])

st.markdown(f"""
<div class="topbar">
  <div class="topbar-logo">
    <svg width="28" height="28" viewBox="0 0 64 64" fill="none">
      <ellipse cx="32" cy="32" rx="26" ry="10" stroke="{GREEN}" stroke-width="2" fill="none"/>
      <ellipse cx="32" cy="32" rx="26" ry="10" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(60 32 32)"/>
      <ellipse cx="32" cy="32" rx="26" ry="10" stroke="{GREEN}" stroke-width="2" fill="none" transform="rotate(120 32 32)"/>
      <circle cx="32" cy="32" r="5" fill="{GREEN}"/><circle cx="32" cy="32" r="2.5" fill="white"/>
    </svg>
    <div class="topbar-logo-text">
      <span class="topbar-logo-name">Núcleo Crédito</span>
      <span class="topbar-logo-sub">No centro da sua vida financeira.</span>
    </div>
  </div>
  <div class="topbar-nav">{nav_btns}</div>
  <div class="topbar-right">
    <span class="topbar-user">{st.session_state.uname.split()[0]}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Handle URL param navigation
qp = st.query_params
if "page" in qp and qp["page"] in PAGES:
    st.session_state.page = qp["page"]
    pg = st.session_state.page

# Sidebar logout fallback
with st.sidebar:
    if st.button("🚪 Sair"):
        st.session_state.logged_in=False
        st.rerun()
    st.caption(f"v2.0 · {date.today().strftime('%d/%m/%Y')}")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ── PÁGINAS ──────────────────────────────────────────────────────────────────

# ═══ DASHBOARD ═══
if pg=="Dashboard":
    st.markdown('<div class="page-header"><h2>📊 Dashboard de Performance</h2><p>Visão geral da operação em tempo real</p></div>',unsafe_allow_html=True)
    df=load_clientes(); dfl=load_leads(); dfc=load_contratos(); dfa=load_fu()

    tc=len(df); at=len(df[df["status"]=="Ativo"]) if not df.empty else 0
    mt=df["margem"].clip(lower=0).sum() if not df.empty else 0
    op=len(df[df["margem"]>300]) if not df.empty else 0
    tl=len(dfl); cv=len(dfl[dfl["status"]=="Convertido"]) if not dfl.empty else 0
    tx=round(cv/tl*100,1) if tl>0 else 0
    car=dfc["valor"].sum() if not dfc.empty else 0
    fh=0
    if not dfa.empty:
        dfa["data_followup"]=pd.to_datetime(dfa["data_followup"]).dt.date
        fh=len(dfa[dfa["data_followup"]==date.today()])

    cols=st.columns(8)
    for col,(l,v,s,c) in zip(cols,[
        ("Clientes",tc,"","n"),("Ativos",at,"","g"),
        ("Margem Total",fmt(mt),"disponível","g"),("Oportunidades",op,">R$300","y"),
        ("Leads",tl,"","n"),("Conversão",f"{tx}%",f"{cv} fechados","g"),
        ("Carteira",fmt(car),"","n"),("Agenda Hoje",fh,"follow-ups","y" if fh>0 else "n"),
    ]):
        with col: st.markdown(kpi(l,v,s,c),unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)

    if not df.empty:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="chart-card"><div class="ct">🎯 Score de Propensão</div>',unsafe_allow_html=True)
            ds=df.sort_values("score",ascending=True)
            fig=go.Figure(go.Bar(x=ds["score"],y=ds["nome"].str.split().str[:2].str.join(" "),orientation="h",
                marker_color=[GREEN if s>=75 else YELLOW if s>=55 else NAVY for s in ds["score"]],
                marker_line_width=0,text=[f"{s}%" for s in ds["score"]],textposition="outside"))
            fig.update_layout(height=240,xaxis=dict(range=[0,115],showgrid=True,gridcolor="#F5F5F5"),**{k:v for k,v in plt_def().items() if k!="xaxis"})
            st.plotly_chart(fig,use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="chart-card"><div class="ct">💰 Margem Disponível</div>',unsafe_allow_html=True)
            dm=df.sort_values("margem",ascending=True)
            fig2=go.Figure(go.Bar(x=dm["margem"],y=dm["nome"].str.split().str[:2].str.join(" "),orientation="h",
                marker_color=[GREEN if m>300 else YELLOW if m>0 else RED for m in dm["margem"]],
                marker_line_width=0,text=[fmt(m) for m in dm["margem"]],textposition="outside"))
            fig2.add_vline(x=300,line_dash="dot",line_color=GREEN,line_width=1.5)
            fig2.update_layout(height=240,**plt_def())
            st.plotly_chart(fig2,use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)

        if not dfl.empty:
            c3,c4=st.columns(2)
            with c3:
                st.markdown('<div class="chart-card"><div class="ct">📋 Leads por Canal</div>',unsafe_allow_html=True)
                cc=dfl["canal"].value_counts().reset_index(); cc.columns=["Canal","Leads"]
                fig3=px.bar(cc,x="Canal",y="Leads",color_discrete_sequence=[NAVY],text="Leads")
                fig3.update_traces(textposition="outside",marker_line_width=0)
                fig3.update_layout(height=220,**plt_def())
                st.plotly_chart(fig3,use_container_width=True)
                st.markdown('</div>',unsafe_allow_html=True)
            with c4:
                st.markdown('<div class="chart-card"><div class="ct">🔄 Pipeline de Leads</div>',unsafe_allow_html=True)
                sc2=dfl["status"].value_counts().reset_index(); sc2.columns=["Status","Qtd"]
                fig4=px.pie(sc2,values="Qtd",names="Status",color_discrete_sequence=[GREEN,YELLOW,NAVY,RED],hole=0.6)
                fig4.update_traces(textinfo="percent+label",textfont_size=10)
                fig4.update_layout(height=220,showlegend=False,paper_bgcolor="white",margin=dict(l=0,r=0,t=0,b=0),font=dict(family="Montserrat"))
                st.plotly_chart(fig4,use_container_width=True)
                st.markdown('</div>',unsafe_allow_html=True)

        dpg=df[df["dias"].notna()].copy()
        dpg["dias"]=dpg["dias"].astype(int)
        urg=dpg[dpg["dias"]<=5].sort_values("dias")
        if len(urg)>0:
            st.markdown('<div class="chart-card"><div class="ct">🗓 Pagamentos INSS Próximos 5 Dias</div>',unsafe_allow_html=True)
            for _,r in urg.iterrows():
                cor=RED if r["dias"]<=1 else YELLOW if r["dias"]<=3 else GREEN
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid #F5F5F5">
                  <div><span style="font-weight:700;color:{NAVY};font-size:13px">{r['nome'].split()[0]} {r['nome'].split()[1] if len(r['nome'].split())>1 else ''}</span>
                  <span style="font-size:11px;color:#888;margin-left:8px">{r['tel_d']}</span></div>
                  <div style="text-align:right"><span style="font-weight:700;color:{cor};font-size:14px">{r['prox'].strftime('%d/%m') if r['prox'] else ''}</span>
                  <span style="font-size:10px;color:#aaa;margin-left:6px">em {r['dias']} dia(s)</span></div>
                </div>""",unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado. Vá para Clientes para começar.")

# ═══ CLIENTES ═══
elif pg=="Clientes":
    st.markdown('<div class="page-header"><h2>👥 Gestão de Clientes</h2><p>Base segura com dados criptografados — LGPD</p></div>',unsafe_allow_html=True)
    with st.expander("➕ Cadastrar Novo Cliente"):
        with st.form("fc",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                nome=st.text_input("Nome Completo *"); cpf=st.text_input("CPF (criptografado)")
                tel=st.text_input("Telefone (criptografado)"); email=st.text_input("Email (mailing)")
                dn=st.date_input("Data Nascimento",value=date(1960,1,1),min_value=date(1930,1,1),max_value=date(2005,1,1))
            with c2:
                ben=st.number_input("Benefício (R$) *",min_value=0.0,step=50.0)
                par=st.number_input("Parcelas Ativas (R$)",min_value=0.0,step=50.0)
                canal=st.selectbox("Canal",["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"])
                status=st.selectbox("Status",["Lead Quente","Em análise","Ativo"])
                int_=st.selectbox("Interesse",["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor"])
            obs=st.text_area("Observações",height=55)
            if st.form_submit_button("✅ Cadastrar",use_container_width=True):
                if not nome or not ben: st.error("Nome e Benefício são obrigatórios.")
                else:
                    ins_cli({"nome":nome,"cpf":cpf,"telefone":tel,"email":email,"data_nasc":str(dn),"beneficio":float(ben),"parcelas":float(par),"canal":canal,"status":status,"interesse":int_,"observacoes":obs})
                    st.success(f"✅ {nome} cadastrado!"); st.rerun()

    df=load_clientes()
    if not df.empty:
        cf1,cf2,cf3=st.columns(3)
        with cf1: fs=st.multiselect("Status",df["status"].unique().tolist(),default=df["status"].unique().tolist())
        with cf2: fc=st.multiselect("Canal",df["canal"].unique().tolist(),default=df["canal"].unique().tolist())
        with cf3: oo=st.checkbox("Apenas oportunidades (>R$300)")
        dff=df[df["status"].isin(fs)&df["canal"].isin(fc)]
        if oo: dff=dff[dff["margem"]>300]
        dff=dff.sort_values("score",ascending=False)
        st.markdown(f"<p style='color:#888;font-size:11px;margin:8px 0 12px'><b>{len(dff)}</b> cliente(s)</p>",unsafe_allow_html=True)
        for _,row in dff.iterrows():
            m=row["margem"]; cc="cc-opp" if m>300 else "cc-red" if m<=0 else "cc-warn"
            bm=badge("Oportunidade","g") if m>300 else badge("Sem margem","r") if m<=0 else badge("Margem baixa","y")
            with st.expander(f"{'🔥' if row['score']>=75 else '⚡' if row['score']>=55 else '📋'} {row['nome']} — Score {row['score']}% — {fmt(m)} disponível"):
                ca,cb=st.columns([2,1])
                with ca:
                    st.markdown(f"""<div class="client-card {cc}">
                      <div style="font-size:14px;font-weight:800;color:{NAVY}">{row['nome']}</div>
                      <div style="font-size:11px;color:#888;margin:3px 0 7px">{row['tel_d']} · {row['canal']} · {row['interesse']}</div>
                      <div>{bm} {badge(row['status'],'b')} {badge(f"Score {row['score']}%",'n')}</div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-top:10px;font-size:12px">
                      {"".join([f'<div style="padding:8px;background:white;border-radius:9px;border:1px solid #F0F0F0"><div style="font-size:9px;color:#888;margin-bottom:2px">{l}</div><div style="font-weight:700;color:{NAVY}">{v}</div></div>' for l,v in [("BENEFÍCIO",fmt(row['beneficio'])),("MARGEM DISP.",fmt(m)),("PRÓX INSS",row['prox'].strftime('%d/%m/%Y') if row['prox'] else '—'),("COMPROMETIDO",f"{row['pct']:.0f}%")]])}
                    </div>""",unsafe_allow_html=True)
                with cb:
                    st.markdown("**Registrar contato**")
                    with st.form(f"h{row['id']}"):
                        tp=st.selectbox("Tipo",["Ligação","WhatsApp","Visita","Email","Outro"],key=f"tp{row['id']}")
                        nt=st.text_area("Nota",height=55,key=f"nt{row['id']}")
                        if st.form_submit_button("📝 Salvar"):
                            ins_hist({"cliente_id":row["id"],"tipo":tp,"nota":nt,"data":str(date.today())}); st.success("✅"); st.rerun()
                    with st.form(f"fu{row['id']}"):
                        dfu=st.date_input("Agendar follow-up",value=date.today()+timedelta(days=1),key=f"dfu{row['id']}")
                        mfu=st.text_input("Motivo",key=f"mfu{row['id']}")
                        if st.form_submit_button("📅 Agendar"): ins_fu({"cliente_id":row["id"],"data_followup":str(dfu),"motivo":mfu}); st.success("✅")
                    if row.get("email") and st.button(f"📧 Enviar INSS",key=f"em{row['id']}"):
                        pg2,dias2=prox_pg(row["cpf_raw"])
                        html=f'<div style="font-family:sans-serif;max-width:500px;margin:0 auto"><div style="background:{NAVY};padding:20px;border-radius:10px 10px 0 0"><h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:24px"><p>Olá <b>{row["nome"].split()[0]}</b>! Seu próximo INSS: <b style="color:{GREEN}">{pg2.strftime("%d/%m/%Y") if pg2 else "Em breve"}</b></p><a href="https://wa.me/5511952723015" style="background:{GREEN};color:white;padding:10px 20px;border-radius:99px;text-decoration:none">💬 WhatsApp</a></div></div>'
                        st.success("✅ Enviado!") if send_email(row["email"],row["nome"],f"Seu INSS — Núcleo Crédito",html) else st.error("Erro no envio")
                    if st.button(f"🗑 Remover",key=f"del{row['id']}"):
                        del_cli(row["id"]); st.rerun()
                hist=load_hist(row["id"])
                if not hist.empty:
                    st.markdown("**Histórico de atendimento**")
                    for _,h in hist.iterrows():
                        st.markdown(f'<div style="background:#F8F9FA;border-radius:8px;padding:7px 11px;margin-bottom:5px;border-left:3px solid {GREEN}"><span style="font-size:10px;color:#888">{h["data"]} · {h["tipo"]}</span><br><span style="font-size:12px">{h["nota"]}</span></div>',unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado.")

# ═══ LEADS ═══
elif pg=="Leads":
    st.markdown('<div class="page-header"><h2>📋 Pipeline de Leads</h2><p>Funil de vendas visual</p></div>',unsafe_allow_html=True)
    with st.expander("➕ Novo Lead"):
        with st.form("fl",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                ln=st.text_input("Nome"); lt=st.text_input("Telefone")
                lc=st.selectbox("Canal",["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"])
            with c2:
                li=st.selectbox("Interesse",["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado"])
                lb=st.number_input("Benefício (R$)",min_value=0.0,step=50.0)
                ls=st.selectbox("Status",["Novo","Em negociação","Convertido","Perdido"])
            lo=st.text_area("Observações",height=50)
            if st.form_submit_button("✅ Registrar",use_container_width=True):
                ins_lead({"nome":ln,"telefone":lt,"canal":lc,"interesse":li,"beneficio":float(lb),"status":ls,"observacoes":lo}); st.success("Lead registrado!"); st.rerun()

    dfl=load_leads()
    if not dfl.empty:
        STATUS=["Novo","Em negociação","Convertido","Perdido"]
        ICONS2={"Novo":"🔵","Em negociação":"🟡","Convertido":"✅","Perdido":"❌"}
        CORES2={"Novo":NAVY,"Em negociação":YELLOW,"Convertido":GREEN,"Perdido":RED}
        cols=st.columns(4)
        for idx,s in enumerate(STATUS):
            g=dfl[dfl["status"]==s]
            with cols[idx]:
                st.markdown(f'<div style="background:white;border-radius:12px;padding:12px;box-shadow:0 2px 6px rgba(0,0,0,0.06);min-height:100px"><div style="font-size:12px;font-weight:800;color:{CORES2[s]};margin-bottom:10px">{ICONS2[s]} {s} <span style="background:#F0F0F0;padding:1px 7px;border-radius:99px;font-size:10px;margin-left:3px">{len(g)}</span></div>',unsafe_allow_html=True)
                for _,row in g.iterrows():
                    st.markdown(f'<div style="background:#F8F9FA;border-radius:9px;padding:9px;margin-bottom:7px;border-left:3px solid {CORES2[s]}"><div style="font-size:12px;font-weight:700;color:{NAVY}">{row["nome"]}</div><div style="font-size:10px;color:#888;margin-top:2px">{row["canal"]} · {row["interesse"]}</div>{"<div style=font-size:11px;color:"+GREEN+";font-weight:600;margin-top:3px>"+fmt(row["beneficio"])+"</div>" if row["beneficio"] else ""}</div>',unsafe_allow_html=True)
                    ns=st.selectbox("Mover para",STATUS,index=STATUS.index(s),key=f"ls{row['id']}",label_visibility="collapsed")
                    if ns!=s: upd_lead(row["id"],ns); st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
    else:
        st.info("Nenhum lead registrado.")

# ═══ CONTRATOS ═══
elif pg=="Contratos":
    st.markdown('<div class="page-header"><h2>📄 Contratos</h2><p>Carteira e comissões</p></div>',unsafe_allow_html=True)
    df_cli=load_clientes(); dfc=load_contratos()
    if not dfc.empty:
        tv=dfc["valor"].sum(); tc2=(tv*0.03)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(kpi("Carteira Total",fmt(tv),"","n"),unsafe_allow_html=True)
        with c2: st.markdown(kpi("Comissão Estimada",fmt(tc2),"3%","g"),unsafe_allow_html=True)
        with c3: st.markdown(kpi("Contratos",len(dfc),"","g"),unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)
    with st.expander("➕ Novo Contrato"):
        if df_cli.empty: st.warning("Cadastre um cliente primeiro.")
        else:
            with st.form("fct",clear_on_submit=True):
                cm={r["nome"]:r["id"] for _,r in df_cli.iterrows()}
                c1,c2=st.columns(2)
                with c1:
                    cs=st.selectbox("Cliente",list(cm.keys()))
                    bco=st.selectbox("Banco",["Banco BMG","Banco Safra","Banco PAN","Caixa","BRB","Facta","Itaú Consig."])
                    val=st.number_input("Valor (R$)",min_value=0.0,step=100.0)
                with c2:
                    pt=st.number_input("Parcelas",min_value=1,max_value=84,value=36,step=1)
                    tx2=st.number_input("Taxa (% a.m.)",min_value=0.5,max_value=5.0,value=1.8,step=0.1)
                    di=st.date_input("Data Início")
                if st.form_submit_button("✅ Registrar",use_container_width=True):
                    ins_ct({"cliente_id":cm[cs],"banco":bco,"valor":float(val),"parcelas_total":int(pt),"taxa_juros":float(tx2),"data_inicio":str(di)}); st.success("Contrato registrado!"); st.rerun()
    if not dfc.empty:
        dfc["parcela"]=dfc.apply(lambda r: round(r["valor"]*(r["taxa_juros"]/100*(1+r["taxa_juros"]/100)**r["parcelas_total"])/((1+r["taxa_juros"]/100)**r["parcelas_total"]-1),2) if r["parcelas_total"]>0 else 0,axis=1)
        dfc["comissao"]=(dfc["valor"]*0.03).round(2)
        st.markdown('<div class="chart-card"><div class="ct">Carteira de Contratos</div>',unsafe_allow_html=True)
        st.dataframe(dfc[["cliente_nome","banco","valor","parcelas_total","parcela","comissao","data_inicio"]].rename(columns={"cliente_nome":"Cliente","banco":"Banco","valor":"Valor","parcelas_total":"Parcelas","parcela":"Parcela/mês","comissao":"Comissão","data_inicio":"Início"}),use_container_width=True,hide_index=True)
        st.markdown('</div>',unsafe_allow_html=True)

# ═══ SIMULADOR ═══
elif pg=="Simulador":
    st.markdown('<div class="page-header"><h2>🧮 Simulador de Crédito</h2><p>Calcule margem e simule propostas</p></div>',unsafe_allow_html=True)
    tab1,tab2=st.tabs(["💳 Simulação","🔄 Portabilidade"])
    with tab1:
        c1,c2=st.columns([1,1.2])
        with c1:
            st.markdown("#### Dados do Cliente")
            ben2=st.number_input("Benefício (R$)",min_value=0.0,value=1412.0,step=50.0,key="sb")
            pa2=st.number_input("Parcelas Ativas (R$)",min_value=0.0,value=0.0,step=50.0,key="spa")
            mc=ben2*0.4; md=max(0,mc-pa2); pct2=min(100,round(pa2/mc*100,1)) if mc>0 else 0
            cor_md=GREEN if md>300 else YELLOW if md>0 else RED
            st.markdown(f"""<div style="background:white;border-radius:12px;padding:14px 16px;box-shadow:0 2px 6px rgba(0,0,0,0.05);margin-top:8px">
              <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #F5F5F5;font-size:12px"><span style="color:#888">Margem consignável (40%)</span><span style="font-weight:700;color:{NAVY}">{fmt(mc)}</span></div>
              <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #F5F5F5;font-size:12px"><span style="color:#888">Parcelas ativas</span><span style="font-weight:700;color:{RED}">{fmt(pa2)}</span></div>
              <div style="display:flex;justify-content:space-between;padding:5px 0;font-size:12px"><span style="color:#888">Margem disponível</span><span style="font-size:20px;font-weight:800;color:{cor_md}">{fmt(md)}</span></div>
              <div style="background:#F0F0F0;border-radius:99px;height:7px;margin-top:9px;overflow:hidden">
                <div style="background:{'#1A7A5E' if pct2<60 else '#F5A623' if pct2<90 else '#C0392B'};width:{pct2}%;height:100%;border-radius:99px"></div>
              </div>
              <div style="font-size:10px;color:#aaa;margin-top:3px">Comprometido: {pct2:.0f}%</div>
            </div>""",unsafe_allow_html=True)
        with c2:
            st.markdown("#### Simulação")
            val2=st.number_input("Valor desejado (R$)",min_value=0.0,value=3000.0,step=500.0,key="sv")
            pz=st.select_slider("Prazo",options=[12,24,36,48,60,72,84],value=36,key="spz")
            tx3=st.slider("Taxa (% a.m.)",0.5,3.5,1.8,0.1,key="stx")
            if val2>0 and ben2>0:
                r2=tx3/100; fat=(r2*(1+r2)**pz)/((1+r2)**pz-1)
                parc=val2*fat; tot=parc*pz; jur=tot-val2; cb=parc<=md
                cr=GREEN if cb else RED; msg="✅ Cabe na margem" if cb else "❌ Excede a margem"
                st.markdown(f"""<div style="background:white;border-radius:12px;padding:18px;box-shadow:0 2px 6px rgba(0,0,0,0.05);border-top:4px solid {cr}">
                  <div style="text-align:center;padding:10px 0 12px">
                    <div style="font-size:10px;color:#888;margin-bottom:4px">Parcela mensal</div>
                    <div style="font-size:30px;font-weight:800;color:{cr}">{fmt(parc)}</div>
                    <div style="font-size:11px;font-weight:700;color:{cr};margin-top:3px">{msg}</div>
                  </div>
                  <div style="display:flex;justify-content:space-between;padding:5px 0;border-top:1px solid #F5F5F5;font-size:12px"><span style="color:#888">Total a pagar</span><span style="font-weight:600">{fmt(tot)}</span></div>
                  <div style="display:flex;justify-content:space-between;padding:5px 0;border-top:1px solid #F5F5F5;font-size:12px"><span style="color:#888">Juros total</span><span style="font-weight:600;color:{RED}">{fmt(jur)}</span></div>
                  <div style="display:flex;justify-content:space-between;padding:5px 0;border-top:1px solid #F5F5F5;font-size:12px"><span style="color:#888">Comissão estimada</span><span style="font-weight:600;color:{GREEN}">{fmt(val2*0.03)}</span></div>
                </div>""",unsafe_allow_html=True)
        if val2>0 and ben2>0:
            st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
            st.markdown('<div class="chart-card"><div class="ct">Comparativo de Prazos</div>',unsafe_allow_html=True)
            pzs=[12,24,36,48,60,72,84]; r2=tx3/100
            pcs=[round(val2*(r2*(1+r2)**p)/((1+r2)**p-1),2) for p in pzs]
            fig5=go.Figure(go.Bar(x=[f"{p}m" for p in pzs],y=pcs,marker_color=[GREEN if p<=md else RED for p in pcs],marker_line_width=0,text=[fmt(p) for p in pcs],textposition="outside",textfont=dict(size=10)))
            fig5.add_hline(y=md,line_dash="dot",line_color=GREEN,line_width=2,annotation_text=f"Margem {fmt(md)}",annotation_font_size=10)
            fig5.update_layout(height=250,**plt_def())
            st.plotly_chart(fig5,use_container_width=True)
            st.markdown("🟢 Verde = cabe na margem &nbsp;&nbsp; 🔴 Vermelho = excede")
            st.markdown('</div>',unsafe_allow_html=True)
    with tab2:
        st.markdown("#### Calculadora de Portabilidade")
        c1,c2=st.columns(2)
        with c1:
            st.markdown("**Contrato Atual**")
            va=st.number_input("Saldo devedor (R$)",min_value=0.0,value=8000.0,step=100.0,key="pva")
            pra=st.number_input("Parcelas restantes",min_value=1,max_value=84,value=48,key="ppra")
            txa=st.number_input("Taxa atual (% a.m.)",min_value=0.1,max_value=5.0,value=2.1,step=0.1,key="ptxa")
        with c2:
            st.markdown("**Nova Proposta**")
            txn=st.number_input("Nova taxa (% a.m.)",min_value=0.1,max_value=5.0,value=1.7,step=0.1,key="ptxn")
            prn=st.number_input("Novo prazo (meses)",min_value=1,max_value=84,value=48,key="pprn")
        if va>0:
            ra=txa/100; rn=txn/100
            pca=va*(ra*(1+ra)**pra)/((1+ra)**pra-1)
            pcn=va*(rn*(1+rn)**prn)/((1+rn)**prn-1)
            eco=pca-pcn; ecot=pca*pra-pcn*prn; vale=eco>0; ce=GREEN if vale else RED
            st.markdown(f"""<div style="background:{'#E8F5F0' if vale else '#FDECEA'};border-radius:12px;padding:18px 22px;margin-top:14px;border:1px solid {'#B8DDD4' if vale else '#F5C6CB'}">
              <div style="font-size:13px;font-weight:800;color:{ce};margin-bottom:10px">{'✅ Portabilidade VALE A PENA' if vale else '❌ Portabilidade NÃO compensa'}</div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;text-align:center">
                {"".join([f'<div><div style="font-size:9px;color:#888;margin-bottom:2px">{l}</div><div style="font-size:16px;font-weight:700;color:{c2}">{v}</div></div>' for l,v,c2 in [("PARCELA ATUAL",fmt(pca),RED),("NOVA PARCELA",fmt(pcn),GREEN),("ECONOMIA/MÊS",fmt(abs(eco)),ce)]])}
              </div>
              <div style="text-align:center;margin-top:10px;font-size:12px;color:#555">Economia total: <strong style="color:{ce}">{fmt(abs(ecot))}</strong></div>
            </div>""",unsafe_allow_html=True)

# ═══ ALERTAS ═══
elif pg=="Alertas":
    st.markdown('<div class="page-header"><h2>🔔 Alertas de Oportunidade</h2><p>Radar inteligente por score de propensão</p></div>',unsafe_allow_html=True)
    df=load_clientes()
    if df.empty: st.info("Nenhum cliente cadastrado."); st.stop()
    opp=df[df["margem"]>300].sort_values("score",ascending=False)
    bx=df[(df["margem"]>0)&(df["margem"]<=300)].sort_values("score",ascending=False)
    sm=df[df["margem"]<=0]
    ph=df[(df["dias"].notna())&(df["dias"].astype(float)<=2)]
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(kpi("Prioridade Alta",len(opp),"margem>R$300","g"),unsafe_allow_html=True)
    with c2: st.markdown(kpi("Atenção",len(bx),"margem baixa","y"),unsafe_allow_html=True)
    with c3: st.markdown(kpi("Sem Margem",len(sm),"portabilidade","r"),unsafe_allow_html=True)
    with c4: st.markdown(kpi("INSS Hoje/Amanhã",len(ph),"urgente","y" if len(ph)>0 else "n"),unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
    if len(ph)>0:
        st.markdown(f"<div style='font-size:13px;font-weight:800;color:{RED};margin-bottom:8px'>🚨 INSS Hoje ou Amanhã</div>",unsafe_allow_html=True)
        for _,row in ph.iterrows():
            st.markdown(f'<div style="background:linear-gradient(135deg,#FFF9E6,#FFF0CC);border:1px solid {YELLOW};border-radius:12px;padding:14px 18px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center"><div><div style="font-size:14px;font-weight:800;color:{NAVY}">{row["nome"]}</div><div style="font-size:11px;color:#888">{row["tel_d"]} · {row["interesse"]}</div></div><div style="text-align:right"><div style="font-size:22px;font-weight:800;color:{RED}">{int(row["dias"])} dia(s)</div><div style="font-size:11px;color:#888">{row["prox"].strftime("%d/%m") if row["prox"] else ""}</div></div></div>',unsafe_allow_html=True)
    if len(opp)>0:
        st.markdown(f"<div style='font-size:13px;font-weight:800;color:{GREEN};margin:14px 0 8px'>🟢 Contatar Esta Semana — {len(opp)} cliente(s)</div>",unsafe_allow_html=True)
        for _,row in opp.iterrows():
            h=row["score"]>=75
            bg = "linear-gradient(135deg,#FFF9E6,#FFF0CC)" if h else "linear-gradient(135deg,#E8F5F0,#D4EDE6)"
            bc = "#F5A623" if h else "#B8DDD4"
            sc = row["score"]; sn = row["nome"]; st2 = row["status"]
            bd = badge("🔥 Máx","y") if h else badge("Oportunidade","g")
            st.markdown(f'<div style="background:{bg};border:1px solid {bc};border-radius:12px;padding:14px 18px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:flex-start"><div><div style="font-size:14px;font-weight:800;color:{NAVY}">{sn}</div><div style="font-size:11px;color:#888;margin:3px 0 6px">{row["tel_d"]} · {row["interesse"]} · {row["canal"]}</div><div>{bd} {badge(f"Score {sc}%","n")} {badge(st2,"b")}</div></div><div style="text-align:right"><div style="font-size:11px;color:#888">Margem disponível</div><div style="font-size:22px;font-weight:800;color:{GREEN}">{fmt(row["margem"])}</div></div></div>',unsafe_allow_html=True)
    if len(bx)>0:
        st.markdown(f"<div style='font-size:13px;font-weight:800;color:{YELLOW};margin:14px 0 8px'>🟡 Margem Baixa — {len(bx)}</div>",unsafe_allow_html=True)
        for _,row in bx.iterrows():
            st.markdown(f'<div style="background:white;border-radius:10px;padding:10px 14px;margin-bottom:6px;border-left:3px solid {YELLOW};box-shadow:0 1px 4px rgba(0,0,0,0.05);display:flex;justify-content:space-between"><span style="font-weight:700;color:{NAVY}">{row["nome"]}</span><span style="font-weight:600;color:{YELLOW}">{fmt(row["margem"])}</span></div>',unsafe_allow_html=True)
    if len(sm)>0:
        st.markdown(f"<div style='font-size:13px;font-weight:800;color:{RED};margin:14px 0 8px'>🔴 Sem Margem — Portabilidade — {len(sm)}</div>",unsafe_allow_html=True)
        for _,row in sm.iterrows():
            st.markdown(f'<div style="background:white;border-radius:10px;padding:10px 14px;margin-bottom:6px;border-left:3px solid {RED};box-shadow:0 1px 4px rgba(0,0,0,0.05);display:flex;justify-content:space-between"><span style="font-weight:700;color:{NAVY}">{row["nome"]}</span><span style="font-size:11px;color:{RED}">Verificar portabilidade</span></div>',unsafe_allow_html=True)

# ═══ AGENDA ═══
elif pg=="Agenda":
    st.markdown('<div class="page-header"><h2>📅 Agenda de Follow-ups</h2><p>Seus compromissos e lembretes</p></div>',unsafe_allow_html=True)
    dfa2=load_fu()
    if not dfa2.empty:
        dfa2["data_followup"]=pd.to_datetime(dfa2["data_followup"]).dt.date
        hoje2=date.today()
        venc=dfa2[dfa2["data_followup"]<hoje2].sort_values("data_followup")
        hj=dfa2[dfa2["data_followup"]==hoje2]
        prx=dfa2[dfa2["data_followup"]>hoje2].sort_values("data_followup")
        for titulo,grupo,cor in [("🚨 Vencidos",venc,RED),("📌 Hoje",hj,GREEN),("📆 Próximos",prx,NAVY)]:
            if len(grupo)==0: continue
            st.markdown(f"<div style='font-size:13px;font-weight:800;color:{cor};margin:12px 0 8px'>{titulo} — {len(grupo)}</div>",unsafe_allow_html=True)
            for _,r in grupo.iterrows():
                ca2,cb2=st.columns([4,1])
                with ca2:
                    st.markdown(f'<div style="background:{"#FDECEA" if cor==RED else "#E8F5F0" if cor==GREEN else "white"};border-radius:9px;padding:9px 13px;margin-bottom:5px;border-left:3px solid {cor}"><span style="font-weight:700;color:{NAVY}">{r["cliente_nome"]}</span><span style="font-size:10px;color:#888;margin-left:8px">{r["data_followup"].strftime("%d/%m/%Y") if cor!=GREEN else ""}</span><br><span style="font-size:11px;color:#555">{r["motivo"]}</span></div>',unsafe_allow_html=True)
                with cb2:
                    if st.button("✅",key=f"dfu{r['id']}"): del_fu(r["id"]); st.rerun()
    else:
        st.info("Nenhum follow-up agendado. Agende na aba Clientes.")

# ═══ EMAIL ═══
elif pg=="Email Marketing":
    st.markdown('<div class="page-header"><h2>📧 Email Marketing</h2><p>Campanhas via Brevo — 300 emails/dia gratuitos</p></div>',unsafe_allow_html=True)
    df=load_clientes()
    dce=df[df["email"].notna()&(df["email"]!="")] if not df.empty else pd.DataFrame()
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(kpi("Com Email",len(dce),"","n"),unsafe_allow_html=True)
    with c2: st.markdown(kpi("Emails/dia","300","plano grátis","g"),unsafe_allow_html=True)
    with c3: st.markdown(kpi("Custo","R$ 0,00","Brevo","g"),unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["📅 Calendário INSS","💡 Dica Financeira","📣 Campanha Livre"])
    with t1:
        st.markdown("Envia o próximo pagamento INSS personalizado para cada cliente.")
        if dce.empty: st.warning("Nenhum cliente com email cadastrado.")
        else:
            sel=st.multiselect("Selecionar clientes",dce["nome"].tolist(),default=dce["nome"].tolist())
            if st.button("📧 Enviar Calendário INSS",use_container_width=True):
                env=0
                for _,row in dce[dce["nome"].isin(sel)].iterrows():
                    pg3,dias3=prox_pg(row["cpf_raw"])
                    html=f'<div style="font-family:sans-serif;max-width:500px;margin:0 auto"><div style="background:{NAVY};padding:20px;border-radius:10px 10px 0 0"><h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:24px"><p>Olá <b>{row["nome"].split()[0]}</b>! Seu próximo INSS: <b style="color:{GREEN}">{pg3.strftime("%d/%m/%Y") if pg3 else "Em breve"}</b> {f"(em {dias3} dia(s))" if dias3 is not None else ""}.</p><a href="https://wa.me/5511952723015" style="background:{GREEN};color:white;padding:10px 20px;border-radius:99px;text-decoration:none">💬 Falar no WhatsApp</a></div></div>'
                    if send_email(row["email"],row["nome"],f"Seu INSS — Núcleo Crédito",html): env+=1
                st.success(f"✅ {env} email(s) enviado(s)!")
    with t2:
        DICAS=[("Proteja seu benefício","Nunca forneça sua senha do INSS por telefone. Golpistas fingem ser funcionários de bancos."),("Portabilidade pode economizar","Se sua taxa está acima de 2%, você pode migrar para uma menor sem custo algum."),("O que é margem consignável?","É o valor máximo que pode ser descontado do seu benefício — até 40% pelo INSS."),("Janeiro: melhor mês para crédito","O reajuste anual do INSS libera mais margem. Aproveite para conseguir condições melhores.")]
        ds=st.selectbox("Escolha a dica",[d[0] for d in DICAS])
        db=next(d[1] for d in DICAS if d[0]==ds)
        st.info(db)
        if not dce.empty:
            sel2=st.multiselect("Clientes",dce["nome"].tolist(),default=dce["nome"].tolist(),key="ds2")
            if st.button("📧 Enviar Dica",use_container_width=True):
                env2=0
                for _,row in dce[dce["nome"].isin(sel2)].iterrows():
                    html=f'<div style="font-family:sans-serif;max-width:500px;margin:0 auto"><div style="background:{NAVY};padding:20px;border-radius:10px 10px 0 0"><h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:24px"><p>Olá <b>{row["nome"].split()[0]}</b>!</p><div style="border-left:4px solid {GREEN};padding:12px 16px;background:#F8FFFE"><b style="color:{NAVY}">{ds}</b><p style="color:#555;margin-top:8px">{db}</p></div><a href="https://wa.me/5511952723015" style="display:inline-block;margin-top:16px;background:{GREEN};color:white;padding:10px 20px;border-radius:99px;text-decoration:none">💬 Tirar dúvidas</a></div></div>'
                    if send_email(row["email"],row["nome"],f"💡 {ds} — Núcleo Crédito",html): env2+=1
                st.success(f"✅ {env2} email(s) enviado(s)!")
    with t3:
        ca3=st.text_input("Assunto"); ct3=st.text_input("Título"); cc3=st.text_area("Mensagem",height=100)
        if not dce.empty:
            sel3=st.multiselect("Clientes",dce["nome"].tolist(),key="ds3")
            if st.button("📣 Enviar Campanha",use_container_width=True):
                if not ca3 or not cc3: st.error("Preencha assunto e mensagem.")
                else:
                    env3=0
                    for _,row in dce[dce["nome"].isin(sel3)].iterrows():
                        html=f'<div style="font-family:sans-serif;max-width:500px;margin:0 auto"><div style="background:{NAVY};padding:20px;border-radius:10px 10px 0 0"><h2 style="color:white;margin:0">⚛ Núcleo Crédito</h2></div><div style="background:white;padding:24px"><p>Olá <b>{row["nome"].split()[0]}</b>!</p><h3 style="color:{NAVY}">{ct3}</h3><p style="color:#555">{cc3}</p><a href="https://wa.me/5511952723015" style="background:{GREEN};color:white;padding:10px 20px;border-radius:99px;text-decoration:none">💬 WhatsApp</a></div></div>'
                        if send_email(row["email"],row["nome"],ca3,html): env3+=1
                    st.success(f"✅ {env3} email(s) enviado(s)!")

# ═══ METAS ═══
elif pg=="Metas":
    st.markdown('<div class="page-header"><h2>🎯 Painel de Metas</h2><p>Progresso mensal</p></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: mc2=st.number_input("Meta de contratos/mês",min_value=1,value=30,step=5)
    with c2: ml=st.number_input("Meta de leads/mês",min_value=1,value=50,step=5)
    with c3: mcm=st.number_input("Meta de comissão (R$)",min_value=0.0,value=3000.0,step=500.0)
    dfl2=load_leads(); dfc2=load_contratos()
    lm=len(dfl2); ctm=len(dfc2); com=dfc2["valor"].sum()*0.03 if not dfc2.empty else 0
    st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
    for lbl,atual,meta,cor2 in [("Contratos Fechados",ctm,mc2,GREEN),("Leads Gerados",lm,ml,NAVY),("Comissão (R$)",com,mcm,YELLOW)]:
        pct3=min(100,round(atual/meta*100,1)) if meta>0 else 0
        vf=fmt(atual) if "R$" in lbl else str(int(atual)); mf=fmt(meta) if "R$" in lbl else str(int(meta))
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:16px 18px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,0.05)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="font-size:13px;font-weight:700;color:{NAVY}">{lbl}</span>
            <span style="font-size:12px;color:#888">{vf} / {mf} ({pct3}%)</span>
          </div>
          <div style="background:#F0F0F0;border-radius:99px;height:10px;overflow:hidden">
            <div style="background:{cor2};width:{pct3}%;height:100%;border-radius:99px"></div>
          </div>
          <div style="font-size:10px;color:{'#1A7A5E' if pct3>=100 else '#888'};margin-top:5px">{'🎉 Meta atingida!' if pct3>=100 else f'Faltam {mf if "R$" in lbl else str(int(meta-atual))} para a meta'}</div>
        </div>""",unsafe_allow_html=True)

st.markdown('</div>',unsafe_allow_html=True)
