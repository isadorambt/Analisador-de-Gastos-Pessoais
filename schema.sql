-- ===============================================
-- Analisador de Gastos Pessoais - Estrutura do banco
-- ===============================================

-- Tabela de categorias de gasto (ex: Alimentação, Transporte, Lazer)
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

-- Tabela de contas/cartões (ex: Nubank, Dinheiro, Cartão XP)
CREATE TABLE contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL CHECK (tipo IN ('conta_corrente', 'cartao_credito', 'dinheiro', 'poupanca', 'outro'))
);

-- Tabela de transações (o coração do sistema)
CREATE TABLE transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    categoria_id INTEGER NOT NULL,
    conta_id INTEGER NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (conta_id) REFERENCES contas(id)
);

-- Índices para consultas por data e categoria (comuns em relatórios)
CREATE INDEX idx_transacoes_data ON transacoes(data);
CREATE INDEX idx_transacoes_categoria ON transacoes(categoria_id);

-- ===============================================
-- Perfil: guarda o valor da sua hora de trabalho,
-- usado pra converter gastos em "horas de vida"
-- ===============================================
CREATE TABLE perfil (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor_hora_trabalho REAL NOT NULL
);

-- View: cada transação também mostrada em horas de trabalho equivalentes
CREATE VIEW gastos_em_horas AS
SELECT
    t.id,
    t.data,
    t.descricao,
    t.valor,
    ROUND(t.valor / p.valor_hora_trabalho, 2) AS horas_trabalho
FROM transacoes t, perfil p;
