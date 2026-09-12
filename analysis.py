"""
Análise de gastos pessoais com pandas.

Este módulo carrega os dados do gastos.db (o mesmo banco usado no
playground SQL) e oferece funções de análise equivalentes às consultas
SQL do projeto — mas usando pandas. A ideia é mostrar o mesmo problema
resolvido com duas ferramentas diferentes, e os testes (tests/test_analysis.py)
confirmam que os dois caminhos chegam ao mesmo resultado.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "gastos.db"


def conectar(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Abre uma conexão com o gastos.db."""
    return sqlite3.connect(db_path)


def carregar_transacoes(conn: sqlite3.Connection) -> pd.DataFrame:
    """Carrega todas as transações já com o nome da categoria e da conta
    (em vez dos IDs), prontas pra análise em pandas."""
    query = """
        SELECT
            t.id,
            t.data,
            t.descricao,
            t.valor,
            c.nome AS categoria,
            ct.nome AS conta
        FROM transacoes t
        JOIN categorias c ON t.categoria_id = c.id
        JOIN contas ct ON t.conta_id = ct.id
        ORDER BY t.data
    """
    df = pd.read_sql_query(query, conn, parse_dates=["data"])
    return df


def carregar_valor_hora(conn: sqlite3.Connection) -> float:
    """Lê o valor da hora de trabalho cadastrado em perfil."""
    return pd.read_sql_query("SELECT valor_hora_trabalho FROM perfil", conn).iloc[0, 0]


def total_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Total gasto e número de transações por categoria, do maior pro menor."""
    resultado = (
        df.groupby("categoria")
        .agg(total=("valor", "sum"), transacoes=("valor", "count"))
        .sort_values("total", ascending=False)
        .reset_index()
    )
    return resultado


def ticket_medio_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Valor médio por transação, em cada categoria."""
    resultado = (
        df.groupby("categoria")["valor"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .reset_index(name="ticket_medio")
    )
    return resultado


def gasto_mensal(df: pd.DataFrame) -> pd.DataFrame:
    """Total gasto por mês — a base pra ver tendência ao longo do tempo."""
    serie = (
        df.set_index("data")["valor"]
        .resample("MS")  # MS = início de cada mês
        .sum()
        .reset_index()
        .rename(columns={"data": "mes", "valor": "total"})
    )
    return serie


def custo_em_horas(df: pd.DataFrame, valor_hora: float) -> pd.DataFrame:
    """Equivalente em pandas da view gastos_em_horas do SQL."""
    resultado = df.copy()
    resultado["horas_trabalho"] = (resultado["valor"] / valor_hora).round(2)
    return resultado.sort_values("horas_trabalho", ascending=False)


def detectar_assinaturas(df: pd.DataFrame) -> pd.DataFrame:
    """Reimplementação em pandas do detector de assinaturas que fizemos em
    SQL com window functions (LAG). Agrupa por descrição, ordena por data,
    e usa .diff() pra calcular o intervalo de dias e a variação de valor
    entre cobranças consecutivas de mesma descrição."""
    ordenado = df.sort_values(["descricao", "data"]).copy()

    ordenado["dias_desde_ultima"] = (
        ordenado.groupby("descricao")["data"].diff().dt.days
    )
    ordenado["diferenca_valor"] = (
        ordenado.groupby("descricao")["valor"].diff().abs()
    )

    candidatos = ordenado[
        (ordenado["dias_desde_ultima"].between(25, 35))
        & (ordenado["diferenca_valor"] < 10)
    ]

    resultado = (
        candidatos.groupby("descricao")
        .agg(
            ocorrencias=("descricao", "size"),
            intervalo_medio_dias=("dias_desde_ultima", "mean"),
            valor_medio_atual=("valor", "mean"),
        )
        .reset_index()
    )
    # +1 porque a primeira ocorrência de cada assinatura não tem "anterior"
    # pra comparar, então não entra na contagem do diff — mas existiu.
    resultado["ocorrencias"] = resultado["ocorrencias"] + 1
    resultado["intervalo_medio_dias"] = resultado["intervalo_medio_dias"].round(1)
    resultado["valor_medio_atual"] = resultado["valor_medio_atual"].round(2)

    return resultado[resultado["ocorrencias"] >= 3].sort_values(
        "ocorrencias", ascending=False
    ).reset_index(drop=True)


def projecao_saldo(
    df: pd.DataFrame, saldo_atual: float, dias_futuros: int = 30
) -> pd.DataFrame:
    """Projeta gasto futuro com base na média móvel de gasto diário dos
    últimos 30 dias de dados, e estima em quantos dias o saldo informado
    se esgotaria no ritmo atual."""
    diario = (
        df.set_index("data")["valor"]
        .resample("D")
        .sum()
    )
    media_diaria = diario.tail(30).mean()

    dias_ate_zerar = (
        round(saldo_atual / media_diaria) if media_diaria > 0 else None
    )

    projecao = pd.DataFrame({
        "dia": range(1, dias_futuros + 1),
    })
    projecao["gasto_acumulado_projetado"] = (
        projecao["dia"] * media_diaria
    ).round(2)
    projecao["saldo_projetado"] = (
        saldo_atual - projecao["gasto_acumulado_projetado"]
    ).round(2)

    projecao.attrs["media_diaria"] = round(media_diaria, 2)
    projecao.attrs["dias_ate_zerar"] = dias_ate_zerar

    return projecao
