"""
Entidades e Modelos do Cardápio unificados via SQLModel.

CONVENÇÃO: Hierarquia canônica do SQLModel/FastAPI unificando o modelo de domínio,
a tabela de banco de dados relacional (DDL/Alembic) e os schemas de validação/serialização (DTOs).
"""
from typing import Any
from sqlmodel import SQLModel, Field
from pydantic import ValidationError
from app.domain.errors import RegraVioladaError


class ItemCardapioBase(SQLModel):
    """Campos base compartilhados entre a entidade/tabela e os schemas de API."""

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


class ItemCardapio(ItemCardapioBase, table=True):
    """Entidade de domínio e modelo de tabela relacional unificados via SQLModel."""

    __tablename__ = "itens_cardapio"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True, index=True)

    def __init__(self, **data: Any) -> None:
        if not data:
            super().__init__()
            return

        try:
            super().__init__(**data)
        except ValidationError as e:
            for err in e.errors():
                loc = err["loc"][0] if err["loc"] else ""
                if loc == "nome":
                    raise RegraVioladaError(
                        "O nome do item deve ter no mínimo 2 caracteres.",
                        codigo="NOME_INVALIDO",
                    ) from e
                if loc == "preco":
                    raise RegraVioladaError(
                        "O preço do item deve ser estritamente maior que zero.",
                        codigo="PRECO_INVALIDO",
                    ) from e
                if loc == "tempo_preparo_minutos":
                    raise RegraVioladaError(
                        "O tempo estimado de preparo deve ser de no mínimo 1 minuto.",
                        codigo="TEMPO_PREPARO_INVALIDO",
                    ) from e
            raise
        self.validar()

    def validar(self) -> None:
        """Garante as invariantes de negócio da entidade."""
        if hasattr(self, "nome") and self.nome is not None:
            if len(self.nome.strip()) < 2:
                raise RegraVioladaError(
                    "O nome do item deve ter no mínimo 2 caracteres.",
                    codigo="NOME_INVALIDO",
                )
        if hasattr(self, "preco") and self.preco is not None:
            if self.preco <= 0:
                raise RegraVioladaError(
                    "O preço do item deve ser estritamente maior que zero.",
                    codigo="PRECO_INVALIDO",
                )
        if hasattr(self, "tempo_preparo_minutos") and self.tempo_preparo_minutos is not None:
            if self.tempo_preparo_minutos < 1:
                raise RegraVioladaError(
                    "O tempo estimado de preparo deve ser de no mínimo 1 minuto.",
                    codigo="TEMPO_PREPARO_INVALIDO",
                )

    def alternar_disponibilidade(self) -> None:
        """Alterna a disponibilidade do item (disponível <-> esgotado)."""
        self.disponivel = not self.disponivel

    def atualizar(
        self,
        nome: str | None = None,
        descricao: str | None = None,
        preco: float | None = None,
        categoria: str | None = None,
        disponivel: bool | None = None,
        tempo_preparo_minutos: int | None = None,
    ) -> None:
        """Atualiza campos fornecidos e revalida as invariantes."""
        if nome is not None:
            self.nome = nome
        if descricao is not None:
            self.descricao = descricao
        if preco is not None:
            self.preco = preco
        if categoria is not None:
            self.categoria = categoria
        if disponivel is not None:
            self.disponivel = disponivel
        if tempo_preparo_minutos is not None:
            self.tempo_preparo_minutos = tempo_preparo_minutos

        self.validar()


class ItemCardapioCreate(ItemCardapioBase):
    """Schema para validação do corpo da requisição no cadastro (POST)."""
    pass


class ItemCardapioUpdate(SQLModel):
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
