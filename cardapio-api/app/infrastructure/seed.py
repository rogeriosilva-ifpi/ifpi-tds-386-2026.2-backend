"""
Serviço de Inicialização e Seed do Banco de Dados.
"""
from sqlmodel import Session, select
from app.infrastructure.repositories.sqlmodel_models import ItemCardapioTable


DADOS_INICIAIS = [
    ItemCardapioTable(
        nome="Filé com Fritas",
        descricao="Filé mignon grelhado em tiras, servido com batatas fritas crocantes.",
        preco=38.50,
        categoria="Lanches",
        disponivel=True,
        tempo_preparo_minutos=25,
    ),
    ItemCardapioTable(
        nome="Pão c/ Carne de Sol (3und)",
        descricao="Mini pães recheados com carne de sol desfiada e nata especial.",
        preco=22.00,
        categoria="Lanches",
        disponivel=True,
        tempo_preparo_minutos=15,
    ),
    ItemCardapioTable(
        nome="Pastel de Queijo Coalho (6und)",
        descricao="Pastéis fritos na hora com recheio de queijo coalho nordestino.",
        preco=18.00,
        categoria="Lanches",
        disponivel=False,  # Demonstrar prato esgotado
        tempo_preparo_minutos=12,
    ),
    ItemCardapioTable(
        nome="Suco de Caju da Terra (500ml)",
        descricao="Suco natural de caju fresco da região de Teresina.",
        preco=8.50,
        categoria="Bebidas",
        disponivel=True,
        tempo_preparo_minutos=5,
    ),
    ItemCardapioTable(
        nome="Pudim de Leite Condensado",
        descricao="Fatia generosa de pudim tradicional com calda de caramelo.",
        preco=10.00,
        categoria="Sobremesas",
        disponivel=True,
        tempo_preparo_minutos=2,
    ),
]


def popular_seed_se_vazio(sessao: Session) -> None:
    """Insere os pratos demonstrativos didáticos caso o banco esteja vazio."""
    itens_existentes = sessao.exec(select(ItemCardapioTable)).first()
    if not itens_existentes:
        sessao.add_all(DADOS_INICIAIS)
        sessao.commit()
