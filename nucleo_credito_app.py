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
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Núcleo Crédito",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

NAVY   = "#1B3A6B"
GREEN  = "#1A7A5E"
RED    = "#C0392B"
YELLOW = "#F5A623"
WHITE  = "#FFFFFF"
LIGHT  = "#F0F4F8"

# ══════════════════════════════════════════════════════════════════════════
# CSS PREMIUM
# ══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
* {{ font-family: 'Montserrat', sans-serif !important; }}
.main {{ background: {LIGHT}; }}
[data-testid="stSidebarContent"] {{
    background: linear-gradient(180deg, {NAVY} 0%, #0F2347 100%);
}}
.nc-logo {{
    text-align:center; padding:28px 16px 20px;
    border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:16px;
}}
.nc-logo .atom {{ font-size:40px; }}
.nc-logo h1 {{ color:white; font-size:19px; font-weight:800; margin:8px 0 4px; letter-spacing:-0.5px; }}
.nc-logo p {{ color:rgba(255,255,255,0.45); font-size:10px; font-style:italic; margin:0; }}
.page-header {{
    background:white; border-radius:16px; padding:20px 24px;
    margin-bottom:20px; border-left:4px solid {GREEN};
    box-shadow:0 2px 10px rgba(0,0,0,0.06);
}}
.page-header h2 {{ color:{NAVY}; font-size:20px; font-weight:800; margin:0 0 4px; }}
.page-header p {{ color:#777; font-size:13px; margin:0; }}
.kpi-card {{
    background:white; border-radius:14px; padding:18px 16px;
    box-shadow:0 2px 8px rgba(0,0,0,0.06);
    border-top:3px solid {GREEN}; text-align:center;
}}
.kpi-card.navy {{ border-top-color:{NAVY}; }}
.kpi-card.red   {{ border-top-color:{RED}; }}
.kpi-card.yellow {{ border-top-color:{YELLOW}; }}
.kpi-label {{ font-size:10px; color:#999; text-transform:uppercase; letter-spacing:.07em; font-weight:700; margin-bottom:6px; }}
.kpi-value {{ font-size:26px; font-weight:800; color:{NAVY}; line-height:1; }}
.kpi-sub   {{ font-size:10px; color:#bbb; margin-top:5px; }}
.chart-card {{
    background:white; border-radius:14px; padding:20px;
    box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:16px;
}}
.chart-title {{ font-size:13px; font-weight:700; color:{NAVY}; margin-bottom:14px;
    padding-bottom:10px; border-bottom:1px solid #F0F0F0; }}
.client-card {{
    background:white; border-radius:14px; padding:16px 20px;
    margin-bottom:10px; box-shadow:0 2px 6px rgba(0,0,0,0.05);
    border-left:4px solid #E0E0E0;
}}
.client-card.opp  {{ border-left-color:{GREEN}; }}
.client-card.warn {{ border-left-color:{YELLOW}; }}
.client-card.red  {{ border-left-color:{RED}; }}
.badge {{ display:inline-block; padding:3px 10px; border-radius:99px; font-size:10px; font-weight:700; margin-right:3px; }}
.bg   {{ background:#E8F5F0; color:#0F6E56; }}
.by   {{ background:#FFF3CD; color:#856404; }}
.br   {{ background:#FDECEA; color:#A32D2D; }}
.bb   {{ background:#E6F1FB; color:#185FA5; }}
.bn   {{ background:#EBF0F8; color:{NAVY}; }}
.alert-box {{
    background:linear-gradient(135deg,#E8F5F0,#D4EDE6);
    border:1px solid #B8DDD4; border-radius:14px; padding:16px 20px; margin-bottom:10px;
}}
.alert-box.high {{
    background:linear-gradient(135deg,#FFF9E6,#FFF0CC);
    border-color:#F5A623;
}}
.login-wrap {{
    max-width:380px; margin:60px auto; background:white;
    border-radius:20px; padding:40px 36px;
    box-shadow:0 8px 40px rgba(0,0,0,0.12); text-align:center;
}}
.stButton>button {{
    background:{NAVY}; color:white; border:none; border-radius:10px;
    padding:10px 20px; font-family:'Montserrat',sans-serif;
    font-weight:700; font-size:13px; width:100%;
    transition:all .2s;
}}
.stButton>button:hover {{ background:#152d54; transform:translateY(-1px); box-shadow:0 4px 14px rgba(27,58,107,0.3); }}
footer,#MainMenu,header {{ display:none !important; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# CREDENCIAIS (via secrets ou env)
# ══════════════════════════════════════════════════════════════════════════
def get_secret(key, default=""):
    try:
        val = st.secrets.get(key, None)
        if val:
            return val
    except:
        pass
    return os.environ.get(key, default)

SUPABASE_URL  = get_secret("SUPABASE_URL",  "https://vvroaokekxbttapefspw.supabase.co")
SUPABASE_KEY  = get_secret("SUPABASE_KEY",  "sb_publishable_OnL6QmmZGnIAGh5IB5TFXQ_tsVn_qK4")
BREVO_API_KEY = get_secret("BREVO_API_KEY", "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")
SENDER_EMAIL  = get_secret("SENDER_EMAIL",  "nucleocastelo.credito@gmail.com")
SENDER_NAME   = get_secret("SENDER_NAME",   "Núcleo Crédito")

# ══════════════════════════════════════════════════════════════════════════
# SUPABASE
# ══════════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_supabase():
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

sb = get_supabase()

# ══════════════════════════════════════════════════════════════════════════
# CRIPTOGRAFIA
# ══════════════════════════════════════════════════════════════════════════
def _fernet():
    raw = get_secret("ENCRYPT_KEY", "")
    if raw:
        return Fernet(raw.encode())
    key = base64.urlsafe_b64encode(hashlib.sha256(b"nucleo_credito_2026_secure").digest())
    return Fernet(key)

def encrypt(text):
    if not text: return ""
    try: return _fernet().encrypt(str(text).encode()).decode()
    except: return text

def decrypt(text):
    if not text: return ""
    try: return _fernet().decrypt(str(text).encode()).decode()
    except: return text

def mask_cpf(cpf):
    c = "".join(filter(str.isdigit, cpf or ""))
    return f"***.{c[3:6]}.{c[6:9]}-**" if len(c) == 11 else "***.***.***-**"

def mask_phone(phone):
    d = "".join(filter(str.isdigit, phone or ""))
    return f"({d[:2]}) *****-{d[-4:]}" if len(d) >= 8 else "(**)*****-****"

# ══════════════════════════════════════════════════════════════════════════
# CALENDÁRIO INSS 2026 (completo)
# ══════════════════════════════════════════════════════════════════════════
INSS_2026 = {
    "ate1sm": {
        1: {"jan":"2026-01-26","fev":"2026-02-23","mar":"2026-03-25","abr":"2026-04-24",
            "mai":"2026-05-25","jun":"2026-06-24","jul":"2026-07-24","ago":"2026-08-24",
            "set":"2026-09-24","out":"2026-10-26","nov":"2026-11-24","dez":"2026-12-22"},
        2: {"jan":"2026-01-27","fev":"2026-02-24","mar":"2026-03-26","abr":"2026-04-27",
            "mai":"2026-05-26","jun":"2026-06-25","jul":"2026-07-28","ago":"2026-08-26",
            "set":"2026-09-25","out":"2026-10-27","nov":"2026-11-25","dez":"2026-12-23"},
        3: {"jan":"2026-01-28","fev":"2026-02-25","mar":"2026-03-27","abr":"2026-04-28",
            "mai":"2026-05-27","jun":"2026-06-26","jul":"2026-07-29","ago":"2026-08-27",
            "set":"2026-09-28","out":"2026-10-28","nov":"2026-11-26","dez":"2026-12-24"},
        4: {"jan":"2026-01-29","fev":"2026-02-26","mar":"2026-03-30","abr":"2026-04-29",
            "mai":"2026-05-28","jun":"2026-06-29","jul":"2026-07-30","ago":"2026-08-28",
            "set":"2026-09-29","out":"2026-10-29","nov":"2026-11-27","dez":"2026-12-29"},
        5: {"jan":"2026-01-30","fev":"2026-02-27","mar":"2026-03-31","abr":"2026-04-30",
            "mai":"2026-05-29","jun":"2026-06-30","jul":"2026-07-31","ago":"2026-08-31",
            "set":"2026-09-30","out":"2026-10-30","nov":"2026-11-30","dez":"2026-12-30"},
        6: {"jan":"2026-02-02","fev":"2026-03-02","mar":"2026-04-01","abr":"2026-05-04",
            "mai":"2026-06-01","jun":"2026-07-01","jul":"2026-08-03","ago":"2026-09-01",
            "set":"2026-10-01","out":"2026-11-02","nov":"2026-12-01","dez":"2026-12-30"},
        7: {"jan":"2026-02-03","fev":"2026-03-03","mar":"2026-04-02","abr":"2026-05-05",
            "mai":"2026-06-02","jun":"2026-07-02","jul":"2026-08-04","ago":"2026-09-02",
            "set":"2026-10-02","out":"2026-11-04","nov":"2026-12-02","dez":"2026-12-30"},
        8: {"jan":"2026-02-05","fev":"2026-03-05","mar":"2026-04-02","abr":"2026-05-06",
            "mai":"2026-06-03","jun":"2026-07-03","jul":"2026-08-05","ago":"2026-09-03",
            "set":"2026-10-05","out":"2026-11-05","nov":"2026-12-03","dez":"2026-12-30"},
        9: {"jan":"2026-02-07","fev":"2026-03-07","mar":"2026-04-07","abr":"2026-05-07",
            "mai":"2026-06-05","jun":"2026-07-06","jul":"2026-08-06","ago":"2026-09-04",
            "set":"2026-10-06","out":"2026-11-06","nov":"2026-12-04","dez":"2026-12-30"},
        0: {"jan":"2026-02-08","fev":"2026-03-08","mar":"2026-04-08","abr":"2026-05-08",
            "mai":"2026-06-06","jun":"2026-07-07","jul":"2026-08-07","ago":"2026-09-08",
            "set":"2026-10-07","out":"2026-11-09","nov":"2026-12-05","dez":"2026-12-30"},
    }
}

MESES = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

def get_proximo_pagamento(cpf_raw, beneficio):
    try:
        cpf_digits = "".join(filter(str.isdigit, cpf_raw or ""))
        if not cpf_digits: return None, None
        ultimo = int(cpf_digits[-1])
        hoje = date.today()
        mes_atual = MESES[hoje.month - 1]
        tabela = INSS_2026["ate1sm"]
        if ultimo in tabela and mes_atual in tabela[ultimo]:
            data_str = tabela[ultimo][mes_atual]
            data_pg = datetime.strptime(data_str, "%Y-%m-%d").date()
            if data_pg < hoje:
                prox_mes_idx = hoje.month % 12
                prox_mes = MESES[prox_mes_idx]
                if prox_mes in tabela[ultimo]:
                    data_str = tabela[ultimo][prox_mes]
                    data_pg = datetime.strptime(data_str, "%Y-%m-%d").date()
            dias = (data_pg - hoje).days
            return data_pg, dias
    except:
        pass
    return None, None

# ══════════════════════════════════════════════════════════════════════════
# SCORE DE PROPENSÃO
# ══════════════════════════════════════════════════════════════════════════
def calcular_score(row):
    score = 0
    margem = row.get("margem", 0)
    status = row.get("status", "")
    canal  = row.get("canal", "")

    if margem > 600:   score += 40
    elif margem > 300: score += 30
    elif margem > 100: score += 15
    else:              score += 0

    status_pts = {"Ativo":20,"Lead Quente":25,"Em análise":15}
    score += status_pts.get(status, 0)

    canal_pts = {"Indicação":20,"WhatsApp":15,"Rádio":12,"Panfletagem":10,"Google":12,"Instagram":8}
    score += canal_pts.get(canal, 5)

    _, dias = get_proximo_pagamento(row.get("cpf_raw",""), row.get("beneficio",0))
    if dias is not None:
        if 0 <= dias <= 2:   score += 15
        elif 3 <= dias <= 5: score += 10

    return min(score, 100)

def score_label(score):
    if score >= 75: return "🔥 Altíssima", RED
    if score >= 55: return "⚡ Alta", YELLOW
    if score >= 35: return "📈 Média", NAVY
    return "💤 Baixa", "#AAA"

# ══════════════════════════════════════════════════════════════════════════
# BREVO — EMAIL
# ══════════════════════════════════════════════════════════════════════════
def send_email(to_email, to_name, subject, html_content):
    try:
        config = sib_api_v3_sdk.Configuration()
        config.api_key["api-key"] = BREVO_API_KEY
        api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(config))
        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email, "name": to_name}],
            sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
            subject=subject,
            html_content=html_content
        )
        api.send_transac_email(email)
        return True
    except ApiException as e:
        st.error(f"Erro ao enviar email: {e}")
        return False

def email_calendario_inss(nome, email, cpf_raw, beneficio):
    data_pg, dias = get_proximo_pagamento(cpf_raw, beneficio)
    data_fmt = data_pg.strftime("%d/%m/%Y") if data_pg else "Em breve"
    html = f"""
    <div style="font-family:Montserrat,Arial,sans-serif;max-width:600px;margin:0 auto">
      <div style="background:#1B3A6B;padding:28px 32px;border-radius:12px 12px 0 0">
        <h1 style="color:white;font-size:22px;margin:0">⚛ Núcleo Crédito</h1>
        <p style="color:rgba(255,255,255,0.6);font-size:12px;margin:6px 0 0;font-style:italic">No centro da sua vida financeira.</p>
      </div>
      <div style="background:white;padding:28px 32px">
        <p style="font-size:16px;color:#333">Olá, <strong>{nome.split()[0]}</strong>!</p>
        <p style="font-size:14px;color:#555;line-height:1.6">
          Seu próximo pagamento do INSS está chegando.<br>
          Separamos essa informação para você se planejar.
        </p>
        <div style="background:#E8F5F0;border-radius:12px;padding:20px;margin:20px 0;text-align:center">
          <p style="font-size:12px;color:#0F6E56;margin:0 0 6px;font-weight:700;text-transform:uppercase;letter-spacing:.06em">Próximo Pagamento</p>
          <p style="font-size:28px;font-weight:800;color:#1B3A6B;margin:0">{data_fmt}</p>
          {f'<p style="font-size:13px;color:#1A7A5E;margin:6px 0 0">Em {dias} dia(s)</p>' if dias is not None else ''}
        </div>
        <div style="background:#F8F9FA;border-radius:12px;padding:16px 20px;margin:16px 0">
          <p style="font-size:13px;color:#333;margin:0 0 8px;font-weight:600">💡 Dica de segurança</p>
          <p style="font-size:13px;color:#555;margin:0;line-height:1.5">
            Fique atento a ligações suspeitas pedindo dados pessoais ou senhas do seu benefício.
            O Núcleo Crédito <strong>nunca pede sua senha</strong>.<br>
            Em caso de dúvida, nos contate diretamente: <strong>(11) 95272-3015</strong>
          </p>
        </div>
        <p style="font-size:13px;color:#555;line-height:1.5">
          Tem dúvidas sobre seu crédito consignado? Nossa equipe está pronta para te atender
          com transparência e sem burocracia.
        </p>
        <div style="text-align:center;margin:24px 0">
          <a href="https://wa.me/5511952723015" style="background:#1A7A5E;color:white;padding:12px 28px;border-radius:99px;text-decoration:none;font-weight:700;font-size:14px">
            💬 Falar no WhatsApp
          </a>
        </div>
      </div>
      <div style="background:#F0F4F8;padding:16px 32px;border-radius:0 0 12px 12px;text-align:center">
        <p style="font-size:11px;color:#aaa;margin:0">
          Núcleo Crédito &nbsp;·&nbsp; (11) 95272-3015 &nbsp;·&nbsp; @nucleocredito<br>
          <a href="#" style="color:#aaa;font-size:10px">Cancelar inscrição</a>
        </p>
      </div>
    </div>
    """
    return send_email(email, nome, f"⚛ Seu INSS cai em {data_fmt} — Núcleo Crédito", html)

def email_dica_financeira(nome, email, dica_titulo, dica_corpo):
    html = f"""
    <div style="font-family:Montserrat,Arial,sans-serif;max-width:600px;margin:0 auto">
      <div style="background:#1B3A6B;padding:28px 32px;border-radius:12px 12px 0 0">
        <h1 style="color:white;font-size:22px;margin:0">⚛ Núcleo Crédito</h1>
        <p style="color:rgba(255,255,255,0.6);font-size:12px;margin:6px 0 0;font-style:italic">No centro da sua vida financeira.</p>
      </div>
      <div style="background:white;padding:28px 32px">
        <p style="font-size:16px;color:#333">Olá, <strong>{nome.split()[0]}</strong>!</p>
        <div style="border-left:4px solid #1A7A5E;padding:16px 20px;margin:16px 0;background:#F8FFFE">
          <p style="font-size:15px;font-weight:700;color:#1B3A6B;margin:0 0 8px">💡 {dica_titulo}</p>
          <p style="font-size:14px;color:#555;margin:0;line-height:1.6">{dica_corpo}</p>
        </div>
        <div style="text-align:center;margin:24px 0">
          <a href="https://wa.me/5511952723015" style="background:#1A7A5E;color:white;padding:12px 28px;border-radius:99px;text-decoration:none;font-weight:700;font-size:14px">
            💬 Tirar dúvidas no WhatsApp
          </a>
        </div>
      </div>
      <div style="background:#F0F4F8;padding:16px 32px;border-radius:0 0 12px 12px;text-align:center">
        <p style="font-size:11px;color:#aaa;margin:0">Núcleo Crédito &nbsp;·&nbsp; (11) 95272-3015</p>
      </div>
    </div>
    """
    return send_email(email, nome, f"💡 {dica_titulo} — Núcleo Crédito", html)

# ══════════════════════════════════════════════════════════════════════════
# BANCO DE DADOS
# ══════════════════════════════════════════════════════════════════════════
def load_clientes():
    try:
        r = sb.table("clientes").select("*").order("created_at", desc=True).execute()
        if not r.data: return pd.DataFrame()
        df = pd.DataFrame(r.data)
        df["cpf_raw"]     = df["cpf"].apply(lambda x: decrypt(x) if x else "")
        df["tel_raw"]     = df["telefone"].apply(lambda x: decrypt(x) if x else "")
        df["cpf_display"] = df["cpf_raw"].apply(mask_cpf)
        df["tel_display"] = df["tel_raw"].apply(mask_phone)
        df["margem"]      = df.apply(lambda r: round(r["beneficio"]*0.4 - r["parcelas"], 2), axis=1)
        df["pct_comp"]    = df.apply(lambda r: min(100, round(r["parcelas"]/(r["beneficio"]*0.4)*100,1)) if r["beneficio"]>0 else 0, axis=1)
        df["score"]       = df.apply(calcular_score, axis=1)
        df["prox_pg"], df["dias_pg"] = zip(*df.apply(lambda r: get_proximo_pagamento(r["cpf_raw"], r["beneficio"]), axis=1))
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

def load_leads():
    try:
        r = sb.table("leads").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except: return pd.DataFrame()

def load_contratos():
    try:
        r = sb.table("contratos").select("*, clientes(nome)").order("created_at", desc=True).execute()
        if not r.data: return pd.DataFrame()
        df = pd.DataFrame(r.data)
        df["cliente_nome"] = df["clientes"].apply(lambda x: x["nome"] if isinstance(x, dict) else "")
        return df
    except: return pd.DataFrame()

def load_historico(cliente_id):
    try:
        r = sb.table("historico").select("*").eq("cliente_id", cliente_id).order("created_at", desc=True).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except: return pd.DataFrame()

def load_followups():
    try:
        r = sb.table("followups").select("*, clientes(nome)").order("data_followup").execute()
        if not r.data: return pd.DataFrame()
        df = pd.DataFrame(r.data)
        df["cliente_nome"] = df["clientes"].apply(lambda x: x["nome"] if isinstance(x, dict) else "")
        return df
    except: return pd.DataFrame()

def insert_cliente(data):
    data["cpf"]      = encrypt(data.get("cpf",""))
    data["telefone"] = encrypt(data.get("telefone",""))
    return sb.table("clientes").insert(data).execute()

def insert_lead(data):     return sb.table("leads").insert(data).execute()
def insert_historico(data): return sb.table("historico").insert(data).execute()
def insert_followup(data):  return sb.table("followups").insert(data).execute()
def insert_contrato(data):  return sb.table("contratos").insert(data).execute()

def update_lead_status(id, status):
    return sb.table("leads").update({"status": status}).eq("id", id).execute()

def delete_cliente(id):
    sb.table("historico").delete().eq("cliente_id", id).execute()
    sb.table("followups").delete().eq("cliente_id", id).execute()
    return sb.table("clientes").delete().eq("id", id).execute()

def delete_followup(id):
    return sb.table("followups").delete().eq("id", id).execute()

# ══════════════════════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════════════
USERS = {
    "eduardo": {
        "pwd": hashlib.sha256(b"nucleo2026").hexdigest(),
        "name": "Eduardo Lima de Sousa",
        "role": "admin"
    }
}

def check_pwd(user, pwd):
    u = USERS.get(user.lower())
    if not u: return False
    return hmac.compare_digest(u["pwd"], hashlib.sha256(pwd.encode()).hexdigest())

def login_screen():
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown(f"""
        <div class="login-wrap">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px">
            <ellipse cx="32" cy="32" rx="28" ry="11" stroke="#1A7A5E" stroke-width="1.8" fill="none"/>
            <ellipse cx="32" cy="32" rx="28" ry="11" stroke="#1A7A5E" stroke-width="1.8" fill="none" transform="rotate(60 32 32)"/>
            <ellipse cx="32" cy="32" rx="28" ry="11" stroke="#1A7A5E" stroke-width="1.8" fill="none" transform="rotate(120 32 32)"/>
            <circle cx="32" cy="32" r="5" fill="#1A7A5E"/>
            <circle cx="32" cy="32" r="2" fill="white"/>
            <circle cx="60" cy="32" r="2.5" fill="#1A7A5E"/>
            <circle cx="4" cy="32" r="2.5" fill="#1A7A5E"/>
            <circle cx="46" cy="9" r="2.5" fill="#1A7A5E"/>
            <circle cx="18" cy="55" r="2.5" fill="#1A7A5E"/>
          </svg>
          <div style="font-size:24px;font-weight:800;color:{NAVY};letter-spacing:-0.5px;margin:4px 0 2px">Núcleo <span style="color:#1A7A5E">Crédito</span></div>
          <p style="color:#999;font-size:12px;font-style:italic;margin-bottom:28px">No centro da sua vida financeira.</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            st.markdown("#### Acesse o sistema")
            user = st.text_input("Usuário", placeholder="usuário")
            pwd  = st.text_input("Senha", type="password", placeholder="••••••••")
            if st.form_submit_button("Entrar", width="stretch"):
                if check_pwd(user, pwd):
                    st.session_state.logged_in = True
                    st.session_state.username  = user
                    st.session_state.user_name = USERS[user.lower()]["name"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        st.markdown(f"<p style='text-align:center;font-size:10px;color:#ccc;margin-top:12px'>Sistema seguro · LGPD · Dados criptografados</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# HELPERS UI
# ══════════════════════════════════════════════════════════════════════════
def fmt(v):
    return f"R$ {abs(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")

def kpi(label, value, sub="", color="green"):
    cc = {"navy":"navy","red":"red","yellow":"yellow"}.get(color,"")
    return f'<div class="kpi-card {cc}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{"<div class=kpi-sub>"+sub+"</div>" if sub else ""}</div>'

def badge(text, color):
    cls = {"green":"bg","yellow":"by","red":"br","blue":"bb","navy":"bn"}.get(color,"bb")
    return f'<span class="badge {cls}">{text}</span>'

def plotly_defaults():
    return dict(plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=0,r=10,t=10,b=0),
                font=dict(family="Montserrat"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#F5F5F5"))

# ══════════════════════════════════════════════════════════════════════════
# INIT SESSION
# ══════════════════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="nc-logo">
      <div style="position:relative;display:inline-block;margin-bottom:8px">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="32" cy="32" rx="28" ry="11" stroke="#1A7A5E" stroke-width="1.8" fill="none" opacity="0.9"/>
          <ellipse cx="32" cy="32" rx="28" ry="11" stroke="#1A7A5E" stroke-width="1.8" fill="none" opacity="0.9" transform="rotate(60 32 32)"/>
          <ellipse cx="32" cy="32" rx="28" ry="11" stroke="#1A7A5E" stroke-width="1.8" fill="none" opacity="0.9" transform="rotate(120 32 32)"/>
          <circle cx="32" cy="32" r="5" fill="#1A7A5E" opacity="0.95"/>
          <circle cx="32" cy="32" r="2" fill="white"/>
          <circle cx="60" cy="32" r="2.5" fill="#1A7A5E" opacity="0.8"/>
          <circle cx="4" cy="32" r="2.5" fill="#1A7A5E" opacity="0.8"/>
          <circle cx="46" cy="9" r="2.5" fill="#1A7A5E" opacity="0.8"/>
          <circle cx="18" cy="55" r="2.5" fill="#1A7A5E" opacity="0.8"/>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </svg>
      </div>
      <div style="color:white;font-size:22px;font-weight:800;letter-spacing:-0.5px;line-height:1">Núcleo</div>
      <div style="color:#1A7A5E;font-size:11px;font-weight:600;letter-spacing:0.35em;margin-top:1px">CRÉDITO</div>
      <div style="color:rgba(255,255,255,0.4);font-size:10px;font-style:italic;margin-top:8px">No centro da sua vida financeira.</div>
    </div>""", unsafe_allow_html=True)

    menu = st.radio("Menu", [
        "📊  Dashboard",
        "👥  Clientes",
        "📋  Leads",
        "📄  Contratos",
        "🧮  Simulador",
        "🔔  Alertas",
        "📅  Agenda",
        "📧  Email Marketing",
        "🎯  Metas",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div style="padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;margin:0 6px">
      <div style="color:white;font-size:13px;font-weight:700">{st.session_state.user_name.split()[0]}</div>
      <div style="color:rgba(255,255,255,0.45);font-size:10px">Administrador</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown(f"<div style='text-align:center;margin-top:12px'><span style='color:rgba(255,255,255,0.25);font-size:9px'>{date.today().strftime('%d/%m/%Y')}</span></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
if "Dashboard" in menu:
    st.markdown('<div class="page-header"><h2>📊 Dashboard de Performance</h2><p>Visão geral da operação em tempo real</p></div>', unsafe_allow_html=True)

    df  = load_clientes()
    dfl = load_leads()
    dfc = load_contratos()
    dfa = load_followups()

    total_cli    = len(df)
    ativos       = len(df[df["status"]=="Ativo"]) if not df.empty else 0
    marg_tot     = df["margem"].clip(lower=0).sum() if not df.empty else 0
    opp          = len(df[df["margem"]>300]) if not df.empty else 0
    total_leads  = len(dfl)
    conv         = len(dfl[dfl["status"]=="Convertido"]) if not dfl.empty else 0
    taxa_conv    = round(conv/total_leads*100,1) if total_leads>0 else 0
    carteira     = dfc["valor"].sum() if not dfc.empty else 0
    comissao     = carteira * 0.03

    followups_hoje = 0
    if not dfa.empty:
        dfa["data_followup"] = pd.to_datetime(dfa["data_followup"]).dt.date
        followups_hoje = len(dfa[dfa["data_followup"] == date.today()])

    cols = st.columns(8)
    dados_kpi = [
        ("Clientes", total_cli, "", "navy"),
        ("Ativos", ativos, "", "green"),
        ("Margem Total", fmt(marg_tot), "disponível", "green"),
        ("Oportunidades", opp, ">R$300", "yellow"),
        ("Leads", total_leads, "", "navy"),
        ("Conversão", f"{taxa_conv}%", f"{conv} fechados", "green"),
        ("Carteira", fmt(carteira), "contratos", "navy"),
        ("Agenda Hoje", followups_hoje, "follow-ups", "yellow" if followups_hoje>0 else "navy"),
    ]
    for col, (lbl, val, sub, cor) in zip(cols, dados_kpi):
        with col:
            st.markdown(kpi(lbl, val, sub, cor), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-card"><div class="chart-title">🎯 Score de Propensão por Cliente</div>', unsafe_allow_html=True)
            df_score = df.sort_values("score", ascending=True)
            cores_score = [GREEN if s>=75 else YELLOW if s>=55 else NAVY if s>=35 else "#CCC" for s in df_score["score"]]
            fig = go.Figure(go.Bar(
                x=df_score["score"],
                y=df_score["nome"].str.split().str[:2].str.join(" "),
                orientation="h",
                marker_color=cores_score,
                marker_line_width=0,
                text=[f"{s}%" for s in df_score["score"]],
                textposition="outside"
            ))
            fig.update_layout(height=260, xaxis=dict(range=[0,115], showgrid=True, gridcolor="#F5F5F5"), **{k:v for k,v in plotly_defaults().items() if k!="xaxis"})
            st.plotly_chart(fig, width="stretch")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-card"><div class="chart-title">💰 Margem Disponível por Cliente</div>', unsafe_allow_html=True)
            df_m = df.sort_values("margem", ascending=True)
            cores_m = [GREEN if m>300 else YELLOW if m>0 else RED for m in df_m["margem"]]
            fig2 = go.Figure(go.Bar(
                x=df_m["margem"],
                y=df_m["nome"].str.split().str[:2].str.join(" "),
                orientation="h",
                marker_color=cores_m,
                marker_line_width=0,
                text=[fmt(m) for m in df_m["margem"]],
                textposition="outside"
            ))
            fig2.add_vline(x=300, line_dash="dot", line_color=GREEN, line_width=1.5)
            fig2.update_layout(height=260, **plotly_defaults())
            st.plotly_chart(fig2, width="stretch")
            st.markdown('</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            if not dfl.empty:
                st.markdown('<div class="chart-card"><div class="chart-title">📋 Pipeline por Canal</div>', unsafe_allow_html=True)
                cc = dfl["canal"].value_counts().reset_index()
                cc.columns = ["Canal","Leads"]
                fig3 = px.bar(cc, x="Canal", y="Leads", color_discrete_sequence=[NAVY], text="Leads")
                fig3.update_traces(textposition="outside", marker_line_width=0)
                fig3.update_layout(height=240, **plotly_defaults())
                st.plotly_chart(fig3, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            if not dfl.empty:
                st.markdown('<div class="chart-card"><div class="chart-title">🔄 Status do Pipeline</div>', unsafe_allow_html=True)
                sc = dfl["status"].value_counts().reset_index()
                sc.columns = ["Status","Qtd"]
                fig4 = px.pie(sc, values="Qtd", names="Status",
                    color_discrete_sequence=[GREEN,YELLOW,NAVY,RED], hole=0.6)
                fig4.update_traces(textinfo="percent+label", textfont_size=11)
                fig4.update_layout(height=240, showlegend=False, paper_bgcolor="white",
                    margin=dict(l=0,r=0,t=0,b=0), font=dict(family="Montserrat"))
                st.plotly_chart(fig4, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)

        # Pagamentos próximos
        df_pg = df[df["dias_pg"].notna()].copy()
        df_pg["dias_pg"] = df_pg["dias_pg"].astype(int)
        df_urgente = df_pg[df_pg["dias_pg"] <= 5].sort_values("dias_pg")
        if len(df_urgente) > 0:
            st.markdown('<div class="chart-card"><div class="chart-title">🗓️ Pagamentos INSS nos Próximos 5 Dias</div>', unsafe_allow_html=True)
            for _, r in df_urgente.iterrows():
                cor = RED if r["dias_pg"]<=1 else YELLOW if r["dias_pg"]<=3 else GREEN
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F5F5F5">
                  <div>
                    <span style="font-weight:700;color:{NAVY};font-size:14px">{r['nome'].split()[0]} {r['nome'].split()[1] if len(r['nome'].split())>1 else ''}</span>
                    <span style="font-size:12px;color:#888;margin-left:8px">{r['tel_display']}</span>
                  </div>
                  <div style="text-align:right">
                    <span style="font-weight:700;color:{cor};font-size:14px">{r['prox_pg'].strftime('%d/%m') if r['prox_pg'] else ''}</span>
                    <span style="font-size:11px;color:#aaa;margin-left:6px">em {r['dias_pg']} dia(s)</span>
                  </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado. Vá para a aba Clientes para começar.")

# ══════════════════════════════════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════════════════════════════════
elif "Clientes" in menu:
    st.markdown('<div class="page-header"><h2>👥 Gestão de Clientes</h2><p>Base segura com dados criptografados — LGPD</p></div>', unsafe_allow_html=True)

    with st.expander("➕ Cadastrar Novo Cliente"):
        with st.form("form_cli", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nome      = st.text_input("Nome Completo *")
                cpf       = st.text_input("CPF (criptografado)")
                telefone  = st.text_input("Telefone (criptografado)")
                email_cli = st.text_input("Email (para mailing)")
                data_nasc = st.date_input("Data Nascimento", value=date(1960,1,1), min_value=date(1930,1,1), max_value=date(2005,1,1))
            with c2:
                beneficio = st.number_input("Benefício (R$) *", min_value=0.0, step=50.0)
                parcelas  = st.number_input("Parcelas Ativas (R$)", min_value=0.0, step=50.0)
                canal     = st.selectbox("Canal", ["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"])
                status    = st.selectbox("Status", ["Lead Quente","Em análise","Ativo"])
                interesse = st.selectbox("Interesse", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor"])
            obs = st.text_area("Observações", height=60)

            if st.form_submit_button("✅ Cadastrar", width="stretch"):
                if not nome or not beneficio:
                    st.error("Nome e Benefício são obrigatórios.")
                else:
                    insert_cliente({"nome":nome,"cpf":cpf,"telefone":telefone,
                        "email":email_cli,"data_nasc":str(data_nasc),
                        "beneficio":float(beneficio),"parcelas":float(parcelas),
                        "canal":canal,"status":status,"interesse":interesse,"observacoes":obs})
                    st.success(f"✅ {nome} cadastrado!")
                    st.rerun()

    df = load_clientes()
    if not df.empty:
        cf1, cf2, cf3 = st.columns(3)
        with cf1: f_status = st.multiselect("Status", df["status"].unique().tolist(), default=df["status"].unique().tolist())
        with cf2: f_canal  = st.multiselect("Canal", df["canal"].unique().tolist(), default=df["canal"].unique().tolist())
        with cf3: so_opp   = st.checkbox("Apenas oportunidades")

        df_f = df[df["status"].isin(f_status) & df["canal"].isin(f_canal)]
        if so_opp: df_f = df_f[df_f["margem"]>300]
        df_f = df_f.sort_values("score", ascending=False)

        st.markdown(f"<p style='color:#888;font-size:12px;margin:8px 0 12px'><b>{len(df_f)}</b> cliente(s)</p>", unsafe_allow_html=True)

        for _, row in df_f.iterrows():
            m = row["margem"]
            card_cls = "opp" if m>300 else "red" if m<=0 else "warn"
            sl, sc = score_label(row["score"])
            badge_m = badge("Oportunidade","green") if m>300 else badge("Sem margem","red") if m<=0 else badge("Margem baixa","yellow")
            badge_s = badge(row["status"],"blue")

            with st.expander(f"{'🔥' if row['score']>=75 else '⚡' if row['score']>=55 else '📋'} {row['nome']} — Score {row['score']}% — {fmt(m)} disponível"):
                col_a, col_b = st.columns([2,1])
                with col_a:
                    st.markdown(f"""
                    <div class="client-card {card_cls}">
                      <div style="font-size:15px;font-weight:800;color:{NAVY};margin-bottom:4px">{row['nome']}</div>
                      <div style="font-size:12px;color:#888;margin-bottom:8px">{row['tel_display']} · {row['canal']} · {row['interesse']}</div>
                      <div>{badge_m} {badge_s} <span class="badge bn">Score: {row['score']}%</span></div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;font-size:13px">
                      <div style="padding:8px 12px;background:white;border-radius:10px;border:1px solid #F0F0F0">
                        <div style="color:#888;font-size:10px;margin-bottom:3px">BENEFÍCIO</div>
                        <div style="font-weight:700;color:{NAVY}">{fmt(row['beneficio'])}</div>
                      </div>
                      <div style="padding:8px 12px;background:white;border-radius:10px;border:1px solid #F0F0F0">
                        <div style="color:#888;font-size:10px;margin-bottom:3px">MARGEM DISPONÍVEL</div>
                        <div style="font-weight:700;color:{'#1A7A5E' if m>300 else '#C0392B' if m<=0 else '#F5A623'}">{fmt(m)}</div>
                      </div>
                      <div style="padding:8px 12px;background:white;border-radius:10px;border:1px solid #F0F0F0">
                        <div style="color:#888;font-size:10px;margin-bottom:3px">PRÓXIMO INSS</div>
                        <div style="font-weight:700;color:{NAVY}">{row['prox_pg'].strftime('%d/%m/%Y') if row['prox_pg'] else '—'}</div>
                      </div>
                      <div style="padding:8px 12px;background:white;border-radius:10px;border:1px solid #F0F0F0">
                        <div style="color:#888;font-size:10px;margin-bottom:3px">COMPROMETIMENTO</div>
                        <div style="font-weight:700;color:{'#1A7A5E' if row['pct_comp']<60 else '#F5A623' if row['pct_comp']<90 else '#C0392B'}">{row['pct_comp']:.0f}%</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_b:
                    st.markdown("**Ações rápidas**")

                    # Histórico
                    with st.form(f"hist_{row['id']}"):
                        tipo_contato = st.selectbox("Tipo", ["Ligação","WhatsApp","Visita","Email","Outro"], key=f"tc_{row['id']}")
                        nota = st.text_area("Anotação", height=60, key=f"nota_{row['id']}")
                        if st.form_submit_button("📝 Registrar contato"):
                            insert_historico({"cliente_id":row["id"],"tipo":tipo_contato,"nota":nota,"data":str(date.today())})
                            st.success("Registrado!")
                            st.rerun()

                    # Follow-up
                    with st.form(f"fu_{row['id']}"):
                        data_fu = st.date_input("Agendar follow-up", value=date.today()+timedelta(days=1), key=f"dfu_{row['id']}")
                        motivo  = st.text_input("Motivo", key=f"mfu_{row['id']}")
                        if st.form_submit_button("📅 Agendar"):
                            insert_followup({"cliente_id":row["id"],"data_followup":str(data_fu),"motivo":motivo})
                            st.success("Agendado!")

                    # Email
                    if row.get("email"):
                        if st.button(f"📧 Enviar calendário INSS", key=f"email_{row['id']}"):
                            if email_calendario_inss(row["nome"], row["email"], row["cpf_raw"], row["beneficio"]):
                                st.success("Email enviado!")
                            else:
                                st.error("Erro no envio.")

                    if st.button(f"🗑 Remover", key=f"del_{row['id']}"):
                        delete_cliente(row["id"])
                        st.rerun()

                # Histórico
                hist = load_historico(row["id"])
                if not hist.empty:
                    st.markdown("**Histórico de atendimento**")
                    for _, h in hist.iterrows():
                        st.markdown(f"""
                        <div style="background:#F8F9FA;border-radius:8px;padding:8px 12px;margin-bottom:6px;border-left:3px solid {GREEN}">
                          <span style="font-size:10px;color:#888">{h['data']} · {h['tipo']}</span><br>
                          <span style="font-size:13px;color:#333">{h['nota']}</span>
                        </div>""", unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente cadastrado ainda.")

# ══════════════════════════════════════════════════════════════════════════
# LEADS
# ══════════════════════════════════════════════════════════════════════════
elif "Leads" in menu:
    st.markdown('<div class="page-header"><h2>📋 Pipeline de Leads</h2><p>Funil de vendas com kanban visual</p></div>', unsafe_allow_html=True)

    with st.expander("➕ Novo Lead"):
        with st.form("form_lead", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                l_nome  = st.text_input("Nome")
                l_tel   = st.text_input("Telefone")
                l_canal = st.selectbox("Canal", ["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"])
            with c2:
                l_int    = st.selectbox("Interesse", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado"])
                l_ben    = st.number_input("Benefício (R$)", min_value=0.0, step=50.0)
                l_status = st.selectbox("Status", ["Novo","Em negociação","Convertido","Perdido"])
            l_obs = st.text_area("Observações", height=50)
            if st.form_submit_button("✅ Registrar Lead", width="stretch"):
                insert_lead({"nome":l_nome,"telefone":l_tel,"canal":l_canal,
                             "interesse":l_int,"beneficio":float(l_ben),"status":l_status,"observacoes":l_obs})
                st.success("Lead registrado!")
                st.rerun()

    dfl = load_leads()
    if not dfl.empty:
        STATUS = ["Novo","Em negociação","Convertido","Perdido"]
        ICONS  = {"Novo":"🔵","Em negociação":"🟡","Convertido":"✅","Perdido":"❌"}
        CORES  = {"Novo":NAVY,"Em negociação":YELLOW,"Convertido":GREEN,"Perdido":RED}

        cols = st.columns(4)
        for idx, s in enumerate(STATUS):
            grupo = dfl[dfl["status"]==s]
            with cols[idx]:
                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:14px 12px;box-shadow:0 2px 8px rgba(0,0,0,0.06);min-height:120px">
                  <div style="font-size:12px;font-weight:800;color:{CORES[s]};margin-bottom:10px">
                    {ICONS[s]} {s}
                    <span style="background:#F0F0F0;color:#666;padding:1px 7px;border-radius:99px;font-size:10px;margin-left:4px">{len(grupo)}</span>
                  </div>
                """, unsafe_allow_html=True)
                for _, row in grupo.iterrows():
                    st.markdown(f"""
                    <div style="background:#F8F9FA;border-radius:10px;padding:10px;margin-bottom:8px;border-left:3px solid {CORES[s]}">
                      <div style="font-size:12px;font-weight:700;color:{NAVY}">{row['nome']}</div>
                      <div style="font-size:10px;color:#888;margin-top:2px">{row['canal']} · {row['interesse']}</div>
                      {f'<div style="font-size:12px;color:{GREEN};font-weight:600;margin-top:3px">{fmt(row["beneficio"])}</div>' if row["beneficio"] else ''}
                    </div>""", unsafe_allow_html=True)
                    ns = st.selectbox("Status", STATUS, index=STATUS.index(s), key=f"ls_{row['id']}", label_visibility="collapsed")
                    if ns != s:
                        update_lead_status(row["id"], ns)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum lead registrado.")

# ══════════════════════════════════════════════════════════════════════════
# CONTRATOS
# ══════════════════════════════════════════════════════════════════════════
elif "Contratos" in menu:
    st.markdown('<div class="page-header"><h2>📄 Contratos</h2><p>Carteira de contratos e comissões</p></div>', unsafe_allow_html=True)

    df_cli = load_clientes()
    dfc    = load_contratos()

    if not dfc.empty:
        tv = dfc["valor"].sum()
        tc = tv * 0.03
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(kpi("Carteira Total", fmt(tv), "", "navy"), unsafe_allow_html=True)
        with c2: st.markdown(kpi("Comissão Estimada", fmt(tc), "3% sobre valor", "green"), unsafe_allow_html=True)
        with c3: st.markdown(kpi("Contratos", len(dfc), "", "green"), unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    with st.expander("➕ Novo Contrato"):
        if df_cli.empty:
            st.warning("Cadastre um cliente primeiro.")
        else:
            with st.form("form_ct", clear_on_submit=True):
                cli_map = {r["nome"]: r["id"] for _, r in df_cli.iterrows()}
                c1, c2 = st.columns(2)
                with c1:
                    cli_sel  = st.selectbox("Cliente", list(cli_map.keys()))
                    banco    = st.selectbox("Banco", ["Banco BMG","Banco Safra","Banco PAN","Caixa","BRB","Facta","Itaú Consig."])
                    valor    = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
                with c2:
                    parc_tot = st.number_input("Parcelas", min_value=1, max_value=84, value=36, step=1)
                    taxa     = st.number_input("Taxa (% a.m.)", min_value=0.5, max_value=5.0, value=1.8, step=0.1)
                    d_ini    = st.date_input("Data Início")
                if st.form_submit_button("✅ Registrar", width="stretch"):
                    insert_contrato({"cliente_id":cli_map[cli_sel],"banco":banco,"valor":float(valor),
                        "parcelas_total":int(parc_tot),"taxa_juros":float(taxa),"data_inicio":str(d_ini)})
                    st.success("Contrato registrado!")
                    st.rerun()

    if not dfc.empty:
        dfc["parcela"] = dfc.apply(lambda r: round(
            r["valor"]*(r["taxa_juros"]/100*(1+r["taxa_juros"]/100)**r["parcelas_total"])/
            ((1+r["taxa_juros"]/100)**r["parcelas_total"]-1),2) if r["parcelas_total"]>0 else 0, axis=1)
        dfc["comissao"] = (dfc["valor"]*0.03).round(2)
        st.markdown('<div class="chart-card"><div class="chart-title">Carteira de Contratos</div>', unsafe_allow_html=True)
        st.dataframe(dfc[["cliente_nome","banco","valor","parcelas_total","parcela","comissao","data_inicio"]].rename(columns={
            "cliente_nome":"Cliente","banco":"Banco","valor":"Valor (R$)","parcelas_total":"Parcelas",
            "parcela":"Parcela/mês","comissao":"Comissão","data_inicio":"Início"
        }), width="stretch", hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# SIMULADOR
# ══════════════════════════════════════════════════════════════════════════
elif "Simulador" in menu:
    st.markdown('<div class="page-header"><h2>🧮 Simulador de Crédito</h2><p>Calcule margem, simule propostas e compare portabilidade</p></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["💳 Simulação de Crédito", "🔄 Calculadora de Portabilidade"])

    with tab1:
        c1, c2 = st.columns([1,1.2])
        with c1:
            st.markdown("#### Dados do Cliente")
            ben    = st.number_input("Benefício (R$)", min_value=0.0, value=1412.0, step=50.0)
            parc_a = st.number_input("Parcelas Ativas (R$)", min_value=0.0, value=0.0, step=50.0)
            mc = ben*0.4
            md = max(0, mc-parc_a)
            pct = min(100, round(parc_a/mc*100,1)) if mc>0 else 0
            cor_md = GREEN if md>300 else YELLOW if md>0 else RED
            st.markdown(f"""
            <div style="background:white;border-radius:14px;padding:16px 18px;box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-top:8px">
              <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #F5F5F5;font-size:13px">
                <span style="color:#888">Margem consignável (40%)</span><span style="font-weight:700;color:{NAVY}">{fmt(mc)}</span>
              </div>
              <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #F5F5F5;font-size:13px">
                <span style="color:#888">Parcelas ativas</span><span style="font-weight:700;color:{RED}">{fmt(parc_a)}</span>
              </div>
              <div style="display:flex;justify-content:space-between;padding:5px 0;font-size:13px">
                <span style="color:#888">Margem disponível</span><span style="font-size:20px;font-weight:800;color:{cor_md}">{fmt(md)}</span>
              </div>
              <div style="background:#F0F0F0;border-radius:99px;height:8px;margin-top:10px;overflow:hidden">
                <div style="background:{'#1A7A5E' if pct<60 else '#F5A623' if pct<90 else '#C0392B'};width:{pct}%;height:100%;border-radius:99px"></div>
              </div>
              <div style="font-size:10px;color:#aaa;margin-top:4px">Comprometido: {pct:.0f}%</div>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("#### Simulação")
            valor  = st.number_input("Valor desejado (R$)", min_value=0.0, value=3000.0, step=500.0)
            prazo  = st.select_slider("Prazo", options=[12,24,36,48,60,72,84], value=36)
            taxa   = st.slider("Taxa (% a.m.)", 0.5, 3.5, 1.8, 0.1)

            if valor>0 and ben>0:
                r      = taxa/100
                fator  = (r*(1+r)**prazo)/((1+r)**prazo-1)
                parc   = valor*fator
                total  = parc*prazo
                juros  = total-valor
                cabe   = parc<=md
                cor_r  = GREEN if cabe else RED
                msg    = "✅ Cabe na margem" if cabe else "❌ Excede a margem"

                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-top:4px solid {cor_r}">
                  <div style="text-align:center;padding:10px 0 14px">
                    <div style="font-size:11px;color:#888;margin-bottom:5px">Parcela mensal</div>
                    <div style="font-size:34px;font-weight:800;color:{cor_r}">{fmt(parc)}</div>
                    <div style="font-size:12px;font-weight:700;color:{cor_r};margin-top:4px">{msg}</div>
                  </div>
                  <div style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid #F5F5F5;font-size:13px"><span style="color:#888">Total a pagar</span><span style="font-weight:600">{fmt(total)}</span></div>
                  <div style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid #F5F5F5;font-size:13px"><span style="color:#888">Juros total</span><span style="font-weight:600;color:{RED}">{fmt(juros)}</span></div>
                  <div style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid #F5F5F5;font-size:13px"><span style="color:#888">Comissão estimada</span><span style="font-weight:600;color:{GREEN}">{fmt(valor*0.03)}</span></div>
                </div>""", unsafe_allow_html=True)

        if valor>0 and ben>0:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="chart-card"><div class="chart-title">Comparativo de Prazos</div>', unsafe_allow_html=True)
            r = taxa/100
            pzs = [12,24,36,48,60,72,84]
            pcs = [round(valor*(r*(1+r)**p)/((1+r)**p-1),2) for p in pzs]
            fig5 = go.Figure(go.Bar(
                x=[f"{p}m" for p in pzs], y=pcs,
                marker_color=[GREEN if p<=md else RED for p in pcs],
                marker_line_width=0,
                text=[fmt(p) for p in pcs], textposition="outside", textfont=dict(size=10)
            ))
            fig5.add_hline(y=md, line_dash="dot", line_color=GREEN, line_width=2,
                           annotation_text=f"Margem {fmt(md)}", annotation_font_size=11)
            fig5.update_layout(height=260, **plotly_defaults())
            st.plotly_chart(fig5, width="stretch")
            st.markdown("🟢 Verde = cabe na margem &nbsp;&nbsp; 🔴 Vermelho = excede")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Calculadora de Portabilidade")
        st.markdown("Verifique se vale a pena migrar o contrato do cliente para uma taxa menor.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Contrato Atual**")
            val_atual   = st.number_input("Saldo devedor atual (R$)", min_value=0.0, value=8000.0, step=100.0, key="pa_val")
            parc_atual  = st.number_input("Parcelas restantes", min_value=1, max_value=84, value=48, key="pa_parc")
            taxa_atual  = st.number_input("Taxa atual (% a.m.)", min_value=0.1, max_value=5.0, value=2.1, step=0.1, key="pa_taxa")
        with c2:
            st.markdown("**Nova Proposta**")
            taxa_nova   = st.number_input("Nova taxa (% a.m.)", min_value=0.1, max_value=5.0, value=1.7, step=0.1, key="pn_taxa")
            parc_nova   = st.number_input("Novo prazo (meses)", min_value=1, max_value=84, value=48, key="pn_parc")

        if val_atual>0:
            r_a  = taxa_atual/100
            r_n  = taxa_nova/100
            pc_a = val_atual*(r_a*(1+r_a)**parc_atual)/((1+r_a)**parc_atual-1)
            pc_n = val_atual*(r_n*(1+r_n)**parc_nova)/((1+r_n)**parc_nova-1)
            economia_mensal = pc_a - pc_n
            economia_total  = pc_a*parc_atual - pc_n*parc_nova
            vale  = economia_mensal > 0
            cor_e = GREEN if vale else RED

            st.markdown(f"""
            <div style="background:{'#E8F5F0' if vale else '#FDECEA'};border-radius:14px;padding:20px 24px;margin-top:16px;border:1px solid {'#B8DDD4' if vale else '#F5C6CB'}">
              <div style="font-size:14px;font-weight:800;color:{cor_e};margin-bottom:12px">
                {'✅ Portabilidade VALE A PENA' if vale else '❌ Portabilidade NÃO compensa'}
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
                <div style="text-align:center"><div style="font-size:10px;color:#888;margin-bottom:3px">PARCELA ATUAL</div><div style="font-size:18px;font-weight:700;color:{RED}">{fmt(pc_a)}</div></div>
                <div style="text-align:center"><div style="font-size:10px;color:#888;margin-bottom:3px">NOVA PARCELA</div><div style="font-size:18px;font-weight:700;color:{GREEN}">{fmt(pc_n)}</div></div>
                <div style="text-align:center"><div style="font-size:10px;color:#888;margin-bottom:3px">ECONOMIA/MÊS</div><div style="font-size:18px;font-weight:700;color:{cor_e}">{fmt(abs(economia_mensal))}</div></div>
              </div>
              <div style="margin-top:12px;text-align:center;font-size:13px;color:#555">
                Economia total no período: <strong style="color:{cor_e}">{fmt(abs(economia_total))}</strong>
              </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ALERTAS
# ══════════════════════════════════════════════════════════════════════════
elif "Alertas" in menu:
    st.markdown('<div class="page-header"><h2>🔔 Alertas de Oportunidade</h2><p>Radar inteligente — priorizados por score de propensão</p></div>', unsafe_allow_html=True)

    df = load_clientes()
    if df.empty:
        st.info("Nenhum cliente cadastrado ainda.")
        st.stop()

    opp     = df[df["margem"]>300].sort_values("score", ascending=False)
    baixa   = df[(df["margem"]>0)&(df["margem"]<=300)].sort_values("score", ascending=False)
    sem_m   = df[df["margem"]<=0]
    pg_hoje = df[(df["dias_pg"].notna()) & (df["dias_pg"].astype(float)<=2)]

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi("Prioridade Alta", len(opp), "margem > R$300", "green"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Atenção", len(baixa), "margem baixa", "yellow"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Sem Margem", len(sem_m), "portabilidade", "red"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Pagar Hoje/Amanhã", len(pg_hoje), "contato urgente", "yellow" if len(pg_hoje)>0 else "navy"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if len(pg_hoje)>0:
        st.markdown(f"<div style='font-size:14px;font-weight:800;color:{RED};margin-bottom:10px'>🚨 INSS Cai Hoje ou Amanhã — Contatar Agora</div>", unsafe_allow_html=True)
        for _, row in pg_hoje.iterrows():
            sl, sc = score_label(row["score"])
            st.markdown(f"""
            <div class="alert-box high">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                  <div style="font-size:15px;font-weight:800;color:{NAVY}">{row['nome']}</div>
                  <div style="font-size:12px;color:#888;margin:2px 0 6px">{row['tel_display']} · {row['interesse']}</div>
                  <div>{badge('🚨 URGENTE','red')} {badge(f'Score {row["score"]}%','navy')} {badge(sl,'yellow')}</div>
                </div>
                <div style="text-align:right">
                  <div style="font-size:11px;color:#888">INSS em</div>
                  <div style="font-size:24px;font-weight:800;color:{RED}">{int(row['dias_pg'])} dia(s)</div>
                  <div style="font-size:12px;color:#888">{row['prox_pg'].strftime('%d/%m') if row['prox_pg'] else ''}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    if len(opp)>0:
        st.markdown(f"<div style='font-size:14px;font-weight:800;color:{GREEN};margin:16px 0 10px'>🟢 Contatar Esta Semana — {len(opp)} cliente(s)</div>", unsafe_allow_html=True)
        for _, row in opp.iterrows():
            sl, sc = score_label(row["score"])
            high = row["score"] >= 75
            st.markdown(f"""
            <div class="alert-box {'high' if high else ''}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div style="font-size:15px;font-weight:800;color:{NAVY}">{row['nome']}</div>
                  <div style="font-size:12px;color:#888;margin:2px 0 6px">{row['tel_display']} · {row['interesse']} · {row['canal']}</div>
                  <div>{badge(sl,'green' if row['score']>=55 else 'yellow')} {badge(f'Score {row["score"]}%','navy')} {badge(row['status'],'blue')}</div>
                  {f'<div style="font-size:11px;color:#888;margin-top:4px">INSS em {int(row["dias_pg"])} dia(s) — {row["prox_pg"].strftime("%d/%m") if row["prox_pg"] else ""}</div>' if row['dias_pg'] is not None and not pd.isna(row['dias_pg']) else ''}
                </div>
                <div style="text-align:right">
                  <div style="font-size:11px;color:#888;margin-bottom:2px">Margem disponível</div>
                  <div style="font-size:24px;font-weight:800;color:{GREEN}">{fmt(row['margem'])}</div>
                  <div style="font-size:11px;color:#888;margin-top:3px">Benefício: {fmt(row['beneficio'])}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    if len(baixa)>0:
        st.markdown(f"<div style='font-size:14px;font-weight:800;color:{YELLOW};margin:16px 0 10px'>🟡 Margem Baixa — {len(baixa)} cliente(s)</div>", unsafe_allow_html=True)
        for _, row in baixa.iterrows():
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:12px 16px;margin-bottom:8px;border-left:3px solid {YELLOW};box-shadow:0 2px 6px rgba(0,0,0,0.05);display:flex;justify-content:space-between">
              <div>
                <span style="font-weight:700;color:{NAVY}">{row['nome']}</span>
                <span style="font-size:12px;color:#888;margin-left:8px">{row['tel_display']}</span>
              </div>
              <span style="font-weight:700;color:{YELLOW}">{fmt(row['margem'])} disponível</span>
            </div>""", unsafe_allow_html=True)

    if len(sem_m)>0:
        st.markdown(f"<div style='font-size:14px;font-weight:800;color:{RED};margin:16px 0 10px'>🔴 Sem Margem — Indicar Portabilidade — {len(sem_m)} cliente(s)</div>", unsafe_allow_html=True)
        for _, row in sem_m.iterrows():
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:12px 16px;margin-bottom:8px;border-left:3px solid {RED};box-shadow:0 2px 6px rgba(0,0,0,0.05);display:flex;justify-content:space-between">
              <div>
                <span style="font-weight:700;color:{NAVY}">{row['nome']}</span>
                <span style="font-size:12px;color:#888;margin-left:8px">{row['tel_display']}</span>
              </div>
              <span style="font-size:12px;color:{RED}">Verificar portabilidade</span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# AGENDA
# ══════════════════════════════════════════════════════════════════════════
elif "Agenda" in menu:
    st.markdown('<div class="page-header"><h2>📅 Agenda de Follow-ups</h2><p>Seus compromissos e lembretes de contato</p></div>', unsafe_allow_html=True)

    dfa = load_followups()
    if not dfa.empty:
        dfa["data_followup"] = pd.to_datetime(dfa["data_followup"]).dt.date
        hoje    = date.today()
        vencidos = dfa[dfa["data_followup"] < hoje].sort_values("data_followup")
        hoje_fu  = dfa[dfa["data_followup"] == hoje]
        proximos = dfa[dfa["data_followup"] > hoje].sort_values("data_followup")

        if len(vencidos)>0:
            st.markdown(f"<div style='font-size:13px;font-weight:800;color:{RED};margin-bottom:8px'>🚨 Vencidos — {len(vencidos)}</div>", unsafe_allow_html=True)
            for _, r in vencidos.iterrows():
                col_a, col_b = st.columns([4,1])
                with col_a:
                    st.markdown(f"""
                    <div style="background:#FDECEA;border-radius:10px;padding:10px 14px;margin-bottom:6px;border-left:3px solid {RED}">
                      <span style="font-weight:700;color:{NAVY}">{r['cliente_nome']}</span>
                      <span style="font-size:11px;color:{RED};margin-left:8px">{r['data_followup'].strftime('%d/%m/%Y')}</span>
                      <br><span style="font-size:12px;color:#666">{r['motivo']}</span>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    if st.button("✅ Feito", key=f"dfu_{r['id']}"):
                        delete_followup(r["id"])
                        st.rerun()

        if len(hoje_fu)>0:
            st.markdown(f"<div style='font-size:13px;font-weight:800;color:{GREEN};margin:12px 0 8px'>📌 Hoje — {len(hoje_fu)}</div>", unsafe_allow_html=True)
            for _, r in hoje_fu.iterrows():
                col_a, col_b = st.columns([4,1])
                with col_a:
                    st.markdown(f"""
                    <div style="background:#E8F5F0;border-radius:10px;padding:10px 14px;margin-bottom:6px;border-left:3px solid {GREEN}">
                      <span style="font-weight:700;color:{NAVY}">{r['cliente_nome']}</span>
                      <br><span style="font-size:12px;color:#555">{r['motivo']}</span>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    if st.button("✅ Feito", key=f"dfu_{r['id']}"):
                        delete_followup(r["id"])
                        st.rerun()

        if len(proximos)>0:
            st.markdown(f"<div style='font-size:13px;font-weight:800;color:{NAVY};margin:12px 0 8px'>📆 Próximos — {len(proximos)}</div>", unsafe_allow_html=True)
            for _, r in proximos.iterrows():
                dias = (r["data_followup"] - hoje).days
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:10px 14px;margin-bottom:6px;border-left:3px solid #DDD;box-shadow:0 1px 4px rgba(0,0,0,0.05)">
                  <span style="font-weight:700;color:{NAVY}">{r['cliente_nome']}</span>
                  <span style="font-size:11px;color:#888;margin-left:8px">{r['data_followup'].strftime('%d/%m/%Y')} · em {dias} dia(s)</span>
                  <br><span style="font-size:12px;color:#666">{r['motivo']}</span>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("Nenhum follow-up agendado. Agende na aba Clientes.")

# ══════════════════════════════════════════════════════════════════════════
# EMAIL MARKETING
# ══════════════════════════════════════════════════════════════════════════
elif "Email" in menu:
    st.markdown('<div class="page-header"><h2>📧 Email Marketing</h2><p>Campanhas automáticas via Brevo — 300 emails/dia grátis</p></div>', unsafe_allow_html=True)

    df = load_clientes()
    df_com_email = df[df["email"].notna() & (df["email"] != "")] if not df.empty else pd.DataFrame()

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(kpi("Clientes com Email", len(df_com_email), "na base", "navy"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Emails Disponíveis", "300/dia", "plano gratuito", "green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Custo", "R$ 0,00", "Brevo gratuito", "green"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📅 Calendário INSS", "💡 Dica Financeira", "📣 Campanha Livre"])

    with tab1:
        st.markdown("#### Enviar calendário INSS para clientes")
        st.markdown("Envia o próximo pagamento do INSS personalizado para cada cliente.")
        if df_com_email.empty:
            st.warning("Nenhum cliente com email cadastrado. Adicione emails na aba Clientes.")
        else:
            selecionados = st.multiselect("Selecionar clientes", df_com_email["nome"].tolist(), default=df_com_email["nome"].tolist())
            if st.button("📧 Enviar Calendário INSS", width="stretch"):
                enviados = 0
                for _, row in df_com_email[df_com_email["nome"].isin(selecionados)].iterrows():
                    if email_calendario_inss(row["nome"], row["email"], row["cpf_raw"], row["beneficio"]):
                        enviados += 1
                st.success(f"✅ {enviados} email(s) enviado(s)!")

    with tab2:
        st.markdown("#### Enviar dica financeira")
        DICAS = [
            ("Proteja seu benefício de golpes", "Nunca forneça sua senha do INSS por telefone ou WhatsApp. Golpistas se passam por funcionários de bancos para roubar seu benefício. Em caso de dúvida, ligue diretamente para o banco ou nos procure."),
            ("Você sabia que pode portar seu consignado?", "Se você tem um empréstimo consignado com taxa alta, pode transferir para outro banco com taxa menor sem custo. Isso pode reduzir sua parcela mensal e te dar mais dinheiro no bolso."),
            ("O que é margem consignável?", "A margem consignável é o valor máximo que pode ser descontado do seu benefício. Pelo regulamento do INSS, é de até 40% do seu benefício. Consulte gratuitamente quanto você ainda tem disponível."),
            ("Janeiro é o melhor mês para crédito", "Todo início de ano o INSS reajusta os benefícios. Isso significa mais margem disponível. É o melhor momento para conseguir um crédito com parcelas menores."),
        ]
        dica_sel = st.selectbox("Escolha a dica", [d[0] for d in DICAS])
        dica_corpo = next(d[1] for d in DICAS if d[0] == dica_sel)
        st.info(dica_corpo)
        if df_com_email.empty:
            st.warning("Nenhum cliente com email cadastrado.")
        else:
            selecionados2 = st.multiselect("Clientes", df_com_email["nome"].tolist(), default=df_com_email["nome"].tolist(), key="dica_sel")
            if st.button("📧 Enviar Dica", width="stretch"):
                enviados = 0
                for _, row in df_com_email[df_com_email["nome"].isin(selecionados2)].iterrows():
                    if email_dica_financeira(row["nome"], row["email"], dica_sel, dica_corpo):
                        enviados += 1
                st.success(f"✅ {enviados} email(s) enviado(s)!")

    with tab3:
        st.markdown("#### Campanha personalizada")
        camp_assunto = st.text_input("Assunto do email")
        camp_titulo  = st.text_input("Título da mensagem")
        camp_corpo   = st.text_area("Corpo da mensagem", height=120)
        if df_com_email.empty:
            st.warning("Nenhum cliente com email cadastrado.")
        else:
            selecionados3 = st.multiselect("Clientes", df_com_email["nome"].tolist(), key="camp_sel")
            if st.button("📣 Enviar Campanha", width="stretch"):
                if not camp_assunto or not camp_corpo:
                    st.error("Preencha o assunto e o corpo.")
                else:
                    enviados = 0
                    for _, row in df_com_email[df_com_email["nome"].isin(selecionados3)].iterrows():
                        html = f"""
                        <div style="font-family:Montserrat,Arial,sans-serif;max-width:600px;margin:0 auto">
                          <div style="background:#1B3A6B;padding:24px 32px;border-radius:12px 12px 0 0">
                            <h1 style="color:white;font-size:20px;margin:0">⚛ Núcleo Crédito</h1>
                          </div>
                          <div style="background:white;padding:28px 32px">
                            <p style="font-size:15px;color:#333">Olá, <strong>{row['nome'].split()[0]}</strong>!</p>
                            <h2 style="font-size:18px;color:#1B3A6B">{camp_titulo}</h2>
                            <p style="font-size:14px;color:#555;line-height:1.6">{camp_corpo}</p>
                            <div style="text-align:center;margin:24px 0">
                              <a href="https://wa.me/5511952723015" style="background:#1A7A5E;color:white;padding:12px 28px;border-radius:99px;text-decoration:none;font-weight:700">
                                💬 Falar no WhatsApp
                              </a>
                            </div>
                          </div>
                          <div style="background:#F0F4F8;padding:14px 32px;border-radius:0 0 12px 12px;text-align:center">
                            <p style="font-size:10px;color:#aaa;margin:0">Núcleo Crédito · (11) 95272-3015</p>
                          </div>
                        </div>"""
                        if send_email(row["email"], row["nome"], camp_assunto, html):
                            enviados += 1
                    st.success(f"✅ {enviados} email(s) enviado(s)!")

# ══════════════════════════════════════════════════════════════════════════
# METAS
# ══════════════════════════════════════════════════════════════════════════
elif "Metas" in menu:
    st.markdown('<div class="page-header"><h2>🎯 Painel de Metas</h2><p>Acompanhe seu progresso mensal</p></div>', unsafe_allow_html=True)

    mes_atual = date.today().strftime("%B %Y")

    c1, c2, c3 = st.columns(3)
    with c1:  meta_contratos = st.number_input("Meta de contratos/mês", min_value=1, value=30, step=5)
    with c2:  meta_leads     = st.number_input("Meta de leads/mês", min_value=1, value=50, step=5)
    with c3:  meta_comissao  = st.number_input("Meta de comissão (R$)", min_value=0.0, value=3000.0, step=500.0)

    dfl = load_leads()
    dfc = load_contratos()

    leads_mes     = len(dfl) if not dfl.empty else 0
    contratos_mes = len(dfc) if not dfc.empty else 0
    comissao_mes  = dfc["valor"].sum() * 0.03 if not dfc.empty else 0

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    for label, atual, meta, cor in [
        ("Contratos Fechados", contratos_mes, meta_contratos, GREEN),
        ("Leads Gerados", leads_mes, meta_leads, NAVY),
        ("Comissão (R$)", comissao_mes, meta_comissao, YELLOW),
    ]:
        pct = min(100, round(atual/meta*100,1)) if meta>0 else 0
        val_fmt = fmt(atual) if "R$" in label else str(int(atual))
        meta_fmt = fmt(meta) if "R$" in label else str(int(meta))

        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:18px 20px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <span style="font-size:14px;font-weight:700;color:{NAVY}">{label}</span>
            <span style="font-size:13px;color:#888">{val_fmt} / {meta_fmt} ({pct}%)</span>
          </div>
          <div style="background:#F0F0F0;border-radius:99px;height:12px;overflow:hidden">
            <div style="background:{cor};width:{pct}%;height:100%;border-radius:99px;transition:width .3s"></div>
          </div>
          <div style="font-size:11px;color:{'#1A7A5E' if pct>=100 else '#888'};margin-top:6px">
            {'🎉 Meta atingida!' if pct>=100 else f'Faltam {meta_fmt if "R$" in label else str(int(meta-atual))} para a meta'}
          </div>
        </div>""", unsafe_allow_html=True)

    if contratos_mes > 0 and meta_contratos > 0:
        dias_uteis_restantes = max(1, 22 - date.today().day)
        ritmo_necessario = max(0, (meta_contratos - contratos_mes) / dias_uteis_restantes)
        st.markdown(f"""
        <div style="background:#EBF0F8;border-radius:12px;padding:14px 18px;margin-top:8px">
          <span style="font-size:13px;color:{NAVY};font-weight:600">📈 Ritmo necessário: </span>
          <span style="font-size:13px;color:#555">{ritmo_necessario:.1f} contrato(s)/dia nos próximos {dias_uteis_restantes} dias úteis</span>
        </div>""", unsafe_allow_html=True)
