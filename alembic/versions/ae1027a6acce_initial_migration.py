"""initial migration

Revision ID: ae1027a6acce
Revises: 
Create Date: 2023-08-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae1027a6acce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=True),
        sa.Column('mobile', sa.String(length=15), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('mobile')
    )
    
    # Create otp_logins table
    op.create_table(
        'otp_logins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('otp_code', sa.String(length=6), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create pujas table
    op.create_table(
        'pujas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create puja_images table
    op.create_table(
        'puja_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('puja_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['puja_id'], ['pujas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create plans table
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('actual_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('discounted_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create puja_plans table
    op.create_table(
        'puja_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('puja_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id']),
        sa.ForeignKeyConstraint(['puja_id'], ['pujas.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('puja_id', 'plan_id')
    )
    
    # Create chadawas table
    op.create_table(
        'chadawas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('requires_note', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create puja_chadawas table
    op.create_table(
        'puja_chadawas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('puja_id', sa.Integer(), nullable=False),
        sa.Column('chadawa_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['chadawa_id'], ['chadawas.id']),
        sa.ForeignKeyConstraint(['puja_id'], ['pujas.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('puja_id', 'chadawa_id')
    )
    
    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('puja_id', sa.Integer(), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('booking_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('puja_link', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id']),
        sa.ForeignKeyConstraint(['puja_id'], ['pujas.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create booking_chadawas table
    op.create_table(
        'booking_chadawas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('chadawa_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chadawa_id'], ['chadawas.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('razorpay_order_id', sa.String(length=100), nullable=False),
        sa.Column('razorpay_payment_id', sa.String(length=100), nullable=True),
        sa.Column('razorpay_signature', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True, server_default='INR'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='created'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_otp_logins_id'), 'otp_logins', ['id'], unique=False)
    op.create_index(op.f('ix_pujas_id'), 'pujas', ['id'], unique=False)
    op.create_index(op.f('ix_puja_images_id'), 'puja_images', ['id'], unique=False)
    op.create_index(op.f('ix_plans_id'), 'plans', ['id'], unique=False)
    op.create_index(op.f('ix_puja_plans_id'), 'puja_plans', ['id'], unique=False)
    op.create_index(op.f('ix_chadawas_id'), 'chadawas', ['id'], unique=False)
    op.create_index(op.f('ix_puja_chadawas_id'), 'puja_chadawas', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_booking_chadawas_id'), 'booking_chadawas', ['id'], unique=False)
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)


def downgrade():
    # Drop all tables in reverse order
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_index(op.f('ix_booking_chadawas_id'), table_name='booking_chadawas')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_index(op.f('ix_puja_chadawas_id'), table_name='puja_chadawas')
    op.drop_index(op.f('ix_chadawas_id'), table_name='chadawas')
    op.drop_index(op.f('ix_puja_plans_id'), table_name='puja_plans')
    op.drop_index(op.f('ix_plans_id'), table_name='plans')
    op.drop_index(op.f('ix_puja_images_id'), table_name='puja_images')
    op.drop_index(op.f('ix_pujas_id'), table_name='pujas')
    op.drop_index(op.f('ix_otp_logins_id'), table_name='otp_logins')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    
    op.drop_table('payments')
    op.drop_table('booking_chadawas')
    op.drop_table('bookings')
    op.drop_table('puja_chadawas')
    op.drop_table('chadawas')
    op.drop_table('puja_plans')
    op.drop_table('plans')
    op.drop_table('puja_images')
    op.drop_table('pujas')
    op.drop_table('otp_logins')
    op.drop_table('users')
