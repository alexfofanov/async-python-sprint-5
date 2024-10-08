"""tbl_file_constraint

Revision ID: 9f207ac97c22
Revises: a2e9880c6df9
Create Date: 2024-08-19 21:05:08.918727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f207ac97c22'
down_revision: Union[str, None] = 'a2e9880c6df9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_user_path_uc', 'file', type_='unique')
    op.create_unique_constraint('_user_path_name_uc', 'file', ['user_id', 'path', 'name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_user_path_name_uc', 'file', type_='unique')
    op.create_unique_constraint('_user_path_uc', 'file', ['user_id', 'path'])
    # ### end Alembic commands ###
