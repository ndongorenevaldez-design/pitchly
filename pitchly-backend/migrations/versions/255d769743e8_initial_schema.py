"""initial_schema

Revision ID: 255d769743e8
Revises: 3f2796e6d99c
Create Date: 2026-06-14 02:23:18.585524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '255d769743e8'
down_revision: Union[str, None] = '3f2796e6d99c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
