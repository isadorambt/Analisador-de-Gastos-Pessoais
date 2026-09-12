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

-- ===============================================
-- 10) CUSTO EM HORAS DE VIDA
-- Converte cada gasto em quantas horas do seu trabalho ele custou.
-- Usa a view gastos_em_horas (que cruza transacoes com o valor
-- da sua hora, guardado na tabela perfil).
-- ===============================================
SELECT descricao, valor, horas_trabalho
FROM gastos_em_horas
ORDER BY horas_trabalho DESC
LIMIT 10;

-- ===============================================
-- 11) DETECTOR DE ASSINATURAS ESQUECIDAS
-- Usa uma WINDOW FUNCTION (LAG) pra comparar cada transação com a
-- transação anterior de mesma descrição, calculando o intervalo de
-- dias e a diferença de valor entre elas. Se o intervalo for
-- consistentemente ~30 dias e o valor for parecido, é assinatura.
-- ===============================================
WITH ordenado AS (
    SELECT
        descricao,
        data,
        valor,
        LAG(data) OVER (PARTITION BY descricao ORDER BY data) AS data_anterior,
        LAG(valor) OVER (PARTITION BY descricao ORDER BY data) AS valor_anterior
    FROM transacoes
),
intervalos AS (
    SELECT
        descricao,
        valor,
        julianday(data) - julianday(data_anterior) AS dias_desde_ultima,
        ABS(valor - valor_anterior) AS diferenca_valor
    FROM ordenado
    WHERE data_anterior IS NOT NULL
)
SELECT
    descricao,
    COUNT(*) + 1 AS ocorrencias,
    ROUND(AVG(dias_desde_ultima), 1) AS intervalo_medio_dias,
    ROUND(AVG(valor), 2) AS valor_medio_atual
FROM intervalos
WHERE dias_desde_ultima BETWEEN 25 AND 35   -- aproximadamente mensal
  AND diferenca_valor < 10                  -- valor parecido (tolera reajuste)
GROUP BY descricao
HAVING COUNT(*) >= 2                        -- pelo menos 3 ocorrências no total
ORDER BY ocorrencias DESC;
