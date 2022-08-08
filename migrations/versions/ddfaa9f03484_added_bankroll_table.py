"""Added bankroll table

Revision ID: ddfaa9f03484
Revises: 1b2f1e160adb
Create Date: 2022-08-07 09:03:56.288983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddfaa9f03484'
down_revision = '1b2f1e160adb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bankroll',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('url_id', sa.Integer(), nullable=True),
    sa.Column('behavior_id', sa.Integer(), nullable=True),
    sa.Column('imported', sa.Boolean(), nullable=True),
    sa.Column('date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('location', sa.String(length=200), nullable=True),
    sa.Column('buyin', sa.Integer(), nullable=True),
    sa.Column('cashout', sa.Integer(), nullable=True),
    sa.Column('net', sa.Integer(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('hands_played', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['behavior_id'], ['behavior.id'], name=op.f('fk_bankroll_behavior_id_behavior')),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], name=op.f('fk_bankroll_game_id_game')),
    sa.ForeignKeyConstraint(['url_id'], ['url.id'], name=op.f('fk_bankroll_url_id_url')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bankroll'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bankroll')
    # ### end Alembic commands ###
