"""Add collector status fields to CollectorSource

Revision ID: ab14680fb1c3
Revises: c5a39f91385b
Create Date: 2026-05-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ab14680fb1c3'
down_revision: Union[str, None] = 'c5a39f91385b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('collectorsource', sa.Column('last_run_at', sa.DateTime(), nullable=True))
    op.add_column('collectorsource', sa.Column('last_success_at', sa.DateTime(), nullable=True))
    op.add_column('collectorsource', sa.Column('last_error', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('collectorsource', sa.Column('last_fetched_count', sa.Integer(), nullable=True))
    op.add_column('collectorsource', sa.Column('last_saved_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('collectorsource', 'last_saved_count')
    op.drop_column('collectorsource', 'last_fetched_count')
    op.drop_column('collectorsource', 'last_error')
    op.drop_column('collectorsource', 'last_success_at')
    op.drop_column('collectorsource', 'last_run_at')
