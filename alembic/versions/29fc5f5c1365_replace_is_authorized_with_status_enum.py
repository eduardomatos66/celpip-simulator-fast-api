"""replace_is_authorized_with_status_enum

Revision ID: 29fc5f5c1365
Revises: 16e977332b0b
Create Date: 2026-03-28 09:49:59.472233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '29fc5f5c1365'
down_revision: Union[str, None] = '16e977332b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add column as nullable
    enum_type = sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='userstatus')
    op.add_column('users', sa.Column('status', enum_type, nullable=True))
    
    # 2. Migrate data
    op.execute("UPDATE users SET status = 'APPROVED' WHERE is_authorized = 1")
    op.execute("UPDATE users SET status = 'PENDING' WHERE is_authorized = 0")
    
    # 3. Handle any remaining NULLs and set NOT NULL
    op.execute("UPDATE users SET status = 'PENDING' WHERE status IS NULL")
    op.alter_column('users', 'status', nullable=False, type_=enum_type, existing_type=enum_type)
    
    # 4. Drop old column
    op.drop_column('users', 'is_authorized')


def downgrade() -> None:
    # 1. Add column as nullable
    bool_type = mysql.TINYINT(display_width=1)
    op.add_column('users', sa.Column('is_authorized', bool_type, autoincrement=False, nullable=True))
    
    # 2. Migrate data back
    op.execute("UPDATE users SET is_authorized = 1 WHERE status = 'APPROVED'")
    op.execute("UPDATE users SET is_authorized = 0 WHERE status != 'APPROVED'")
    
    # 3. Set NOT NULL
    op.alter_column('users', 'is_authorized', nullable=False, type_=bool_type, existing_type=bool_type)
    
    # 4. Drop new column
    op.drop_column('users', 'status')
