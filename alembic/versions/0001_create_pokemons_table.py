"""create pokemons table

Revision ID: 0001
Revises: 
Create Date: 2025-09-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'pokemons',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('poke_id', sa.Integer, nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_poke_id", "pokemons", ["poke_id"])

def downgrade():
    op.drop_table('pokemons')
