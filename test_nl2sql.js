/**
 * Testes do tradutor de linguagem natural (nl2sql.js).
 * Roda com: node tests/test_nl2sql.js
 * Não depende de nenhum pacote externo — só o Node puro.
 */

const assert = require("assert");
const { traduzirPergunta } = require("../nl2sql.js");

let testesRodados = 0;

function testar(descricao, fn) {
  fn();
  testesRodados += 1;
  console.log(`  ok - ${descricao}`);
}

testar("reconhece pergunta sobre categoria", () => {
  const r = traduzirPergunta("Quanto gastei com Alimentação?");
  assert.ok(r, "deveria reconhecer a pergunta");
  assert.ok(r.sql.includes("c.nome = 'Alimentação'"));
});

testar("reconhece categoria mesmo sem acento", () => {
  const r = traduzirPergunta("quanto gastei com alimentacao");
  assert.ok(r);
  assert.ok(r.sql.includes("c.nome = 'Alimentação'"));
});

testar("reconhece pergunta sobre assinaturas", () => {
  const r = traduzirPergunta("Quais são minhas assinaturas?");
  assert.ok(r);
  assert.ok(r.sql.includes("PARTITION BY descricao"));
});

testar("reconhece pergunta sobre o maior gasto", () => {
  const r = traduzirPergunta("Qual foi meu maior gasto?");
  assert.ok(r);
  assert.ok(r.sql.includes("ORDER BY valor DESC LIMIT 1"));
});

testar("reconhece pergunta sobre total geral", () => {
  const r = traduzirPergunta("Quanto gastei no total?");
  assert.ok(r);
  assert.ok(r.sql.includes("SUM(valor) AS total_geral"));
});

testar("reconhece pergunta sobre um mês específico", () => {
  const r = traduzirPergunta("Quanto gastei em agosto?");
  assert.ok(r);
  assert.ok(r.sql.includes("'2026-08-01'"));
  assert.ok(r.sql.includes("'2026-08-31'"));
});

testar("reconhece categoria + mês juntos", () => {
  const r = traduzirPergunta("Quanto gastei com Saúde em julho?");
  assert.ok(r);
  assert.ok(r.sql.includes("c.nome = 'Saúde'"));
  assert.ok(r.sql.includes("'2026-07-01'"));
});

testar("reconhece pergunta sobre total por categoria", () => {
  const r = traduzirPergunta("Quais categorias eu mais gasto?");
  assert.ok(r);
  assert.ok(r.sql.includes("GROUP BY c.nome"));
});

testar("retorna null pra pergunta não reconhecida", () => {
  const r = traduzirPergunta("qual a capital da frança");
  assert.strictEqual(r, null);
});

testar("retorna null pra texto vazio", () => {
  assert.strictEqual(traduzirPergunta(""), null);
  assert.strictEqual(traduzirPergunta(null), null);
});

console.log(`\n${testesRodados} testes do tradutor de linguagem natural passaram.`);
