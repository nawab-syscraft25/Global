"""drop_old_schema_safely

Revision ID: f3f874212652
Revises: 6540aea1e593
Create Date: 2025-08-23 15:12:07.759081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3f874212652'
down_revision = 'ae1027a6acce'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Drop foreign key constraints first to avoid dependency issues
    op.drop_constraint('bookings_pooja_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('chadawas_pooja_id_fkey', 'chadawas', type_='foreignkey')
    
    # Step 2: Drop dependent tables
    op.drop_index('ix_booking_chadawa_id', table_name='booking_chadawa')
    op.drop_table('booking_chadawa')
    
    # Step 3: Now we can safely drop poojas table
    op.drop_index('ix_poojas_id', table_name='poojas')
    op.drop_table('poojas')


def downgrade() -> None:
    # Recreate poojas table
    op.create_table('poojas',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), nullable=False),
        sa.Column('description', sa.VARCHAR(length=500), nullable=True),
        sa.Column('price', sa.DOUBLE_PRECISION(precision=53), nullable=False),
        sa.Column('duration', sa.INTEGER(), nullable=False),
        sa.Column('location', sa.VARCHAR(length=255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_poojas_id', 'poojas', ['id'], unique=False)
    
    # Recreate booking_chadawa table
    op.create_table('booking_chadawa',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.INTEGER(), nullable=False),
        sa.Column('chadawa_id', sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id']),
        sa.ForeignKeyConstraint(['chadawa_id'], ['chadawas.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_booking_chadawa_id', 'booking_chadawa', ['id'], unique=False)
    
    # Recreate foreign key constraints
    op.create_foreign_key('bookings_pooja_id_fkey', 'bookings', 'poojas', ['pooja_id'], ['id'])
    op.create_foreign_key('chadawas_pooja_id_fkey', 'chadawas', 'poojas', ['pooja_id'], ['id'])
