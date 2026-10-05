import sys
from pathlib import Path

import pandas as pd

import matplotlib

# Permite gerar os graficos sem abrir uma janela.

matplotlib.use("Agg")

import matplotlib.pyplot as plt

COLUNAS_OBRIGATORIAS = {
"pedido_id",
"data",
"produto",
"categoria",
"quantidade",
"preco_unitario",
"cliente_id",
}

class AnalisadorVendas:
    """
    Classe responsavel por carregar e analisar os dados de vendas.
    """

    def __init__(self, caminho_csv: str):
        self.caminho_csv = Path(caminho_csv)

        if not self.caminho_csv.exists():
            raise FileNotFoundError(
                f"\nNao encontrei o arquivo "
                f"'{self.caminho_csv}'.\n"
                "Rode primeiro:\n"
                "    python gerar_dados.py\n"
            )

        try:
            self.df = pd.read_csv(
                self.caminho_csv,
                parse_dates=["data"]
            )
        except Exception as erro:
            raise ValueError(
                f"Nao foi possivel ler o CSV: {erro}"
            ) from erro

        self._validar_colunas()
        self._preparar_dados()

    def _validar_colunas(self):
        colunas_encontradas = set(self.df.columns)

        faltando = (
            COLUNAS_OBRIGATORIAS
            - colunas_encontradas
        )

        if faltando:
            raise ValueError(
                "O CSV nao possui todas as colunas necessarias.\n"
                f"Colunas faltando: {', '.join(sorted(faltando))}"
            )

    def _preparar_dados(self):
        if self.df.empty:
            raise ValueError(
                "O arquivo CSV esta vazio."
            )

        if self.df["quantidade"].isna().any():
            raise ValueError(
                "Existem valores vazios na coluna 'quantidade'."
            )

        if self.df["preco_unitario"].isna().any():
            raise ValueError(
                "Existem valores vazios na coluna "
                "'preco_unitario'."
            )

        if (self.df["quantidade"] <= 0).any():
            raise ValueError(
                "A coluna 'quantidade' possui valores "
                "menores ou iguais a zero."
            )

        if (self.df["preco_unitario"] < 0).any():
            raise ValueError(
                "A coluna 'preco_unitario' possui "
                "valores negativos."
            )

        self.df["valor_total"] = (
            self.df["quantidade"]
            * self.df["preco_unitario"]
        )

