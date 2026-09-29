from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import computed_field

if TYPE_CHECKING:
    from app.models.pedido import Pedido
    from app.models.item_cardapio import ItemCardapio

# =====================================================================
# CONCEITO DIDÁTICO: Entidade Dependente (ItemPedido) e Snapshot de Preço
#
# 1. Relação de Composição (1:N):
#    Um Pedido é composto por vários Itens. O ItemPedido não tem sentido
#    de existir isoladamente sem um Pedido pai.
#
# 2. Snapshot de Preço (Historicidade e Imutabilidade):
#    O campo 'preco_unitario' congela o preço do prato no instante exato da compra.
#    Se o restaurante reajustar o preço no cardápio amanhã, o total dos pedidos
#    já realizados no passado NÃO PODE mudar.
#
# 3. Integridade Referencial e Cascade:
#    - FK para 'pedidos.id' com ondelete='CASCADE': se o pedido for excluído,
#      seus itens são deletados automaticamente.
#    - FK para 'itens_cardapio.id': conecta ao catálogo de pratos/bebidas.
# =====================================================================


class ItemPedidoBase(SQLModel):
    """Campos comuns do item de pedido compartilhados entre API e Banco."""
    quantidade: int = Field(
        default=1,
        gt=0,
        description="Quantidade solicitada (deve ser maior que zero)"
    )
    observacao: str | None = Field(
        default=None,
        max_length=150,
        description="Observação do cliente (ex: Sem cebola, carne bem passada)"
    )


class ItemPedido(ItemPedidoBase, table=True):
    """Tabela 'itens_pedido' no banco de dados."""
    __tablename__ = "itens_pedido"

    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(
        foreign_key="pedidos.id",
        index=True,
        ondelete="CASCADE",
        description="Chave estrangeira apontando para o pedido pai"
    )
    item_cardapio_id: int = Field(
        foreign_key="itens_cardapio.id",
        index=True,
        description="Chave estrangeira apontando para o item do cardápio"
    )
    preco_unitario: float = Field(
        gt=0,
        description="Snapshot: valor unitário histórico no momento da compra"
    )

    # Relacionamentos bidirecionais
    pedido: Optional["Pedido"] = Relationship(back_populates="itens")
    item_cardapio: Optional["ItemCardapio"] = Relationship(back_populates="itens_pedido")


class ItemPedidoCreate(ItemPedidoBase):
    """Schema para adicionar um item via sub-recurso POST /pedidos/{id}/itens."""
    item_cardapio_id: int = Field(
        description="ID do prato ou bebida a ser incluído no pedido"
    )


class ItemPedidoCreateInline(ItemPedidoBase):
    """Schema para inclusão de itens diretamente no payload de criação do pedido."""
    item_cardapio_id: int = Field(
        description="ID do prato ou bebida a ser incluído no pedido"
    )


class ItemPedidoUpdate(SQLModel):
    """Schema para atualização de item (PUT/PATCH no sub-recurso)."""
    quantidade: int | None = Field(
        default=None,
        gt=0,
        description="Nova quantidade do item"
    )
    observacao: str | None = Field(
        default=None,
        max_length=150,
        description="Nova observação ou null para limpar"
    )


class ItemPedidoResponse(ItemPedidoBase):
    """Schema retornado pela API nas consultas de itens de pedidos."""
    id: int
    pedido_id: int
    item_cardapio_id: int
    nome_item: str
    preco_unitario: float

    @computed_field
    @property
    def subtotal(self) -> float:
        """Cálculo automático do subtotal (preço unitário * quantidade)."""
        return round(self.preco_unitario * self.quantidade, 2)
