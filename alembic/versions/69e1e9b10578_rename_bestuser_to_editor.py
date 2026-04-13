"""rename_bestuser_to_editor

Revision ID: 69e1e9b10578
Revises: 947aa597a63d
Create Date: 2026-04-13 17:21:58.212467

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '69e1e9b10578'
down_revision: Union[str, None] = '947aa597a63d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Update existing data if any (BestUser -> Editor)
    op.execute("UPDATE users SET role = 'EDITOR' WHERE role = 'BESTUSER'")

    # 2. Alter column to update Enum definition
    op.alter_column('users', 'role',
               existing_type=mysql.ENUM('USER', 'BESTUSER', 'ADMIN'),
               type_=sa.Enum('USER', 'EDITOR', 'ADMIN', name='userrole'),
               existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Update existing data if any (Editor -> BestUser)
    op.execute("UPDATE users SET role = 'BESTUSER' WHERE role = 'EDITOR'")

    # 2. Alter column to revert Enum definition
    op.alter_column('users', 'role',
               existing_type=sa.Enum('USER', 'EDITOR', 'ADMIN', name='userrole'),
               type_=mysql.ENUM('USER', 'BESTUSER', 'ADMIN'),
               existing_nullable=False)
