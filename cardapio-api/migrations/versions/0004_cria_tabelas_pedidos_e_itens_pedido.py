"""cria_tabelas_pedidos_e_itens_pedido

Revision ID: 0004_pedidos
Revises: 0003_clientes
Create Date: 2026-09-29 17:30:00.000000

CONCEITO DIDÁTICO: Migração de Esquema - Relacionamentos 1:N e Sub-Recursos
Adiciona as tabelas 'pedidos' e 'itens_pedido':
- pedidos: associado a clientes via cliente_id (ON DELETE CASCADE)
- itens_pedido: associado a pedidos via pedido_id (ON DELETE CASCADE)
  e associado a itens_cardapio via item_cardapio_id
- Inclui snapshot histórico de preço em 'preco_unitario'
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# Identificadores de revisão do Alembic
revision: str = '0004_pedidos'
down_revision: Union[str, None] = '0003_clientes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica as alterações no banco de dados (Criação de pedidos e itens_pedido)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Criação da tabela pedidos
    if not inspector.has_table('pedidos'):
        op.create_table(
            'pedidos',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('cliente_id', sa.Integer(), nullable=False),
            sa.Column('data_hora', sa.DateTime(), nullable=False),
            sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
            sa.Column('observacoes', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
            sa.Column('valor_total', sa.Float(), nullable=False, server_default='0.0'),
            sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_pedidos_id'), 'pedidos', ['id'], unique=False)
        op.create_index(op.f('ix_pedidos_cliente_id'), 'pedidos', ['cliente_id'], unique=False)

    # 2. Criação da tabela itens_pedido (composição de pedido e referência a item_cardapio)
    if not inspector.has_table('itens_pedido'):
        op.create_table(
            'itens_pedido',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('pedido_id', sa.Integer(), nullable=False),
            sa.Column('item_cardapio_id', sa.Integer(), nullable=False),
            sa.Column('quantidade', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('preco_unitario', sa.Float(), nullable=False),
            sa.Column('observacao', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=True),
            sa.ForeignKeyConstraint(['pedido_id'], ['pedidos.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['item_cardapio_id'], ['itens_cardapio.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_itens_pedido_id'), 'itens_pedido', ['id'], unique=False)
        op.create_index(op.f('ix_itens_pedido_pedido_id'), 'itens_pedido', ['pedido_id'], unique=False)
        op.create_index(op.f('ix_itens_pedido_item_cardapio_id'), 'itens_pedido', ['item_cardapio_id'], unique=False)


def downgrade() -> None:
    """Reverte as alterações respeitando a ordem de integridade referencial."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table('itens_pedido'):
        op.drop_index(op.f('ix_itens_pedido_item_cardapio_id'), table_name='itens_pedido')
        op.drop_index(op.f('ix_itens_pedido_pedido_id'), table_name='itens_pedido')
        op.drop_index(op.f('ix_itens_pedido_id'), table_name='itens_pedido')
        op.drop_table('itens_pedido')

    if inspector.has_table('pedidos'):
        op.drop_index(op.f('ix_pedidos_cliente_id'), table_name='pedidos')
        op.drop_index(op.f('ix_pedidos_id'), table_name='pedidos')
        op.drop_table('pedidos')
