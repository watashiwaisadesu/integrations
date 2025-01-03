"""recreate whatsapp

Revision ID: 5ae6b83c1543
Revises: dada45389e84
Create Date: 2024-12-27 09:09:29.154770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ae6b83c1543'
down_revision: Union[str, None] = 'dada45389e84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('whatsapp_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('api_url', sa.String(), nullable=False),
    sa.Column('id_instance', sa.BigInteger(), nullable=False),
    sa.Column('api_token', sa.String(), nullable=False),
    sa.Column('callback_url', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('authorized', sa.Boolean(), nullable=False),
    sa.Column('order_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_instance'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_index(op.f('ix_whatsapp_users_id'), 'whatsapp_users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_whatsapp_users_id'), table_name='whatsapp_users')
    op.drop_table('whatsapp_users')
    # ### end Alembic commands ###
