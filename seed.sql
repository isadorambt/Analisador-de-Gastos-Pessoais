-- ===============================================
-- Dados de exemplo para testar o banco
-- ===============================================

-- Categorias
INSERT INTO categorias (nome) VALUES
    ('Alimentação'),
    ('Transporte'),
    ('Lazer'),
    ('Moradia'),
    ('Saúde'),
    ('Educação'),
    ('Outros');

-- Contas
INSERT INTO contas (nome, tipo) VALUES
    ('Nubank', 'cartao_credito'),
    ('Conta Corrente', 'conta_corrente'),
    ('Dinheiro', 'dinheiro');

-- Transações de exemplo (Setembro de 2026)
INSERT INTO transacoes (data, descricao, valor, categoria_id, conta_id) VALUES
    ('2026-09-01', 'Supermercado', 285.40, 1, 1),
    ('2026-09-02', 'Uber para o trabalho', 18.50, 2, 1),
    ('2026-09-03', 'Cinema', 45.00, 3, 2),
    ('2026-09-05', 'Aluguel', 1200.00, 4, 2),
    ('2026-09-06', 'Farmácia', 67.90, 5, 1),
    ('2026-09-08', 'Restaurante', 92.30, 1, 1),
    ('2026-09-10', 'Curso online', 150.00, 6, 1),
    ('2026-09-12', 'Gasolina', 120.00, 2, 3),
    ('2026-09-15', 'Show de música', 180.00, 3, 1),
    ('2026-09-18', 'Mercado', 210.75, 1, 1),
    ('2026-09-20', 'Conta de luz', 145.00, 4, 2),
    ('2026-09-22', 'Livro', 55.00, 6, 1);
