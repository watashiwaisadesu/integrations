"""asd

Revision ID: 98cd755e09db
Revises: a7fc8196ea52
Create Date: 2024-12-17 20:57:31.160699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98cd755e09db'
down_revision: Union[str, None] = 'a7fc8196ea52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('instagram_users', sa.Column('bot_url', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('instagram_users', 'bot_url')
    # ### end Alembic commands ###