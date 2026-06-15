"""initial_schema

Revision ID: aad5fce30468
Revises: 6030299633bf
Create Date: 2026-06-15 03:09:29.248332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aad5fce30468'
down_revision: Union[str, None] = '6030299633bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
