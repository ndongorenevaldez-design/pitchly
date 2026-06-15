"""initial_schema

Revision ID: 3f2796e6d99c
Revises: 0e3aa90938e1
Create Date: 2026-06-14 02:19:08.331776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f2796e6d99c'
down_revision: Union[str, None] = '0e3aa90938e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
