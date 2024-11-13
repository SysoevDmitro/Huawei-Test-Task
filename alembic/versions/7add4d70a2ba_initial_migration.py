"""Initial migration

Revision ID: 7add4d70a2ba
Revises: 009c48b9fa0c
Create Date: 2024-11-11 14:40:48.800400

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7add4d70a2ba'
down_revision: Union[str, None] = '009c48b9fa0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