# ==========================================================
# METRICAS
# ==========================================================

    def faturamento_total(self) -> float:
        return float(
            self.df["valor_total"].sum()
        )

    def ticket_medio(self) -> float:
        """
        Calcula o ticket medio por pedido,
        e nao por linha do CSV.
        """

        faturamento_por_pedido = (
            self.df
            .groupby("pedido_id")["valor_total"]
            .sum()
        )

        if faturamento_por_pedido.empty:
            return 0.0

        return float(
            faturamento_por_pedido.mean()
        )

    def total_pedidos(self) -> int:
        return int(
            self.df["pedido_id"].nunique()
        )

    def produtos_mais_vendidos(
        self,
        top_n: int = 5
    ) -> pd.Series:

        if top_n <= 0:
            raise ValueError(
                "top_n precisa ser maior que zero."
            )

        return (
            self.df
            .groupby("produto")["quantidade"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
        )

    def faturamento_por_categoria(self) -> pd.Series:
        return (
            self.df
            .groupby("categoria")["valor_total"]
            .sum()
            .sort_values(ascending=False)
        )

    def vendas_por_dia_da_semana(self) -> pd.Series:
        dias = [
            "Segunda",
            "Terca",
            "Quarta",
            "Quinta",
            "Sexta",
            "Sabado",
            "Domingo",
        ]

        contagem = (
            self.df["data"]
            .dt.dayofweek
            .value_counts()
            .reindex(range(7), fill_value=0)
            .sort_index()
        )

        contagem.index = [
            dias[indice]
            for indice in contagem.index
        ]

        return contagem

    def faturamento_por_mes(self) -> pd.Series:
        return (
            self.df
            .groupby(
                self.df["data"].dt.to_period("M")
            )["valor_total"]
            .sum()
        )

# ==========================================================
# RESUMO
# ==========================================================

    def imprimir_resumo(self):
        print("=" * 60)
        print("RESUMO DE VENDAS".center(60))
        print("=" * 60)

        print(
            f"Faturamento total: "
            f"R$ {self.faturamento_total():,.2f}"
        )

        print(
            f"Ticket medio:      "
            f"R$ {self.ticket_medio():,.2f}"
        )

        print(
            f"Total de pedidos:  "
            f"{self.total_pedidos()}"
        )

        print("\nTop produtos mais vendidos:")

        for produto, quantidade in (
            self.produtos_mais_vendidos().items()
        ):
            print(
                f"  {produto:<25} "
                f"{quantidade} unidades"
            )

        print("\nFaturamento por categoria:")

        for categoria, valor in (
            self.faturamento_por_categoria().items()
        ):
            print(
                f"  {categoria:<15} "
                f"R$ {valor:,.2f}"
            )

        vendas_dia = (
            self.vendas_por_dia_da_semana()
        )

        dia_mais_forte = vendas_dia.idxmax()

        print(
            f"\nDia da semana com mais pedidos: "
            f"{dia_mais_forte}"
        )

        print("=" * 60)

# ==========================================================
# GRAFICOS
# ==========================================================

def gerar_graficos(
    self,
    pasta_saida: str = "."
):
    pasta_saida = Path(pasta_saida)

    pasta_saida.mkdir(
        parents=True,
        exist_ok=True
    )

    self._grafico_top_produtos(
        pasta_saida
    )

    self._grafico_faturamento_mensal(
        pasta_saida
    )

    self._grafico_pedidos_por_dia(
        pasta_saida
    )

    print(
        f"\nGraficos salvos em:\n"
        f"{pasta_saida.resolve()}"
    )

def _grafico_top_produtos(
    self,
    pasta_saida: Path
):
    plt.figure(figsize=(8, 5))

    dados = (
        self.produtos_mais_vendidos()
        .sort_values()
    )

    dados.plot(
        kind="barh",
        color="#4C72B0"
    )

    plt.title(
        "Produtos mais vendidos (unidades)"
    )

    plt.xlabel(
        "Quantidade vendida"
    )

    plt.ylabel("Produto")

    plt.tight_layout()

    plt.savefig(
        pasta_saida / "top_produtos.png",
        dpi=120
    )

    plt.close()

def _grafico_faturamento_mensal(
    self,
    pasta_saida: Path
):
    plt.figure(figsize=(8, 5))

    faturamento_mensal = (
        self.faturamento_por_mes()
        .copy()
    )

    faturamento_mensal.index = (
        faturamento_mensal.index.astype(str)
    )

    faturamento_mensal.plot(
        kind="line",
        marker="o",
        color="#55A868"
    )

    plt.title(
        "Faturamento por mes"
    )

    plt.xlabel("Mes")
    plt.ylabel("Faturamento (R$)")

    plt.xticks(rotation=45)

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        pasta_saida / "faturamento_mensal.png",
        dpi=120
    )

    plt.close()

def _grafico_pedidos_por_dia(
    self,
    pasta_saida: Path
):
    plt.figure(figsize=(8, 5))

    dados = (
        self.vendas_por_dia_da_semana()
    )

    dados.plot(
        kind="bar",
        color="#C44E52"
    )

    plt.title(
        "Pedidos por dia da semana"
    )

    plt.xlabel(
        "Dia da semana"
    )

    plt.ylabel(
        "Numero de pedidos"
    )

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        pasta_saida / "pedidos_por_dia.png",
        dpi=120
    )

    plt.close()

def main():
    """
    Permite executar:

        python analise_vendas.py

    ou:

        python analise_vendas.py meu_arquivo.csv
    """

    caminho_csv = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "vendas.csv"
    )

    try:
        analisador = AnalisadorVendas(
            caminho_csv
        )

        analisador.imprimir_resumo()

        analisador.gerar_graficos()

    except FileNotFoundError as erro:
        print(erro)
        sys.exit(1)

    except ValueError as erro:
        print(
            f"\nErro nos dados: {erro}"
        )
        sys.exit(1)

    except Exception as erro:
        print(
            f"\nOcorreu um erro inesperado: {erro}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()