import csv
import random
from datetime import date, timedelta

PRODUTOS = [
("Camiseta Basica", "Vestuario", 39.90),
("Calca Jeans", "Vestuario", 129.90),
("Tenis Esportivo", "Calcados", 199.90),
("Bone", "Acessorios", 49.90),
("Jaqueta Corta-Vento", "Vestuario", 159.90),
("Mochila", "Acessorios", 89.90),
("Meia (par)", "Vestuario", 14.90),
("Chinelo", "Calcados", 34.90),
]

def gerar_vendas(
    caminho_saida: str = "vendas.csv",
    quantidade_linhas: int = 500,
    seed: int = 42
):
    random.seed(seed)

    data_inicial = date(2025, 1, 1)

    with open(
        caminho_saida,
        "w",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        escritor = csv.writer(arquivo)

        escritor.writerow([
            "pedido_id",
            "data",
            "produto",
            "categoria",
            "quantidade",
            "preco_unitario",
            "cliente_id",
        ])

        for pedido_id in range(1, quantidade_linhas + 1):
            produto, categoria, preco = random.choice(PRODUTOS)

            dias_aleatorios = random.randint(0, 269)

            data_venda = (
                data_inicial
                + timedelta(days=dias_aleatorios)
            )

            quantidade = random.randint(1, 5)
            cliente_id = random.randint(1, 120)

            escritor.writerow([
                pedido_id,
                data_venda.isoformat(),
                produto,
                categoria,
                quantidade,
                preco,
                cliente_id,
            ])

    print(
        f"Arquivo '{caminho_saida}' "
        f"gerado com {quantidade_linhas} linhas."
    )


if __name__ == "__main__":
    gerar_vendas()