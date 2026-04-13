"""add_user_role_enum

Revision ID: 947aa597a63d
Revises: 63748d876fd0
Create Date: 2026-04-13 17:07:54.791589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '947aa597a63d'
down_revision: Union[str, None] = '63748d876fd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add column as nullable first
    op.add_column('users', sa.Column('role', sa.Enum('USER', 'BESTUSER', 'ADMIN', name='userrole'), nullable=True))

    # 2. Update existing rows based on is_admin
    # Use 1 for True and 0 for False if MySQL/TiDB
    op.execute("UPDATE users SET role = 'ADMIN' WHERE is_admin = 1")
    op.execute("UPDATE users SET role = 'USER' WHERE is_admin = 0")

    # 3. Set role to USER for any stragglers (shouldn't be any)
    op.execute("UPDATE users SET role = 'USER' WHERE role IS NULL")

    # 4. Set nullable=False
    op.alter_column('users', 'role', nullable=False, type_=sa.Enum('USER', 'BESTUSER', 'ADMIN', name='userrole'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
