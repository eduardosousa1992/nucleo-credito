import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import os

# ── CONFIG ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Núcleo Crédito",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY   = "#1B3A6B"
GREEN  = "#1A7A5E"
RED    = "#C0392B"
YELLOW = "#F5A623"

st.markdown(f"""
<style>
    .main {{ background-color: #F8F9FA; }}
    .stApp header {{ background-color: {NAVY}; }}
    .metric-card {{
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        border-left: 4px solid {GREEN};
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 8px;
    }}
    .metric-card.alert {{ border-left-color: {RED}; }}
    .metric-card.warn  {{ border-left-color: {YELLOW}; }}
    .metric-value {{ font-size: 28px; font-weight: 700; color: {NAVY}; }}
    .metric-label {{ font-size: 12px; color: #666; margin-bottom: 4px; }}
    .alert-badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 11px;
        font-weight: 600;
    }}
    .section-header {{
        font-size: 14px;
        font-weight: 600;
        color: {NAVY};
        border-bottom: 2px solid {GREEN};
        padding-bottom: 6px;
        margin: 20px 0 12px;
    }}
    div[data-testid="stSidebarContent"] {{
        background: {NAVY};
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

# ── BANCO DE DADOS ──────────────────────────────────────────────────────────
DB = "nucleo_credito.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS clientes (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        nome        TEXT NOT NULL,
        cpf         TEXT,
        telefone    TEXT,
        data_nasc   TEXT,
        beneficio   REAL NOT NULL,
        parcelas    REAL DEFAULT 0,
        canal       TEXT,
        status      TEXT DEFAULT 'Lead Quente',
        interesse   TEXT,
        observacoes TEXT,
        data_cad    TEXT DEFAULT CURRENT_DATE
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS contratos (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id     INTEGER,
        banco          TEXT,
        valor          REAL,
        parcelas_total INTEGER,
        parcelas_pagas INTEGER DEFAULT 0,
        data_inicio    TEXT,
        taxa_juros     REAL DEFAULT 1.8,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS leads (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        nome        TEXT,
        telefone    TEXT,
        canal       TEXT,
        interesse   TEXT,
        beneficio   REAL,
        status      TEXT DEFAULT 'Novo',
        data_contato TEXT DEFAULT CURRENT_DATE,
        observacoes  TEXT
    )""")
    # Seed com 5 clientes fictícios se vazio
    if c.execute("SELECT COUNT(*) FROM clientes").fetchone()[0] == 0:
        seed = [
            ("Maria Aparecida dos Santos","123.456.789-01","(89)99801-1234","1958-03-12",1412,320,"Panfletagem","Ativo","Consignado INSS","Aposentada por idade"),
            ("José Raimundo Sousa Lima","234.567.890-12","(89)99802-5678","1952-07-25",1754,580,"Rádio","Ativo","Consignado INSS","Pensionista — margem parcial"),
            ("Antonia Ferreira Mendes","345.678.901-23","(89)99803-9012","1965-11-08",2118,0,"WhatsApp","Lead Quente","Portabilidade","Servidora municipal — margem virgem"),
            ("Francisco das Chagas Oliveira","456.789.012-34","(89)99804-3456","1949-04-30",1320,528,"Indicação","Em análise","Consignado INSS","Margem esgotada — analisar portabilidade"),
            ("Raimunda Alves Costa","567.890.123-45","(89)99805-7890","1960-09-17",1980,450,"Google","Ativo","Cartão Consignado","Filha indicou após busca no Google"),
        ]
        c.executemany("""INSERT INTO clientes
            (nome,cpf,telefone,data_nasc,beneficio,parcelas,canal,status,interesse,observacoes)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", seed)
        # Seed leads
        leads_seed = [
            ("João Batista Rocha","(89)99811-1111","Panfletagem","Consignado INSS",1412,"Convertido","Converteu no dia seguinte"),
            ("Conceição Rodrigues","(89)99822-2222","Rádio","Consignado INSS",1754,"Convertido","Ouviu spot manhã"),
            ("Severino Gonçalves","(89)99833-3333","WhatsApp","Portabilidade",2118,"Em negociação","Contrato BMG 2.2%"),
            ("Terezinha Moura","(89)99844-4444","Indicação","Consignado INSS",1320,"Em negociação","Indicada por cliente"),
            ("Benedito Souza","(89)99855-5555","Instagram","Cartão Consignado",1980,"Novo","Filho enviou mensagem"),
        ]
        c.executemany("""INSERT INTO leads (nome,telefone,canal,interesse,beneficio,status,observacoes)
            VALUES (?,?,?,?,?,?,?)""", leads_seed)
    conn.commit()
    conn.close()

def load_clientes():
    return pd.read_sql("SELECT * FROM clientes ORDER BY id DESC", get_conn())

def load_leads():
    return pd.read_sql("SELECT * FROM leads ORDER BY id DESC", get_conn())

def load_contratos():
    return pd.read_sql("""
        SELECT c.*, cl.nome as cliente_nome
        FROM contratos c
        LEFT JOIN clientes cl ON c.cliente_id = cl.id
        ORDER BY c.id DESC
    """, get_conn())

def calcular_margem(beneficio, parcelas):
    return round(beneficio * 0.4 - parcelas, 2)

# ── INICIALIZA DB ───────────────────────────────────────────────────────────
init_db()

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:10px 0 20px'>
        <div style='font-size:28px'>⚛</div>
        <div style='font-size:18px;font-weight:700;color:white'>Núcleo Crédito</div>
        <div style='font-size:11px;color:#9BB8D8;margin-top:4px'>No centro da sua vida financeira.</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio("", [
        "📊  Dashboard",
        "👥  Clientes",
        "📋  Leads",
        "📄  Contratos",
        "🧮  Simulador",
        "🔔  Alertas",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"<div style='color:#9BB8D8;font-size:11px;text-align:center'>(11) 95272-3015<br>@nucleocredito<br>{date.today().strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)

# ── HELPERS ─────────────────────────────────────────────────────────────────
def badge(text, color):
    colors = {
        "green":  ("#E8F5F0","#0F6E56"),
        "yellow": ("#FFF3CD","#856404"),
        "red":    ("#FDECEA","#A32D2D"),
        "blue":   ("#E6F1FB","#185FA5"),
    }
    bg, tc = colors.get(color, ("#F0F0F0","#333"))
    return f"<span style='background:{bg};color:{tc};padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600'>{text}</span>"

# ══════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
if "Dashboard" in menu:
    st.markdown(f"<div style='background:{NAVY};color:white;padding:16px 20px;border-radius:12px;margin-bottom:20px'><h2 style='margin:0;font-size:20px'>⚛ Dashboard de Performance — Núcleo Crédito</h2><p style='margin:4px 0 0;opacity:.7;font-size:12px'>{date.today().strftime('%d de %B de %Y')}</p></div>", unsafe_allow_html=True)

    df = load_clientes()
    dfl = load_leads()

    df["margem"] = df.apply(lambda r: calcular_margem(r["beneficio"], r["parcelas"]), axis=1)
    total_margem = df["margem"].clip(lower=0).sum()
    oportunidades = (df["margem"] > 300).sum()
    ativos = (df["status"] == "Ativo").sum()
    convertidos = (dfl["status"] == "Convertido").sum()
    taxa_conv = round(convertidos / len(dfl) * 100, 1) if len(dfl) > 0 else 0

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("👥 Clientes", len(df))
    with c2:
        st.metric("✅ Ativos", int(ativos))
    with c3:
        st.metric("💰 Margem Total", f"R$ {total_margem:,.0f}".replace(",","."))
    with c4:
        st.metric("🔔 Oportunidades", int(oportunidades))
    with c5:
        st.metric("📈 Conversão", f"{taxa_conv}%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Margem Disponível por Cliente")
        df_sorted = df.sort_values("margem", ascending=True)
        cores = [GREEN if m > 300 else YELLOW if m > 0 else RED for m in df_sorted["margem"]]
        fig = go.Figure(go.Bar(
            x=df_sorted["margem"],
            y=df_sorted["nome"].str.split().str[:2].str.join(" "),
            orientation="h",
            marker_color=cores,
            text=[f"R$ {m:,.0f}" for m in df_sorted["margem"]],
            textposition="outside"
        ))
        fig.update_layout(
            height=300, margin=dict(l=0,r=40,t=10,b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="R$", yaxis_title=""
        )
        fig.add_vline(x=300, line_dash="dash", line_color=GREEN, annotation_text="Limiar R$300")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Leads por Canal de Origem")
        canal_counts = dfl["canal"].value_counts().reset_index()
        canal_counts.columns = ["Canal", "Leads"]
        fig2 = px.bar(canal_counts, x="Canal", y="Leads",
            color_discrete_sequence=[NAVY],
            text="Leads")
        fig2.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
            plot_bgcolor="white", paper_bgcolor="white")
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Status dos Leads")
        status_counts = dfl["status"].value_counts().reset_index()
        status_counts.columns = ["Status","Qtd"]
        fig3 = px.pie(status_counts, values="Qtd", names="Status",
            color_discrete_sequence=[GREEN, YELLOW, NAVY, RED],
            hole=0.5)
        fig3.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### Comprometimento de Margem")
        df["pct_comprometido"] = (df["parcelas"] / (df["beneficio"] * 0.4) * 100).clip(0, 100).round(1)
        fig4 = px.bar(df, x=df["nome"].str.split().str[0], y="pct_comprometido",
            color="pct_comprometido",
            color_continuous_scale=[[0,GREEN],[0.6,YELLOW],[1,RED]],
            text="pct_comprometido", labels={"pct_comprometido":"%","x":"Cliente"})
        fig4.update_traces(texttemplate="%{text}%", textposition="outside")
        fig4.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════════════════════════════════
elif "Clientes" in menu:
    st.markdown(f"<div style='background:{NAVY};color:white;padding:14px 20px;border-radius:12px;margin-bottom:20px'><h2 style='margin:0;font-size:18px'>👥 Gestão de Clientes</h2></div>", unsafe_allow_html=True)

    with st.expander("➕ Cadastrar Novo Cliente", expanded=False):
        with st.form("form_cliente"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome Completo *")
                cpf = st.text_input("CPF")
                telefone = st.text_input("Telefone")
                data_nasc = st.date_input("Data de Nascimento", value=date(1960,1,1))
            with c2:
                beneficio = st.number_input("Benefício / Salário (R$) *", min_value=0.0, step=50.0)
                parcelas = st.number_input("Parcelas Já Ativas (R$)", min_value=0.0, step=50.0)
                canal = st.selectbox("Canal de Origem", ["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"])
                status = st.selectbox("Status", ["Lead Quente","Em análise","Ativo"])
            interesse = st.selectbox("Interesse Principal", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado","Consignado Servidor"])
            obs = st.text_area("Observações", height=60)

            if st.form_submit_button("✅ Cadastrar Cliente", use_container_width=True):
                if not nome or not beneficio:
                    st.error("Nome e Benefício são obrigatórios.")
                else:
                    conn = get_conn()
                    conn.execute("""INSERT INTO clientes
                        (nome,cpf,telefone,data_nasc,beneficio,parcelas,canal,status,interesse,observacoes)
                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (nome,cpf,telefone,str(data_nasc),beneficio,parcelas,canal,status,interesse,obs))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {nome} cadastrado com sucesso!")
                    st.rerun()

    df = load_clientes()
    df["margem"] = df.apply(lambda r: calcular_margem(r["beneficio"], r["parcelas"]), axis=1)

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtro_status = st.multiselect("Filtrar por Status", df["status"].unique(), default=list(df["status"].unique()))
    with col_f2:
        filtro_canal = st.multiselect("Filtrar por Canal", df["canal"].unique(), default=list(df["canal"].unique()))
    with col_f3:
        apenas_oportunidades = st.checkbox("Apenas com oportunidade (margem > R$300)")

    df_filtrado = df[df["status"].isin(filtro_status) & df["canal"].isin(filtro_canal)]
    if apenas_oportunidades:
        df_filtrado = df_filtrado[df_filtrado["margem"] > 300]

    st.markdown(f"**{len(df_filtrado)} clientes encontrados**")

    for _, row in df_filtrado.iterrows():
        m = row["margem"]
        pct = min(100, max(0, row["parcelas"] / (row["beneficio"] * 0.4) * 100)) if row["beneficio"] > 0 else 0
        cor = GREEN if m > 300 else YELLOW if m > 0 else RED
        badge_txt = "Oportunidade" if m > 300 else "Margem baixa" if m > 0 else "Sem margem"
        badge_cor = "green" if m > 300 else "yellow" if m > 0 else "red"

        with st.container():
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**{row['nome']}**")
                st.markdown(f"<span style='font-size:12px;color:#666'>{row['telefone']} &nbsp;|&nbsp; {row['canal']} &nbsp;|&nbsp; {row['interesse']}</span>", unsafe_allow_html=True)
                st.progress(int(pct)/100, text=f"Margem comprometida: {pct:.0f}%")
            with c2:
                st.markdown(f"Benefício: **R$ {row['beneficio']:,.2f}**")
                st.markdown(f"Margem disponível: <span style='color:{cor};font-weight:700'>R$ {m:,.2f}</span>", unsafe_allow_html=True)
                st.markdown(badge(badge_txt, badge_cor) + "&nbsp;" + badge(row["status"], "blue"), unsafe_allow_html=True)
            with c3:
                if st.button("🗑 Remover", key=f"del_{row['id']}"):
                    get_conn().execute("DELETE FROM clientes WHERE id=?", (row["id"],))
                    get_conn().commit()
                    st.rerun()
            st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════
