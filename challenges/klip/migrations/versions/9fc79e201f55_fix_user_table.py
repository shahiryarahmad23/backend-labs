"""fix User table

Revision ID: 9fc79e201f55
Revises: 30f84b793702
Create Date: 2026-09-04 22:48:49.213610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fc79e201f55'
down_revision: Union[str, Sequence[str], None] = '30f84b793702'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        "ALTER TYPE userrole RENAME VALUE 'ADMIN' TO 'PRIVILEGED'"
    )
    op.execute(
        "ALTER TYPE userrole RENAME VALUE 'USER' TO 'OWNER'"
    )


def downgrade():
    op.execute(
        "ALTER TYPE userrole RENAME VALUE 'PRIVILEGED' TO 'ADMIN'"
    )
    op.execute(
        "ALTER TYPE userrole RENAME VALUE 'OWNER' TO 'USER'"
    )