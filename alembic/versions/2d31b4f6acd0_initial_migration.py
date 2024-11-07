"""Initial migration

Revision ID: 2d31b4f6acd0
Revises: 65ce44435602
Create Date: 2024-11-07 12:44:02.258141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d31b4f6acd0'
down_revision: Union[str, None] = '65ce44435602'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
