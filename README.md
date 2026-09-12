# 💰 Analisador de Gastos Pessoais

Projeto de estudo em SQL: um banco de dados simples pra registrar e analisar
gastos pessoais, usando SQLite.

## Estrutura do banco

- **categorias** — tipos de gasto (Alimentação, Transporte, Lazer, etc.)
- **contas** — de onde saiu o dinheiro (cartão, conta corrente, dinheiro)
- **transacoes** — cada gasto individual, ligado a uma categoria e uma conta

## Como usar

```bash
# criar o banco a partir do zero
sqlite3 gastos.db < schema.sql

# popular com dados de exemplo
sqlite3 gastos.db < seed.sql

# rodar as consultas de exemplo
sqlite3 gastos.db < consultas.sql
```

(Se não tiver o `sqlite3` instalado, dá pra rodar os mesmos scripts com o
módulo `sqlite3` do Python, que já vem embutido.)

## Arquivos

| Arquivo         | O que faz                                      |
|-----------------|-------------------------------------------------|
| `schema.sql`    | Cria as tabelas e seus relacionamentos          |
| `seed.sql`      | Popula o banco com dados de exemplo             |
| `consultas.sql` | Consultas de exemplo, do básico ao avançado     |

## Consultas de exemplo incluídas

- Listagem simples e com filtros (`WHERE`, `ORDER BY`)
- Junção de tabelas (`JOIN`) pra mostrar nomes em vez de IDs
- Totais e médias por categoria e por conta (`GROUP BY`, `SUM`, `AVG`)
- Filtro por período de datas
- Top 3 maiores gastos

## Próximos passos (ideias de evolução)

- [ ] Comparar gasto mês a mês
- [ ] Adicionar uma tabela de orçamento (limite por categoria) e consultar
      se estourou ou não
- [ ] Gerar gráficos a partir das consultas com Python + matplotlib
- [ ] Criar uma view para "resumo mensal"
