"""Change id_instance to Integer

Revision ID: a34441089f2d
Revises: 5f7e7a522f01
Create Date: 2024-12-17 19:19:20.994966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a34441089f2d'
down_revision: Union[str, None] = '5f7e7a522f01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Alter column type from String to BIGINT using explicit cast
    op.execute("""
        ALTER TABLE whatsapp_users 
        ALTER COLUMN id_instance 
        TYPE BIGINT USING id_instance::BIGINT
    """)


def downgrade():
    # Revert back to String with explicit cast
    op.execute("""
        ALTER TABLE whatsapp_users 
        ALTER COLUMN id_instance 
        TYPE VARCHAR USING id_instance::TEXT
    """)