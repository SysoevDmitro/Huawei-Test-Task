"""Initial migration

Revision ID: dcd6343b5850
Revises: ab7baba549eb
Create Date: 2024-11-07 15:34:22.165800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcd6343b5850'
down_revision: Union[str, None] = 'ab7baba549eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
