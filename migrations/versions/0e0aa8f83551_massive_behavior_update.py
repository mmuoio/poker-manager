"""=Massive behavior update

Revision ID: 0e0aa8f83551
Revises: 701cc4187c28
Create Date: 2022-08-02 14:29:44.498007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e0aa8f83551'
down_revision = '701cc4187c28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('behavior', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hu_pre_hands_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_pre_hands_participated', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_pre_hands_raised', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_post_hands_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_post_hands_bet_raise', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_post_hands_call', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_post_hands_check', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_cbet_fold', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_cbet_call_raise', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_turns_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_rivers_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_2barrel', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_3barrel', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_no_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_4bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_no_4bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_fold_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_call_raise_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_fold_2b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_call_raise_2b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_fold_3b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_call_raise_3b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_fold_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_call_raise_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hu_wtsd', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_pre_hands_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_pre_hands_participated', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_pre_hands_raised', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_post_hands_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_post_hands_bet_raise', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_post_hands_call', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_post_hands_check', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_cbet_fold', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_cbet_call_raise', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_turns_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_rivers_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_2barrel', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_3barrel', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_no_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_4bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_no_4bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_fold_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_call_raise_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_fold_2b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_call_raise_2b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_fold_3b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_call_raise_3b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_fold_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_call_raise_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sr_wtsd', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_pre_hands_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_pre_hands_participated', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_pre_hands_raised', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_post_hands_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_post_hands_bet_raise', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_post_hands_call', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_post_hands_check', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_cbet_fold', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_cbet_call_raise', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_turns_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_rivers_played', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_2barrel', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_3barrel', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_no_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_4bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_no_4bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_fold_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_call_raise_cbet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_fold_2b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_call_raise_2b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_fold_3b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_call_raise_3b', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_fold_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_call_raise_3bet', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ft_wtsd', sa.Integer(), nullable=True))
        batch_op.drop_column('hands_raised')
        batch_op.drop_column('hands_played')
        batch_op.drop_column('hand_number')
        batch_op.drop_column('hands_participated')
        batch_op.drop_column('street')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('behavior', schema=None) as batch_op:
        batch_op.add_column(sa.Column('street', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('hands_participated', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('hand_number', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('hands_played', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('hands_raised', sa.INTEGER(), nullable=True))
        batch_op.drop_column('ft_wtsd')
        batch_op.drop_column('ft_call_raise_3bet')
        batch_op.drop_column('ft_fold_3bet')
        batch_op.drop_column('ft_call_raise_3b')
        batch_op.drop_column('ft_fold_3b')
        batch_op.drop_column('ft_call_raise_2b')
        batch_op.drop_column('ft_fold_2b')
        batch_op.drop_column('ft_call_raise_cbet')
        batch_op.drop_column('ft_fold_cbet')
        batch_op.drop_column('ft_no_4bet')
        batch_op.drop_column('ft_4bet')
        batch_op.drop_column('ft_no_3bet')
        batch_op.drop_column('ft_3bet')
        batch_op.drop_column('ft_3barrel')
        batch_op.drop_column('ft_2barrel')
        batch_op.drop_column('ft_rivers_played')
        batch_op.drop_column('ft_turns_played')
        batch_op.drop_column('ft_cbet_call_raise')
        batch_op.drop_column('ft_cbet_fold')
        batch_op.drop_column('ft_cbet')
        batch_op.drop_column('ft_post_hands_check')
        batch_op.drop_column('ft_post_hands_call')
        batch_op.drop_column('ft_post_hands_bet_raise')
        batch_op.drop_column('ft_post_hands_played')
        batch_op.drop_column('ft_pre_hands_raised')
        batch_op.drop_column('ft_pre_hands_participated')
        batch_op.drop_column('ft_pre_hands_played')
        batch_op.drop_column('sr_wtsd')
        batch_op.drop_column('sr_call_raise_3bet')
        batch_op.drop_column('sr_fold_3bet')
        batch_op.drop_column('sr_call_raise_3b')
        batch_op.drop_column('sr_fold_3b')
        batch_op.drop_column('sr_call_raise_2b')
        batch_op.drop_column('sr_fold_2b')
        batch_op.drop_column('sr_call_raise_cbet')
        batch_op.drop_column('sr_fold_cbet')
        batch_op.drop_column('sr_no_4bet')
        batch_op.drop_column('sr_4bet')
        batch_op.drop_column('sr_no_3bet')
        batch_op.drop_column('sr_3bet')
        batch_op.drop_column('sr_3barrel')
        batch_op.drop_column('sr_2barrel')
        batch_op.drop_column('sr_rivers_played')
        batch_op.drop_column('sr_turns_played')
        batch_op.drop_column('sr_cbet_call_raise')
        batch_op.drop_column('sr_cbet_fold')
        batch_op.drop_column('sr_cbet')
        batch_op.drop_column('sr_post_hands_check')
        batch_op.drop_column('sr_post_hands_call')
        batch_op.drop_column('sr_post_hands_bet_raise')
        batch_op.drop_column('sr_post_hands_played')
        batch_op.drop_column('sr_pre_hands_raised')
        batch_op.drop_column('sr_pre_hands_participated')
        batch_op.drop_column('sr_pre_hands_played')
        batch_op.drop_column('hu_wtsd')
        batch_op.drop_column('hu_call_raise_3bet')
        batch_op.drop_column('hu_fold_3bet')
        batch_op.drop_column('hu_call_raise_3b')
        batch_op.drop_column('hu_fold_3b')
        batch_op.drop_column('hu_call_raise_2b')
        batch_op.drop_column('hu_fold_2b')
        batch_op.drop_column('hu_call_raise_cbet')
        batch_op.drop_column('hu_fold_cbet')
        batch_op.drop_column('hu_no_4bet')
        batch_op.drop_column('hu_4bet')
        batch_op.drop_column('hu_no_3bet')
        batch_op.drop_column('hu_3bet')
        batch_op.drop_column('hu_3barrel')
        batch_op.drop_column('hu_2barrel')
        batch_op.drop_column('hu_rivers_played')
        batch_op.drop_column('hu_turns_played')
        batch_op.drop_column('hu_cbet_call_raise')
        batch_op.drop_column('hu_cbet_fold')
        batch_op.drop_column('hu_cbet')
        batch_op.drop_column('hu_post_hands_check')
        batch_op.drop_column('hu_post_hands_call')
        batch_op.drop_column('hu_post_hands_bet_raise')
        batch_op.drop_column('hu_post_hands_played')
        batch_op.drop_column('hu_pre_hands_raised')
        batch_op.drop_column('hu_pre_hands_participated')
        batch_op.drop_column('hu_pre_hands_played')

    # ### end Alembic commands ###