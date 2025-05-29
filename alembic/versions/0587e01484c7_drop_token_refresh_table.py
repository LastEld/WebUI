"""drop_token_refresh_table

Revision ID: 0587e01484c7
Revises: 27e8c88a5a58
Create Date: 2025-05-29 12:34:05.079940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0587e01484c7'
down_revision: Union[str, None] = '09d45f7b1801'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('token_refresh')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table('token_refresh',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
    sa.Column('refresh_token', sa.String(length=255), nullable=False, unique=True, index=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