# LEADS
# ══════════════════════════════════════════════════════════════════════════
elif "Leads" in menu:
    st.markdown(f"<div style='background:{NAVY};color:white;padding:14px 20px;border-radius:12px;margin-bottom:20px'><h2 style='margin:0;font-size:18px'>📋 Pipeline de Leads</h2></div>", unsafe_allow_html=True)

    with st.expander("➕ Registrar Novo Lead"):
        with st.form("form_lead"):
            c1, c2 = st.columns(2)
            with c1:
                l_nome = st.text_input("Nome")
                l_tel = st.text_input("Telefone")
                l_canal = st.selectbox("Canal", ["Panfletagem","Rádio","WhatsApp","Indicação","Instagram","Google","Presencial"])
            with c2:
                l_interesse = st.selectbox("Interesse", ["Consignado INSS","Portabilidade","Refinanciamento","Cartão Consignado"])
                l_ben = st.number_input("Benefício informado (R$)", min_value=0.0, step=50.0)
                l_status = st.selectbox("Status", ["Novo","Em negociação","Convertido","Perdido"])
            l_obs = st.text_area("Observações", height=60)
            if st.form_submit_button("✅ Registrar Lead", use_container_width=True):
                conn = get_conn()
                conn.execute("INSERT INTO leads (nome,telefone,canal,interesse,beneficio,status,observacoes) VALUES (?,?,?,?,?,?,?)",
                    (l_nome, l_tel, l_canal, l_interesse, l_ben, l_status, l_obs))
                conn.commit()
                conn.close()
                st.success("Lead registrado!")
                st.rerun()

    dfl = load_leads()
    status_order = ["Novo","Em negociação","Convertido","Perdido"]
    status_colors = {"Novo":"blue","Em negociação":"yellow","Convertido":"green","Perdido":"red"}

    for s in status_order:
        grupo = dfl[dfl["status"]==s]
        if len(grupo) == 0:
            continue
        st.markdown(f"#### {badge(s, status_colors[s])} &nbsp; {len(grupo)} lead(s)", unsafe_allow_html=True)
        for _, row in grupo.iterrows():
            c1, c2, c3 = st.columns([3,2,1])
            with c1:
                st.markdown(f"**{row['nome']}** — {row['telefone']}")
                st.markdown(f"<span style='font-size:12px;color:#666'>{row['canal']} &nbsp;|&nbsp; {row['interesse']}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"Benefício: R$ {row['beneficio']:,.2f}" if row['beneficio'] else "Benefício: —")
                st.markdown(f"<span style='font-size:11px;color:#888'>{row['observacoes']}</span>", unsafe_allow_html=True)
            with c3:
                novo_status = st.selectbox("", status_order, index=status_order.index(s), key=f"ls_{row['id']}", label_visibility="collapsed")
                if novo_status != s:
                    get_conn().execute("UPDATE leads SET status=? WHERE id=?", (novo_status, row["id"]))
                    get_conn().commit()
                    st.rerun()
            st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════
# CONTRATOS
# ══════════════════════════════════════════════════════════════════════════
elif "Contratos" in menu:
    st.markdown(f"<div style='background:{NAVY};color:white;padding:14px 20px;border-radius:12px;margin-bottom:20px'><h2 style='margin:0;font-size:18px'>📄 Contratos</h2></div>", unsafe_allow_html=True)

    df_cli = load_clientes()

    with st.expander("➕ Registrar Novo Contrato"):
        with st.form("form_contrato"):
            c1, c2 = st.columns(2)
            with c1:
                cli_opcoes = {f"{r['nome']} (C{r['id']:03d})": r["id"] for _, r in df_cli.iterrows()}
                cli_sel = st.selectbox("Cliente", list(cli_opcoes.keys()))
                banco = st.selectbox("Banco", ["Banco BMG","Banco Safra","Banco PAN","Caixa","BRB","Facta","Itaú"])
                valor = st.number_input("Valor Contratado (R$)", min_value=0.0, step=100.0)
            with c2:
                parcelas_total = st.number_input("Total de Parcelas", min_value=1, max_value=84, step=1, value=36)
                taxa = st.number_input("Taxa de Juros (% a.m.)", min_value=0.0, max_value=5.0, value=1.8, step=0.1)
                data_inicio = st.date_input("Data de Início")
            if st.form_submit_button("✅ Registrar Contrato", use_container_width=True):
                conn = get_conn()
                conn.execute("INSERT INTO contratos (cliente_id,banco,valor,parcelas_total,taxa_juros,data_inicio) VALUES (?,?,?,?,?,?)",
                    (cli_opcoes[cli_sel], banco, valor, parcelas_total, taxa, str(data_inicio)))
                conn.commit()
                conn.close()
                st.success("Contrato registrado!")
                st.rerun()

    df_c = load_contratos()
    if len(df_c) > 0:
        df_c["parcela_mensal"] = df_c.apply(lambda r: round(
            r["valor"] * (r["taxa_juros"]/100 * (1+r["taxa_juros"]/100)**r["parcelas_total"]) /
            ((1+r["taxa_juros"]/100)**r["parcelas_total"]-1), 2
        ) if r["parcelas_total"] > 0 else 0, axis=1)
        df_c["comissao"] = (df_c["valor"] * 0.03).round(2)
        df_c["restantes"] = df_c["parcelas_total"] - df_c["parcelas_pagas"]

        st.markdown(f"**Total em carteira: R$ {df_c['valor'].sum():,.2f}** &nbsp;|&nbsp; **Comissão estimada: R$ {df_c['comissao'].sum():,.2f}**")
        st.dataframe(df_c[["cliente_nome","banco","valor","parcelas_total","restantes","parcela_mensal","comissao","data_inicio"]].rename(columns={
            "cliente_nome":"Cliente","banco":"Banco","valor":"Valor (R$)","parcelas_total":"Parcelas",
            "restantes":"Restantes","parcela_mensal":"Parcela (R$)","comissao":"Comissão (R$)","data_inicio":"Início"
        }), use_container_width=True)
    else:
        st.info("Nenhum contrato registrado ainda.")

# ══════════════════════════════════════════════════════════════════════════
# SIMULADOR
# ══════════════════════════════════════════════════════════════════════════
elif "Simulador" in menu:
    st.markdown(f"<div style='background:{NAVY};color:white;padding:14px 20px;border-radius:12px;margin-bottom:20px'><h2 style='margin:0;font-size:18px'>🧮 Simulador de Crédito Consignado</h2></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Dados do Cliente")
        beneficio = st.number_input("Benefício / Salário (R$)", min_value=0.0, value=1412.0, step=50.0)
        parcelas_ativas = st.number_input("Parcelas já ativas (R$)", min_value=0.0, value=0.0, step=50.0)
        margem_consig = beneficio * 0.4
        margem_disp = max(0, margem_consig - parcelas_ativas)

        st.markdown(f"""
        <div style='background:#E8F5F0;border-radius:10px;padding:14px;margin-top:10px'>
            <div style='font-size:12px;color:#0F6E56'>Margem consignável (40%)</div>
            <div style='font-size:22px;font-weight:700;color:{NAVY}'>R$ {margem_consig:,.2f}</div>
            <div style='font-size:12px;color:#0F6E56;margin-top:8px'>Margem disponível</div>
            <div style='font-size:22px;font-weight:700;color:{GREEN if margem_disp > 300 else RED}'>R$ {margem_disp:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Simulação")
        valor_desejado = st.number_input("Valor desejado (R$)", min_value=0.0, value=3000.0, step=500.0)
        prazo = st.slider("Prazo (meses)", 12, 84, 36, step=12)
        taxa = st.number_input("Taxa de juros (% a.m.)", min_value=0.5, max_value=5.0, value=1.8, step=0.1)

        if valor_desejado > 0 and beneficio > 0:
            r = taxa / 100
            fator = (r * (1+r)**prazo) / ((1+r)**prazo - 1)
            parcela = valor_desejado * fator
            total_pago = parcela * prazo
            juros = total_pago - valor_desejado
            cabe = parcela <= margem_disp
            cor_res = GREEN if cabe else RED
            msg = "✅ Cabe na margem disponível" if cabe else "❌ Excede a margem — ajuste o valor ou prazo"

            st.markdown(f"""
            <div style='background:{"#E8F5F0" if cabe else "#FDECEA"};border-radius:10px;padding:14px;margin-top:10px'>
                <div style='font-size:12px;color:#666'>Parcela mensal</div>
                <div style='font-size:28px;font-weight:700;color:{cor_res}'>R$ {parcela:,.2f}</div>
                <hr style='border:.5px solid rgba(0,0,0,0.1);margin:10px 0'>
                <div style='display:flex;justify-content:space-between;font-size:13px'>
                    <span>Total a pagar</span><span><b>R$ {total_pago:,.2f}</b></span>
                </div>
                <div style='display:flex;justify-content:space-between;font-size:13px;margin-top:4px'>
                    <span>Juros total</span><span style='color:{RED}'><b>R$ {juros:,.2f}</b></span>
                </div>
                <div style='display:flex;justify-content:space-between;font-size:13px;margin-top:4px'>
                    <span>Comissão estimada</span><span style='color:{GREEN}'><b>R$ {valor_desejado*0.03:,.2f}</b></span>
                </div>
                <div style='margin-top:10px;font-weight:600;color:{cor_res}'>{msg}</div>
            </div>
            """, unsafe_allow_html=True)

    if valor_desejado > 0 and beneficio > 0:
        st.markdown("#### Comparativo de Prazos")
        prazos = [12, 24, 36, 48, 60, 72, 84]
        parcelas_sim = []
        for p in prazos:
            f = (r * (1+r)**p) / ((1+r)**p - 1)
            parcelas_sim.append(round(valor_desejado * f, 2))

        cores_prazos = [GREEN if ps <= margem_disp else RED for ps in parcelas_sim]
        fig = go.Figure(go.Bar(
            x=[f"{p}m" for p in prazos],
            y=parcelas_sim,
            marker_color=cores_prazos,
            text=[f"R${p:,.0f}" for p in parcelas_sim],
            textposition="outside"
        ))
        fig.add_hline(y=margem_disp, line_dash="dash", line_color=GREEN,
                      annotation_text=f"Margem disponível R${margem_disp:,.2f}")
        fig.update_layout(height=300, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(l=0,r=0,t=20,b=0),
                          yaxis_title="Parcela (R$)", xaxis_title="Prazo")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🟢 Verde = cabe na margem &nbsp;&nbsp; 🔴 Vermelho = excede a margem")

# ══════════════════════════════════════════════════════════════════════════
# ALERTAS
# ══════════════════════════════════════════════════════════════════════════
elif "Alertas" in menu:
    st.markdown(f"<div style='background:{NAVY};color:white;padding:14px 20px;border-radius:12px;margin-bottom:20px'><h2 style='margin:0;font-size:18px'>🔔 Alertas de Oportunidade</h2></div>", unsafe_allow_html=True)

    df = load_clientes()
    df["margem"] = df.apply(lambda r: calcular_margem(r["beneficio"], r["parcelas"]), axis=1)

    opp = df[df["margem"] > 300].sort_values("margem", ascending=False)
    sem_margem = df[df["margem"] <= 0]
    baixa = df[(df["margem"] > 0) & (df["margem"] <= 300)]

    st.markdown(f"### 🟢 Contatar esta semana — {len(opp)} cliente(s)")
    if len(opp) > 0:
        for _, row in opp.iterrows():
            with st.container():
                c1, c2 = st.columns([3,1])
                with c1:
                    st.markdown(f"**{row['nome']}**")
                    st.markdown(f"<span style='font-size:12px;color:#666'>{row['telefone']} &nbsp;|&nbsp; {row['interesse']} &nbsp;|&nbsp; {row['canal']}</span>", unsafe_allow_html=True)
                    st.markdown(f"Margem disponível: <span style='color:{GREEN};font-size:18px;font-weight:700'>R$ {row['margem']:,.2f}</span>", unsafe_allow_html=True)
                with c2:
                    if row["margem"] > 600:
                        st.error("🔥 Prioridade máxima")
                    else:
                        st.success("✅ Oportunidade")
                st.markdown("---")
    else:
        st.info("Nenhuma oportunidade com margem > R$300 no momento.")

    st.markdown(f"### 🟡 Margem baixa — {len(baixa)} cliente(s)")
    for _, row in baixa.iterrows():
        st.markdown(f"**{row['nome']}** — margem de R$ {row['margem']:,.2f} — considere portabilidade")

    st.markdown(f"### 🔴 Sem margem disponível — {len(sem_margem)} cliente(s)")
    for _, row in sem_margem.iterrows():
        st.markdown(f"**{row['nome']}** — R$ {row['margem']:,.2f} — indicar portabilidade ou aguardar reajuste INSS")
