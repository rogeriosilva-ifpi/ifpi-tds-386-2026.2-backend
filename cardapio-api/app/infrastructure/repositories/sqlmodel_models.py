"""
Modelos ORM de Banco de Dados (SQLModel / SQLAlchemy).

CONCEITO: Modelo de persistência DDL isolado na infraestrutura.
Inspecionado pelo Alembic para controle de versionamento do banco de dados relacional.
"""
from sqlmodel import SQLModel, Field


class ItemCardapioTable(SQLModel, table=True):
    """Tabela de itens do cardápio no banco de dados relacional."""

    __tablename__ = "itens_cardapio"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True, index=True)
    nome: str = Field(
        min_length=2,
        max_length=100,
        description="Nome do prato ou bebida",
    )
    descricao: str | None = Field(
        default=None,
        max_length=255,
        description="Descrição dos ingredientes ou detalhes do item",
    )
    preco: float = Field(
        gt=0,
        description="Preço em reais (deve ser estritamente maior que zero)",
    )
    categoria: str = Field(
        default="Lanches",
        description="Categoria do item: Lanches, Bebidas, Sobremesas, etc.",
    )
    disponivel: bool = Field(
        default=True,
        description="Indica se o item está disponível para pedido",
    )
    tempo_preparo_minutos: int | None = Field(
        default=None,
        ge=1,
        description="Tempo estimado de preparo em minutos (ex: 15, 30)",
    )
