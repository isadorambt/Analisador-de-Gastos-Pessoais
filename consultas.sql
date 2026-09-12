-- ===============================================
-- Consultas de exemplo - do básico ao avançado
-- ===============================================

-- 1) CONSULTA BÁSICA: listar todas as transações, mais recentes primeiro
SELECT data, descricao, valor
FROM transacoes
ORDER BY data DESC;

-- 2) FILTRO SIMPLES: gastos acima de R$ 100
SELECT data, descricao, valor
FROM transacoes
WHERE valor > 100
ORDER BY valor DESC;

-- 3) JOIN: mostrar o nome da categoria e da conta em vez do ID
SELECT
    t.data,
    t.descricao,
    t.valor,
    c.nome AS categoria,
    ct.nome AS conta
FROM transacoes t
JOIN categorias c ON t.categoria_id = c.id
JOIN contas ct ON t.conta_id = ct.id
ORDER BY t.data;

-- 4) AGREGAÇÃO: total gasto por categoria
SELECT
    c.nome AS categoria,
    SUM(t.valor) AS total_gasto,
    COUNT(*) AS num_transacoes
FROM transacoes t
JOIN categorias c ON t.categoria_id = c.id
GROUP BY c.nome
ORDER BY total_gasto DESC;

-- 5) AGREGAÇÃO: total gasto por conta/cartão
SELECT
    ct.nome AS conta,
    SUM(t.valor) AS total_gasto
FROM transacoes t
JOIN contas ct ON t.conta_id = ct.id
GROUP BY ct.nome
ORDER BY total_gasto DESC;

-- 6) FILTRO POR PERÍODO: gastos de setembro de 2026
SELECT data, descricao, valor
FROM transacoes
WHERE data BETWEEN '2026-09-01' AND '2026-09-30'
ORDER BY data;

-- 7) MÉDIA: ticket médio de gasto por categoria
SELECT
    c.nome AS categoria,
    ROUND(AVG(t.valor), 2) AS ticket_medio
FROM transacoes t
JOIN categorias c ON t.categoria_id = c.id
GROUP BY c.nome
ORDER BY ticket_medio DESC;

-- 8) RESUMO GERAL: quanto eu já gastei no total
SELECT
    SUM(valor) AS total_geral,
    COUNT(*) AS total_transacoes,
    ROUND(AVG(valor), 2) AS gasto_medio_por_transacao
FROM transacoes;

-- 9) TOP 3: as maiores despesas registradas
SELECT descricao, valor, data
FROM transacoes
ORDER BY valor DESC
LIMIT 3;
