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
    ('Assinaturas'),
    ('Outros');

-- Contas
INSERT INTO contas (nome, tipo) VALUES
    ('Nubank', 'cartao_credito'),
    ('Conta Corrente', 'conta_corrente'),
    ('Dinheiro', 'dinheiro');

-- Perfil: valor da hora de trabalho (exemplo: R$ 45/hora)
INSERT INTO perfil (valor_hora_trabalho) VALUES (45.00);

-- Transações de exemplo — Junho a Setembro de 2026
-- (4 meses de histórico, pra dar pro detector de assinaturas encontrar padrões)
INSERT INTO transacoes (data, descricao, valor, categoria_id, conta_id) VALUES
    -- Assinaturas recorrentes (mesmo valor, todo mês, ~30 dias de intervalo)
    ('2026-06-05', 'Netflix', 39.90, 7, 1),
    ('2026-06-08', 'Academia', 120.00, 5, 1),
    ('2026-06-12', 'Spotify', 21.90, 7, 1),
    ('2026-07-05', 'Netflix', 39.90, 7, 1),
    ('2026-07-08', 'Academia', 120.00, 5, 1),
    ('2026-07-12', 'Spotify', 21.90, 7, 1),
    ('2026-08-05', 'Netflix', 39.90, 7, 1),
    ('2026-08-08', 'Academia', 120.00, 5, 1),
    ('2026-08-12', 'Spotify', 21.90, 7, 1),
    ('2026-09-05', 'Netflix', 44.90, 7, 1),
    ('2026-09-08', 'Academia', 120.00, 5, 1),
    ('2026-09-12', 'Spotify', 21.90, 7, 1),

    -- Gastos do dia a dia de junho, julho e agosto (não recorrentes)
    ('2026-06-01', 'Supermercado', 260.00, 1, 1),
    ('2026-06-15', 'Uber', 22.00, 2, 1),
    ('2026-07-02', 'Supermercado', 270.30, 1, 1),
    ('2026-07-18', 'Cinema', 42.00, 3, 2),
    ('2026-08-03', 'Supermercado', 295.10, 1, 1),
    ('2026-08-20', 'Farmácia', 58.40, 5, 1),

    -- Gastos de setembro (mês mais detalhado, igual antes)
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
