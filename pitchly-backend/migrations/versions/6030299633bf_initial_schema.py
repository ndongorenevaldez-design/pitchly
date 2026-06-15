"""initial_schema

Revision ID: 6030299633bf
Revises: 9c2d7b01f0d1
Create Date: 2026-06-15 02:30:47.065284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6030299633bf'
down_revision: Union[str, None] = '9c2d7b01f0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
