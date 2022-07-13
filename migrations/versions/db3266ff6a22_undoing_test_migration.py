"""undoing test migration

Revision ID: db3266ff6a22
Revises: ff045bc0181b
Create Date: 2022-07-13 14:49:47.295012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db3266ff6a22'
down_revision = 'ff045bc0181b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'email')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('email', sa.VARCHAR(length=300), nullable=True))
    # ### end Alembic commands ###