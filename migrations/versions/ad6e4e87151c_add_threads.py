"""add threads

Revision ID: ad6e4e87151c
Revises: 11acf11a422b
Create Date: 2024-12-26 16:10:44.068544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad6e4e87151c'
down_revision: Union[str, None] = '11acf11a422b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('threads',
    sa.Column('thread_id', sa.String(), nullable=False),
    sa.Column('sender_id', sa.String(), nullable=False),
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('assistant_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('thread_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('threads')
    # ### end Alembic commands ###