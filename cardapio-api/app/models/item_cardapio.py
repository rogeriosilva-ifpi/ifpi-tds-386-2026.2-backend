from sqlmodel import SQLModel, Field

# =====================================================================
# CONCEITO DIDÁTICO: SQLModel para Itens do Cardápio
# 1. ItemCardapioBase: campos comuns e regras de validação Pydantic.
# 2. ItemCardapio: mapeamento ORM (table=True) na tabela 'itens_cardapio'.
# 3. ItemCardapioCreate / ItemCardapioUpdate / ItemCardapioResponse: DTOs da API.
# =====================================================================


class ItemCardapioBase(SQLModel):
    """Campos comuns compartilhados tanto pelo Banco quanto pela API."""
    nome: str = Field(
        min_length=2, 
        max_length=100, 
        description="Nome do prato ou bebida"
    )
    descricao: str | None = Field(
        default=None, 
        max_length=255, 
        description="Descrição dos ingredientes ou detalhes do item"
    )
    preco: float = Field(
        gt=0, 
        description="Preço em reais (deve ser estritamente maior que zero)"
    )
    categoria: str = Field(
        default="Lanches", 
        description="Categoria do item: Lanches, Bebidas, Sobremesas, etc."
    )
    disponivel: bool = Field(
        default=True, 
        description="Indica se o item está disponível para pedido"
    )
    # Atributo adicionado na evolução de esquema via Migração Alembic:
    tempo_preparo_minutos: int | None = Field(
        default=None, 
        ge=1, 
        description="Tempo estimado de preparo em minutos (ex: 15, 30)"
    )


class ItemCardapio(ItemCardapioBase, table=True):
    """Modelo ORM que mapeia a tabela 'itens_cardapio' no banco de dados."""
    __tablename__ = "itens_cardapio"

    id: int | None = Field(default=None, primary_key=True)


class ItemCardapioCreate(ItemCardapioBase):
    """Schema para validação do corpo da requisição no cadastro (POST)."""
    pass


class ItemCardapioUpdate(SQLModel):
    """Schema para atualização de dados (PUT/PATCH). Permite atualizar campos parciais."""
    nome: str | None = None
    descricao: str | None = None
    preco: float | None = None
    categoria: str | None = None
    disponivel: bool | None = None
    tempo_preparo_minutos: int | None = None


class ItemCardapioResponse(ItemCardapioBase):
    """Schema retornado pela API nas consultas. Garante a presença do campo 'id'."""
    id: int
