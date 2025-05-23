"""Them cot history

Revision ID: 5972a443b6c1
Revises: 3ae5851d0191
Create Date: 2025-04-24 00:01:40.533532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5972a443b6c1'
down_revision = '3ae5851d0191'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('activity_names', sa.Text(), nullable=False),
    sa.Column('days', sa.Integer(), nullable=False),
    sa.Column('total_cost', sa.String(length=50), nullable=False),
    sa.Column('destination', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('history')
    # ### end Alembic commands ###
