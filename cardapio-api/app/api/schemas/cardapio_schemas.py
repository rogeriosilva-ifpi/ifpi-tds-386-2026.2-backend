"""
Schemas Pydantic para validação de entrada e serialização de saída (DTOs).

CONCEITO: Schemas desacoplados de persistência de banco de dados.
"""
from pydantic import BaseModel, Field, ConfigDict


class ItemCardapioBase(BaseModel):
    """Campos base compartilhados entre os schemas de API."""

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


class ItemCardapioCreate(ItemCardapioBase):
    """Schema para validação do corpo da requisição no cadastro (POST)."""
    pass


class ItemCardapioUpdate(BaseModel):
    """Schema para atualização de dados (PUT/PATCH). Permite atualização parcial."""

    nome: str | None = Field(default=None, min_length=2, max_length=100)
    descricao: str | None = Field(default=None, max_length=255)
    preco: float | None = Field(default=None, gt=0)
    categoria: str | None = None
    disponivel: bool | None = None
    tempo_preparo_minutos: int | None = Field(default=None, ge=1)


class ItemCardapioResponse(ItemCardapioBase):
    """Schema retornado pela API nas consultas. Garante a presença do campo 'id'."""

    id: int

    model_config = ConfigDict(from_attributes=True)
