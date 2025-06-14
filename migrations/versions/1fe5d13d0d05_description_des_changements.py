"""description des changements

Revision ID: 1fe5d13d0d05
Revises: 
Create Date: 2025-05-07 05:02:35.402365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fe5d13d0d05'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('audio_file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('language', sa.String(length=50), nullable=True))
        batch_op.alter_column('model_used',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('audio_file', schema=None) as batch_op:
        batch_op.alter_column('model_used',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.drop_column('language')

    # ### end Alembic commands ###
