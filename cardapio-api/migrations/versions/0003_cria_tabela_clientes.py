"""cria_tabela_clientes

Revision ID: 0003_clientes
Revises: 0002_tempo_preparo
Create Date: 2026-09-22 20:00:00.000000

CONCEITO DIDÁTICO: Migração de Esquema - Criação da Tabela de Clientes
Adiciona a tabela 'clientes' com campos fundamentais e suporte para logística de entregas:
- nome (obrigatório)
- data_nascimento (opcional)
- endereco (obrigatório)
- cep (obrigatório)
- numero (obrigatório)
- telefone (obrigatório, WhatsApp)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# Identificadores de revisão do Alembic
revision: str = '0003_clientes'
down_revision: Union[str, None] = '0002_tempo_preparo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica as alterações no banco de dados (Criação da Tabela clientes)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table('clientes'):
        op.create_table(
            'clientes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=False),
            sa.Column('data_nascimento', sa.Date(), nullable=True),
            sa.Column('endereco', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
            sa.Column('cep', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
            sa.Column('numero', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
            sa.Column('telefone', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_clientes_id'), 'clientes', ['id'], unique=False)


def downgrade() -> None:
    """Reverte as alterações (Exclusão da Tabela clientes)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table('clientes'):
        op.drop_index(op.f('ix_clientes_id'), table_name='clientes')
        op.drop_table('clientes')
