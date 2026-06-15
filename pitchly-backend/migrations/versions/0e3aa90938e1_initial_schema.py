"""initial_schema

Revision ID: 0e3aa90938e1
Revises: 5740e161bb67
Create Date: 2026-06-14 02:13:12.303442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e3aa90938e1'
down_revision: Union[str, None] = '5740e161bb67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
