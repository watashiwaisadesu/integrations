"""recreate logs

Revision ID: 424d053c2c43
Revises: 05e2a279d80d
Create Date: 2024-12-27 08:41:15.343106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '424d053c2c43'
down_revision: Union[str, None] = '05e2a279d80d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.TIMESTAMP(), nullable=True),
    sa.Column('log_level', sa.String(length=10), nullable=True),
    sa.Column('source', sa.String(length=255), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_logs_id'), 'logs', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_logs_id'), table_name='logs')
    op.drop_table('logs')
    # ### end Alembic commands ###