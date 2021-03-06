"""new post

Revision ID: 8018cde6dd74
Revises: 3cf6e36836dc
Create Date: 2019-12-09 17:06:46.607377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8018cde6dd74'
down_revision = '3cf6e36836dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('post_photo_url', sa.String(length=140), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'post_photo_url')
    # ### end Alembic commands ###
