"""fixes with tg

Revision ID: 9bf8dd1da687
Revises: 7ee82f871c9a
Create Date: 2024-12-18 14:37:58.249482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bf8dd1da687'
down_revision: Union[str, None] = '7ee82f871c9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('telegram_users', sa.Column('user_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('telegram_users', 'user_id')
    # ### end Alembic commands ###