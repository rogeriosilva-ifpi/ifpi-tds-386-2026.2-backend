from sqlmodel import SQLModel, Field

# =====================================================================
# CONCEITO: SQLModel (União entre Pydantic e SQLAlchemy)
# 1. Classes que herdam de SQLModel são Schemas Pydantic por padrão (validação).
# 2. Ao adicionar table=True, a classe também se torna uma Tabela no Banco de Dados.
# Isso elimina duplicação de código e simplifica o aprendizado.
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


# =====================================================================
# CONCEITO: Modelo ORM (Tabela no SQLite)
# table=True avisa o SQLModel que esta classe vira uma tabela real no banco.
# Note que o 'id' só existe aqui e no Response, não no Create (pois é autoincrementado).
# =====================================================================
class ItemCardapio(ItemCardapioBase, table=True):
    __tablename__ = "itens_cardapio"

    id: int | None = Field(default=None, primary_key=True)


# =====================================================================
# CONCEITO: Schemas de Validação de Entrada e Saída (DTOs)
# - ItemCardapioCreate: o que o cliente DEVE enviar no POST (sem o id).
# - ItemCardapioUpdate: campos opcionais que podem ser atualizados no PUT/PATCH.
# - ItemCardapioResponse: o que a API GARANTE que vai devolver (sempre com id).
# =====================================================================
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


class ItemCardapioResponse(ItemCardapioBase):
    """Schema retornado pela API nas consultas. Garante a presença do campo 'id'."""
    id: int
