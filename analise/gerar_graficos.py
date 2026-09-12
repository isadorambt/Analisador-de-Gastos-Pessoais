"""
Gera os gráficos usados no README e no notebook, a partir das funções
de analysis.py. Rodar com: python3 analise/gerar_graficos.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analysis as an

PASTA_GRAFICOS = Path(__file__).resolve().parent / "graficos"
PASTA_GRAFICOS.mkdir(exist_ok=True)

sns.set_theme(style="darkgrid", palette="crest")
CORES = {"fig": "#10151C", "eixo": "#1A2029", "texto": "#EDE7DB"}


def estilizar(fig, ax):
    fig.patch.set_facecolor(CORES["fig"])
    ax.set_facecolor(CORES["eixo"])
    ax.tick_params(colors=CORES["texto"])
    ax.xaxis.label.set_color(CORES["texto"])
    ax.yaxis.label.set_color(CORES["texto"])
    ax.title.set_color(CORES["texto"])
    for spine in ax.spines.values():
        spine.set_color("#2B3440")


def grafico_total_por_categoria(df):
    dados = an.total_por_categoria(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=dados, y="categoria", x="total", ax=ax, color="#C9A15A")
    ax.set_title("Total gasto por categoria")
    ax.set_xlabel("Total (R$)")
    ax.set_ylabel("")
    estilizar(fig, ax)
    fig.tight_layout()
    fig.savefig(PASTA_GRAFICOS / "total_por_categoria.png", dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def grafico_gasto_mensal(df):
    dados = an.gasto_mensal(df)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.lineplot(data=dados, x="mes", y="total", ax=ax, marker="o", color="#4FA394", linewidth=2.5)
    ax.set_title("Gasto total por mês")
    ax.set_xlabel("")
    ax.set_ylabel("Total (R$)")
    estilizar(fig, ax)
    fig.tight_layout()
    fig.savefig(PASTA_GRAFICOS / "gasto_mensal.png", dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def grafico_assinaturas(df):
    dados = an.detectar_assinaturas(df)
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=dados, y="descricao", x="valor_medio_atual", ax=ax, color="#C9695A")
    ax.set_title("Assinaturas recorrentes detectadas")
    ax.set_xlabel("Valor médio (R$)")
    ax.set_ylabel("")
    estilizar(fig, ax)
    fig.tight_layout()
    fig.savefig(PASTA_GRAFICOS / "assinaturas.png", dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    conn = an.conectar()
    df = an.carregar_transacoes(conn)

    grafico_total_por_categoria(df)
    grafico_gasto_mensal(df)
    grafico_assinaturas(df)

    print(f"3 gráficos gerados em {PASTA_GRAFICOS}")


if __name__ == "__main__":
    main()
