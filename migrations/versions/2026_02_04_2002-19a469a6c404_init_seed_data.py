"""init_seed_data

Revision ID: 19a469a6c404
Revises: 609911d7b069
Create Date: 2026-02-04 20:02:54.482177

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "19a469a6c404"
down_revision: Union[str, Sequence[str], None] = "609911d7b069"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    from database.init_seed import init_seed_data

    bind = op.get_bind()
    init_seed_data(bind)


def downgrade():
    from database.init_seed import init_seed_data

    bind = op.get_bind()
    init_seed_data(bind)
