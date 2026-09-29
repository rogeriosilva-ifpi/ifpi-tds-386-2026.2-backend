from datetime import datetime, timezone
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from app.models.item_pedido import (
    ItemPedido,
    ItemPedidoCreateInline,
    ItemPedidoResponse,
)

if TYPE_CHECKING:
    from app.models.cliente import Cliente

# =====================================================================
# CONCEITO DIDÁTICO: Entidade Pedido e Máquina de Estados
#
# 1. Relacionamento 1:N (Cliente -> Pedidos):
#    Um cliente pode ter vários pedidos ao longo do tempo. Cada pedido
#    pertence obrigatoriamente a um único cliente ('cliente_id').
#
# 2. Composição e Cascade Delete (Pedido -> ItensPedido):
#    O pedido é a entidade agregadora dos itens. Quando o pedido é deletado,
#    seus itens são deletados em cascata via banco (ON DELETE CASCADE)
#    e via ORM (cascade_delete=True).
#
# 3. Status do Pedido (Enum e Ciclo de Vida):
#    Garante integridade nas transições:
#    CRIADO -> CONFIRMADO -> EM_PREPARO -> PRONTO -> ENTREGUE
#    (ou CANCELADO caso ainda não esteja em preparo).
#
# 4. Total Consolidado:
#    O atributo 'valor_total' mantém o valor monetário total sincronizado
#    a cada alteração dos itens, evitando recálculos pesados em listagens.
# =====================================================================


class StatusPedido(str, Enum):
    """Estados possíveis do ciclo de vida de um pedido no restaurante."""
    CRIADO = "CRIADO"
    CONFIRMADO = "CONFIRMADO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


class PedidoBase(SQLModel):
    """Campos base do Pedido compartilhados entre API e Banco."""
    observacoes: str | None = Field(
        default=None,
        max_length=255,
        description="Instruções gerais para entrega ou preparo"
    )


class Pedido(PedidoBase, table=True):
    """Tabela 'pedidos' no banco de dados."""
    __tablename__ = "pedidos"

    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(
        foreign_key="clientes.id",
        index=True,
        ondelete="CASCADE",
        description="Chave estrangeira referenciando o cliente que realizou o pedido"
    )
    data_hora: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Data e hora em UTC de criação do pedido"
    )
    status: StatusPedido = Field(
        default=StatusPedido.CRIADO,
        description="Situação atual do pedido"
    )
    valor_total: float = Field(
        default=0.0,
        ge=0,
        description="Valor total acumulado dos itens do pedido"
    )

    # Relacionamentos bidirecionais
    cliente: Optional["Cliente"] = Relationship(back_populates="pedidos")
    itens: list[ItemPedido] = Relationship(back_populates="pedido", cascade_delete=True)


class PedidoCreate(PedidoBase):
    """Schema para criação de um novo pedido (POST /pedidos). Permite enviar itens inline."""
    itens: list[ItemPedidoCreateInline] = Field(
        default_factory=list,
        description="Lista opcional de itens iniciais a incluir no pedido"
    )


class PedidoUpdateStatus(SQLModel):
    """Schema para transição de status do pedido (PATCH /pedidos/{id}/status)."""
    status: StatusPedido = Field(
        description="Novo status do pedido: CRIADO, CONFIRMADO, EM_PREPARO, PRONTO, ENTREGUE, CANCELADO"
    )


class PedidoResponse(PedidoBase):
    """Schema de detalhe do pedido com seus itens (GET /pedidos/{id})."""
    id: int
    cliente_id: int
    data_hora: datetime
    status: StatusPedido
    valor_total: float
    itens: list[ItemPedidoResponse] = []


class PedidoListResponse(SQLModel):
    """Schema resumido para listagens gerais (GET /pedidos), otimizando tráfego de rede."""
    id: int
    cliente_id: int
    data_hora: datetime
    status: StatusPedido
    valor_total: float
    total_itens: int
