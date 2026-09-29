"""Módulo de modelos de dados e esquemas SQLModel organizados por entidade."""
from app.models.item_cardapio import (
    ItemCardapioBase,
    ItemCardapio,
    ItemCardapioCreate,
    ItemCardapioUpdate,
    ItemCardapioResponse,
)
from app.models.cliente import (
    ClienteBase,
    Cliente,
    ClienteCreate,
    ClienteUpdate,
    ClienteResponse,
)
from app.models.item_pedido import (
    ItemPedidoBase,
    ItemPedido,
    ItemPedidoCreate,
    ItemPedidoCreateInline,
    ItemPedidoUpdate,
    ItemPedidoResponse,
)
from app.models.pedido import (
    StatusPedido,
    PedidoBase,
    Pedido,
    PedidoCreate,
    PedidoUpdateStatus,
    PedidoResponse,
    PedidoListResponse,
)

__all__ = [
    # Item Cardápio
    "ItemCardapioBase",
    "ItemCardapio",
    "ItemCardapioCreate",
    "ItemCardapioUpdate",
    "ItemCardapioResponse",
    # Cliente
    "ClienteBase",
    "Cliente",
    "ClienteCreate",
    "ClienteUpdate",
    "ClienteResponse",
    # Item Pedido
    "ItemPedidoBase",
    "ItemPedido",
    "ItemPedidoCreate",
    "ItemPedidoCreateInline",
    "ItemPedidoUpdate",
    "ItemPedidoResponse",
    # Pedido
    "StatusPedido",
    "PedidoBase",
    "Pedido",
    "PedidoCreate",
    "PedidoUpdateStatus",
    "PedidoResponse",
    "PedidoListResponse",
]
