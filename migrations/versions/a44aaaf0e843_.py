"""empty message

Revision ID: a44aaaf0e843
Revises: 
Create Date: 2022-07-30 08:57:36.249172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a44aaaf0e843'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('alias', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_alias_alias'), ['alias'])

    with op.batch_alter_table('player', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_player_name'), ['name'])

    with op.batch_alter_table('pokernow_id', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_pokernow_id_pn_id'), ['pn_id'])

    with op.batch_alter_table('url', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_url_url'), ['url'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_user_email'), ['email'])
        batch_op.create_foreign_key(batch_op.f('fk_user_player_id_player'), 'player', ['player_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_user_player_id_player'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('uq_user_email'), type_='unique')

    with op.batch_alter_table('url', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_url_url'), type_='unique')

    with op.batch_alter_table('pokernow_id', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_pokernow_id_pn_id'), type_='unique')

    with op.batch_alter_table('player', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_player_name'), type_='unique')

    with op.batch_alter_table('alias', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_alias_alias'), type_='unique')

    # ### end Alembic commands ###