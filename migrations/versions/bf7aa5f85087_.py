"""empty message

Revision ID: bf7aa5f85087
Revises: f2b0dafe08f3
Create Date: 2019-01-04 17:27:43.595638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf7aa5f85087'
down_revision = 'f2b0dafe08f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.add_column('datasets', sa.Column('author', sa.String(), nullable=True))
    op.drop_column('datasets', 'objects')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('datasets', sa.Column('objects', sa.INTEGER(), nullable=True))
    op.drop_column('datasets', 'author')
    op.drop_table('users')
    # ### end Alembic commands ###
