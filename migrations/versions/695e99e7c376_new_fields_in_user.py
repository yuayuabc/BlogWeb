"""new fields in user

Revision ID: 695e99e7c376
Revises: 3e94d374ca1c
Create Date: 2019-12-07 23:00:34.756686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '695e99e7c376'
down_revision = '3e94d374ca1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'about_me')
    # ### end Alembic commands ###