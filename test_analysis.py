"""
Testes do módulo de análise em pandas (analise/analysis.py).

O ponto central aqui: várias dessas funções reimplementam em pandas algo
que já existe em SQL (consultas.sql). Os testes comparam os dois
resultados e garantem que batem — ou seja, provam que a lógica está
correta nas DUAS implementações, não só "rodou sem erro".

Rodar com:
    python3 -m unittest tests/test_analysis.py -v
"""

import os
import sqlite3
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "analise"))

import analysis as an  # noqa: E402


def montar_banco_de_teste():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    with open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8") as f:
        cur.executescript(f.read())
    with open(os.path.join(BASE_DIR, "seed.sql"), encoding="utf-8") as f:
        cur.executescript(f.read())
    conn.commit()
    return conn


class TestTotalPorCategoria(unittest.TestCase):
    """Compara o resultado do pandas com a mesma agregação feita em SQL puro."""

    def setUp(self):
        self.conn = montar_banco_de_teste()
        self.df = an.carregar_transacoes(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_total_por_categoria_bate_com_sql(self):
        resultado_pandas = an.total_por_categoria(self.df)

        resultado_sql = self.conn.execute("""
            SELECT c.nome, SUM(t.valor)
            FROM transacoes t
            JOIN categorias c ON t.categoria_id = c.id
            GROUP BY c.nome
        """).fetchall()
        totais_sql = {nome: round(total, 2) for nome, total in resultado_sql}

        for _, linha in resultado_pandas.iterrows():
            with self.subTest(categoria=linha["categoria"]):
                self.assertEqual(
                    round(linha["total"], 2),
                    totais_sql[linha["categoria"]],
                    f"Total de {linha['categoria']} não bate entre pandas e SQL",
                )

    def test_soma_geral_bate_com_soma_das_categorias(self):
        resultado = an.total_por_categoria(self.df)
        self.assertAlmostEqual(
            resultado["total"].sum(), self.df["valor"].sum(), places=2
        )


class TestCustoEmHoras(unittest.TestCase):
    def setUp(self):
        self.conn = montar_banco_de_teste()
        self.df = an.carregar_transacoes(self.conn)
        self.valor_hora = an.carregar_valor_hora(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_calculo_bate_com_a_view_sql(self):
        resultado_pandas = an.custo_em_horas(self.df, self.valor_hora)
        linha_aluguel = resultado_pandas[resultado_pandas["descricao"] == "Aluguel"].iloc[0]

        horas_sql = self.conn.execute("""
            SELECT horas_trabalho FROM gastos_em_horas WHERE descricao = 'Aluguel'
        """).fetchone()[0]

        self.assertEqual(linha_aluguel["horas_trabalho"], horas_sql)


class TestDetectorDeAssinaturas(unittest.TestCase):
    """O teste mais importante do módulo: confirma que o detector em pandas
    encontra exatamente as mesmas assinaturas que o detector em SQL
    (implementado com window functions em consultas.sql)."""

    def setUp(self):
        self.conn = montar_banco_de_teste()
        self.df = an.carregar_transacoes(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_encontra_as_mesmas_assinaturas_que_o_sql(self):
        resultado_pandas = an.detectar_assinaturas(self.df)
        encontradas_pandas = dict(
            zip(resultado_pandas["descricao"], resultado_pandas["ocorrencias"])
        )

        resultado_sql = self.conn.execute("""
            WITH ordenado AS (
                SELECT descricao, data, valor,
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
            SELECT descricao, COUNT(*) + 1
            FROM intervalos
            WHERE dias_desde_ultima BETWEEN 25 AND 35 AND diferenca_valor < 10
            GROUP BY descricao
            HAVING COUNT(*) >= 2
        """).fetchall()
        encontradas_sql = dict(resultado_sql)

        self.assertEqual(
            encontradas_pandas, encontradas_sql,
            "pandas e SQL deveriam encontrar exatamente as mesmas assinaturas"
        )

    def test_encontra_netflix_academia_spotify(self):
        resultado = an.detectar_assinaturas(self.df)
        nomes = set(resultado["descricao"])
        self.assertEqual(nomes, {"Netflix", "Academia", "Spotify"})


class TestProjecaoDeSaldo(unittest.TestCase):
    def setUp(self):
        self.conn = montar_banco_de_teste()
        self.df = an.carregar_transacoes(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_saldo_projetado_diminui_ao_longo_do_tempo(self):
        projecao = an.projecao_saldo(self.df, saldo_atual=5000, dias_futuros=10)
        # o saldo projetado no dia 10 deve ser menor que no dia 1
        self.assertLess(
            projecao.iloc[-1]["saldo_projetado"],
            projecao.iloc[0]["saldo_projetado"],
        )

    def test_media_diaria_e_positiva(self):
        projecao = an.projecao_saldo(self.df, saldo_atual=5000)
        self.assertGreater(projecao.attrs["media_diaria"], 0)


if __name__ == "__main__":
    unittest.main()
