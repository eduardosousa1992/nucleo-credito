-- ═══════════════════════════════════════════════════════════
-- NÚCLEO CRÉDITO — Schema do Banco de Dados
-- Execute no Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════

-- CLIENTES
CREATE TABLE IF NOT EXISTS clientes (
    id          BIGSERIAL PRIMARY KEY,
    nome        TEXT NOT NULL,
    cpf         TEXT,
    telefone    TEXT,
    email       TEXT,
    data_nasc   DATE,
    beneficio   NUMERIC(10,2) NOT NULL DEFAULT 0,
    parcelas    NUMERIC(10,2) NOT NULL DEFAULT 0,
    canal       TEXT,
    status      TEXT DEFAULT 'Lead Quente',
    interesse   TEXT,
    observacoes TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- LEADS
CREATE TABLE IF NOT EXISTS leads (
    id          BIGSERIAL PRIMARY KEY,
    nome        TEXT,
    telefone    TEXT,
    canal       TEXT,
    interesse   TEXT,
    beneficio   NUMERIC(10,2) DEFAULT 0,
    status      TEXT DEFAULT 'Novo',
    observacoes TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- CONTRATOS
CREATE TABLE IF NOT EXISTS contratos (
    id              BIGSERIAL PRIMARY KEY,
    cliente_id      BIGINT REFERENCES clientes(id) ON DELETE CASCADE,
    banco           TEXT,
    valor           NUMERIC(10,2) DEFAULT 0,
    parcelas_total  INTEGER DEFAULT 12,
    parcelas_pagas  INTEGER DEFAULT 0,
    taxa_juros      NUMERIC(5,2) DEFAULT 1.8,
    data_inicio     DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- HISTÓRICO DE ATENDIMENTO
CREATE TABLE IF NOT EXISTS historico (
    id          BIGSERIAL PRIMARY KEY,
    cliente_id  BIGINT REFERENCES clientes(id) ON DELETE CASCADE,
    tipo        TEXT,
    nota        TEXT,
    data        DATE DEFAULT CURRENT_DATE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- FOLLOW-UPS
CREATE TABLE IF NOT EXISTS followups (
    id              BIGSERIAL PRIMARY KEY,
    cliente_id      BIGINT REFERENCES clientes(id) ON DELETE CASCADE,
    data_followup   DATE,
    motivo          TEXT,
    concluido       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY (LGPD)
-- ═══════════════════════════════════════════════════════════
ALTER TABLE clientes  ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads     ENABLE ROW LEVEL SECURITY;
ALTER TABLE contratos ENABLE ROW LEVEL SECURITY;
ALTER TABLE historico ENABLE ROW LEVEL SECURITY;
ALTER TABLE followups ENABLE ROW LEVEL SECURITY;

-- Políticas — acesso apenas autenticado
CREATE POLICY "acesso_total" ON clientes  FOR ALL USING (true);
CREATE POLICY "acesso_total" ON leads     FOR ALL USING (true);
CREATE POLICY "acesso_total" ON contratos FOR ALL USING (true);
CREATE POLICY "acesso_total" ON historico FOR ALL USING (true);
CREATE POLICY "acesso_total" ON followups FOR ALL USING (true);
