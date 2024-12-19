"""add bot_url to instagramuser

Revision ID: a7fc8196ea52
Revises: 0d3173ae142a
Create Date: 2024-12-17 20:44:54.024195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7fc8196ea52'
down_revision: Union[str, None] = '0d3173ae142a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'instagram_users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('access_token', sa.Text, nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table('instagram_users')
