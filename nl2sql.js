/**
 * Tradutor de perguntas em português para SQL.
 *
 * IMPORTANTE: isso NÃO é um LLM. É um tradutor por padrões (regex +
 * comparação de texto normalizado) que reconhece um conjunto fixo de
 * formatos de pergunta e gera o SQL correspondente. Funciona 100% no
 * navegador, sem servidor e sem custo — mas só entende as perguntas
 * que ele foi programado para reconhecer.
 *
 * Roda tanto no navegador (via <script src="nl2sql.js">, expõe
 * window.traduzirPergunta) quanto no Node (via require, pros testes
 * em tests/test_nl2sql.js).
 */

const CATEGORIAS = [
  "Alimentação", "Transporte", "Lazer", "Moradia",
  "Saúde", "Educação", "Assinaturas", "Outros",
];

// O banco de exemplo cobre junho a setembro de 2026.
const MESES = {
  junho: { ini: "2026-06-01", fim: "2026-06-30" },
  julho: { ini: "2026-07-01", fim: "2026-07-31" },
  agosto: { ini: "2026-08-01", fim: "2026-08-31" },
  setembro: { ini: "2026-09-01", fim: "2026-09-30" },
};

function normalizar(texto) {
  return texto
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function encontrarCategoria(normalizado) {
  for (const categoria of CATEGORIAS) {
    if (normalizado.includes(normalizar(categoria))) return categoria;
  }
  return null;
}

function encontrarMes(normalizado) {
  for (const mes of Object.keys(MESES)) {
    if (normalizado.includes(mes)) return mes;
  }
  return null;
}

const SQL_ASSINATURAS = `WITH ordenado AS (
    SELECT
        descricao, data, valor,
        LAG(data) OVER (PARTITION BY descricao ORDER BY data) AS data_anterior,
        LAG(valor) OVER (PARTITION BY descricao ORDER BY data) AS valor_anterior
    FROM transacoes
),
intervalos AS (
    SELECT descricao, valor,
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
WHERE dias_desde_ultima BETWEEN 25 AND 35
  AND diferenca_valor < 10
GROUP BY descricao
HAVING COUNT(*) >= 2
ORDER BY ocorrencias DESC;`;

/**
 * @param {string} pergunta - pergunta em português, em texto livre
 * @returns {{sql: string, explicacao: string} | null}
 */
function traduzirPergunta(pergunta) {
  if (!pergunta || typeof pergunta !== "string") return null;
  const norm = normalizar(pergunta);

  if (/assinatur/.test(norm)) {
    return { explicacao: "detectar assinaturas recorrentes", sql: SQL_ASSINATURAS };
  }

  if (/maior gasto|gastei mais|mais car[oa]/.test(norm)) {
    return {
      explicacao: "encontrar o maior gasto registrado",
      sql: `SELECT descricao, valor, data FROM transacoes ORDER BY valor DESC LIMIT 1;`,
    };
  }

  if (/no total|total geral|gasto total/.test(norm)) {
    return {
      explicacao: "somar todos os gastos",
      sql: `SELECT SUM(valor) AS total_geral, COUNT(*) AS transacoes FROM transacoes;`,
    };
  }

  if (/ticket medio|media (de gasto|por categoria)/.test(norm)) {
    return {
      explicacao: "ticket médio por categoria",
      sql: `SELECT c.nome AS categoria, ROUND(AVG(t.valor), 2) AS ticket_medio
FROM transacoes t JOIN categorias c ON t.categoria_id = c.id
GROUP BY c.nome ORDER BY ticket_medio DESC;`,
    };
  }

  if (/categoria.*mais gast|mais gast.*categoria|top categoria|onde gasto mais|por categoria/.test(norm)) {
    return {
      explicacao: "total gasto por categoria",
      sql: `SELECT c.nome AS categoria, SUM(t.valor) AS total, COUNT(*) AS transacoes
FROM transacoes t JOIN categorias c ON t.categoria_id = c.id
GROUP BY c.nome ORDER BY total DESC;`,
    };
  }

  const mes = encontrarMes(norm);
  const categoria = encontrarCategoria(norm);

  if (mes && categoria) {
    const { ini, fim } = MESES[mes];
    return {
      explicacao: `gastos com ${categoria} em ${mes}`,
      sql: `SELECT t.data, t.descricao, t.valor
FROM transacoes t JOIN categorias c ON t.categoria_id = c.id
WHERE c.nome = '${categoria}' AND t.data BETWEEN '${ini}' AND '${fim}'
ORDER BY t.data;`,
    };
  }

  if (mes) {
    const { ini, fim } = MESES[mes];
    return {
      explicacao: `total gasto em ${mes}`,
      sql: `SELECT SUM(valor) AS total, COUNT(*) AS transacoes
FROM transacoes WHERE data BETWEEN '${ini}' AND '${fim}';`,
    };
  }

  if (categoria) {
    return {
      explicacao: `total gasto com ${categoria}`,
      sql: `SELECT SUM(t.valor) AS total, COUNT(*) AS transacoes
FROM transacoes t JOIN categorias c ON t.categoria_id = c.id
WHERE c.nome = '${categoria}';`,
    };
  }

  return null;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { traduzirPergunta, normalizar };
} else {
  window.traduzirPergunta = traduzirPergunta;
}
