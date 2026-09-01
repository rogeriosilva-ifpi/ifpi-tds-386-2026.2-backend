"""criacao_inicial_itens_cardapio

Revision ID: 0001_inicial
Revises: 
Create Date: 2026-09-01 12:00:00.000000

CONCEITO DIDÁTICO: Migração Inicial (Baseline)
Cria a tabela base 'itens_cardapio' com chave primária e campos obrigatórios.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# Identificadores de revisão do Alembic
revision: str = '0001_inicial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica as alterações no banco de dados (Criação da Tabela)."""
    op.create_table(
        'itens_cardapio',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('descricao', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('preco', sa.Float(), nullable=False),
        sa.Column('categoria', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('disponivel', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_itens_cardapio_id'), 'itens_cardapio', ['id'], unique=False)


def downgrade() -> None:
    """Reverte as alterações (Exclusão da Tabela)."""
    op.drop_index(op.f('ix_itens_cardapio_id'), table_name='itens_cardapio')
    op.drop_table('itens_cardapio')
