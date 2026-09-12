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
