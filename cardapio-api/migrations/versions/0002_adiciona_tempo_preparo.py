"""adiciona_tempo_preparo

Revision ID: 0002_tempo_preparo
Revises: 0001_inicial
Create Date: 2026-09-01 12:30:00.000000

CONCEITO DIDÁTICO: Evolução de Esquema (Schema Migration)
Demonstra como adicionar novos atributos a tabelas existentes sem perder dados:
- upgrade(): executa ALTER TABLE ADD COLUMN tempo_preparo_minutos
- downgrade(): executa ALTER TABLE DROP COLUMN tempo_preparo_minutos
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identificadores de revisão do Alembic
revision: str = '0002_tempo_preparo'
down_revision: Union[str, None] = '0001_inicial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona a nova coluna tempo_preparo_minutos."""
    with op.batch_alter_table('itens_cardapio', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('tempo_preparo_minutos', sa.Integer(), nullable=True)
        )


def downgrade() -> None:
    """Remove a coluna tempo_preparo_minutos (Rollback)."""
    with op.batch_alter_table('itens_cardapio', schema=None) as batch_op:
        batch_op.drop_column('tempo_preparo_minutos')
