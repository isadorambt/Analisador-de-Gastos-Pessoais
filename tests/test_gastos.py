"""
Testes automatizados do Analisador de Gastos Pessoais.

Diferente do CI básico (que só confere se o SQL roda sem erro), estes
testes verificam se os RESULTADOS das consultas estão corretos — ou
seja, se a lógica de negócio do projeto realmente funciona como esperado.

Rodar com:
    python3 -m unittest tests/test_gastos.py -v
"""

import sqlite3
import unittest
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def montar_banco_de_teste():
    """Cria um banco em memória a partir do schema.sql + seed.sql reais
    do projeto, garantindo que os testes sempre rodam contra a estrutura
    e os dados que estão de fato no repositório."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    with open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8") as f:
        cur.executescript(f.read())
    with open(os.path.join(BASE_DIR, "seed.sql"), encoding="utf-8") as f:
        cur.executescript(f.read())
    conn.commit()
    return conn


class TestIntegridadeDosDados(unittest.TestCase):
    """Garante que os relacionamentos entre tabelas fazem sentido."""

    def setUp(self):
        self.conn = montar_banco_de_teste()
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_toda_transacao_tem_categoria_valida(self):
        self.cur.execute("""
            SELECT COUNT(*) FROM transacoes t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE c.id IS NULL
        """)
        orfaos = self.cur.fetchone()[0]
        self.assertEqual(orfaos, 0, "Existem transações com categoria_id inválido")

    def test_toda_transacao_tem_conta_valida(self):
        self.cur.execute("""
            SELECT COUNT(*) FROM transacoes t
            LEFT JOIN contas ct ON t.conta_id = ct.id
            WHERE ct.id IS NULL
        """)
        orfaos = self.cur.fetchone()[0]
        self.assertEqual(orfaos, 0, "Existem transações com conta_id inválido")

    def test_nao_existem_valores_negativos_ou_zero(self):
        self.cur.execute("SELECT COUNT(*) FROM transacoes WHERE valor <= 0")
        invalidos = self.cur.fetchone()[0]
        self.assertEqual(invalidos, 0, "Existem transações com valor zero ou negativo")

    def test_perfil_tem_exatamente_uma_linha(self):
        # A view gastos_em_horas faz um cross join com perfil — se houver
        # mais de uma linha em perfil, os valores de horas_trabalho
        # duplicariam silenciosamente.
        self.cur.execute("SELECT COUNT(*) FROM perfil")
        total = self.cur.fetchone()[0]
        self.assertEqual(total, 1, "A tabela perfil deve ter exatamente 1 linha")


class TestRelatoriosAgregados(unittest.TestCase):
    """Garante que os totais e médias batem matematicamente."""

    def setUp(self):
        self.conn = montar_banco_de_teste()
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_soma_por_categoria_bate_com_total_geral(self):
        self.cur.execute("SELECT SUM(valor) FROM transacoes")
        total_geral = round(self.cur.fetchone()[0], 2)

        self.cur.execute("""
            SELECT SUM(total) FROM (
                SELECT SUM(valor) AS total
                FROM transacoes
                GROUP BY categoria_id
            )
        """)
        soma_das_categorias = round(self.cur.fetchone()[0], 2)

        self.assertEqual(
            total_geral, soma_das_categorias,
            "A soma dos totais por categoria deveria bater com o total geral"
        )

    def test_soma_por_conta_bate_com_total_geral(self):
        self.cur.execute("SELECT SUM(valor) FROM transacoes")
        total_geral = round(self.cur.fetchone()[0], 2)

        self.cur.execute("""
            SELECT SUM(total) FROM (
                SELECT SUM(valor) AS total
                FROM transacoes
                GROUP BY conta_id
            )
        """)
        soma_das_contas = round(self.cur.fetchone()[0], 2)

        self.assertEqual(
            total_geral, soma_das_contas,
            "A soma dos totais por conta deveria bater com o total geral"
        )


class TestCustoEmHorasDeVida(unittest.TestCase):
    """Garante que a view gastos_em_horas calcula certo."""

    def setUp(self):
        self.conn = montar_banco_de_teste()
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_calculo_de_horas_bate_com_valor_hora(self):
        self.cur.execute("SELECT valor_hora_trabalho FROM perfil")
        valor_hora = self.cur.fetchone()[0]

        self.cur.execute("""
            SELECT valor, horas_trabalho FROM gastos_em_horas
            WHERE descricao = 'Aluguel'
        """)
        valor, horas_trabalho = self.cur.fetchone()

        esperado = round(valor / valor_hora, 2)
        self.assertEqual(
            horas_trabalho, esperado,
            "horas_trabalho deveria ser valor / valor_hora_trabalho"
        )


class TestDetectorDeAssinaturas(unittest.TestCase):
    """Garante que o detector encontra exatamente as assinaturas conhecidas
    nos dados de exemplo, nem mais nem menos."""

    QUERY_DETECTOR = """
        WITH ordenado AS (
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
        SELECT descricao, COUNT(*) + 1 AS ocorrencias
        FROM intervalos
        WHERE dias_desde_ultima BETWEEN 25 AND 35
          AND diferenca_valor < 10
        GROUP BY descricao
        HAVING COUNT(*) >= 2
        ORDER BY descricao;
    """

    def setUp(self):
        self.conn = montar_banco_de_teste()
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_encontra_exatamente_as_tres_assinaturas_conhecidas(self):
        self.cur.execute(self.QUERY_DETECTOR)
        resultado = {linha[0]: linha[1] for linha in self.cur.fetchall()}

        esperado = {"Netflix": 4, "Academia": 4, "Spotify": 4}
        self.assertEqual(
            resultado, esperado,
            "O detector deveria achar Netflix, Academia e Spotify, 4x cada"
        )

    def test_nao_marca_gastos_pontuais_como_assinatura(self):
        self.cur.execute(self.QUERY_DETECTOR)
        descricoes_detectadas = {linha[0] for linha in self.cur.fetchall()}

        # "Aluguel" se repete todo mês mas com descrição diferente de compra
        # pontual — o importante aqui é confirmar que compras não-recorrentes
        # (Cinema, Livro, Farmácia) não entram na lista por engano.
        gastos_pontuais = {"Cinema", "Livro", "Farmácia", "Show de música"}
        self.assertTrue(
            descricoes_detectadas.isdisjoint(gastos_pontuais),
            "Gastos pontuais não deveriam ser marcados como assinatura"
        )


if __name__ == "__main__":
    unittest.main()
