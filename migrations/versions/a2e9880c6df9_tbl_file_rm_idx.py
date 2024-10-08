"""tbl_file_rm_idx

Revision ID: a2e9880c6df9
Revises: 2f733c9fad03
Create Date: 2024-06-17 16:49:43.057859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2e9880c6df9'
down_revision: Union[str, None] = '2f733c9fad03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('file_path_key', 'file', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('file_path_key', 'file', ['path'])
    # ### end Alembic commands ###
