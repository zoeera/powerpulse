"""initial schema with 14 tables and constraints

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-10 18:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=100), server_default='Telangana'),
        sa.Column('city', sa.String(length=100), server_default='Hyderabad'),
        sa.Column('utility', sa.String(length=50), server_default='TGSPDCL'),
        sa.Column('tariff_category', sa.String(length=50), server_default='LT-I(A)'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. consents
    op.create_table(
        'consents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('consent_type', sa.String(length=100), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_consents_user_id', 'consents', ['user_id'])

    # 3. bills
    op.create_table(
        'bills',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('tariff_category', sa.String(length=50), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False),
        sa.Column('billing_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('units_consumed_kwh', sa.Float(), nullable=False),
        sa.Column('energy_charges', sa.Float(), server_default='0.0'),
        sa.Column('fixed_charges', sa.Float(), server_default='0.0'),
        sa.Column('customer_charges', sa.Float(), server_default='0.0'),
        sa.Column('electricity_duty', sa.Float(), server_default='0.0'),
        sa.Column('subsidy_amount', sa.Float(), server_default='0.0'),
        sa.Column('subsidy_scheme', sa.String(length=50), nullable=True),
        sa.Column('net_payable', sa.Float(), server_default='0.0'),
        sa.Column('meter_number', sa.String(length=100), nullable=True),
        sa.Column('consumer_number', sa.String(length=100), nullable=True),
        sa.Column('manual_review_required', sa.Boolean(), server_default='false'),
        sa.Column('confidence_score', sa.Float(), server_default='1.0'),
        sa.Column('source_file_hash', sa.String(length=64), unique=True, nullable=True),
        sa.Column('source_file_path', sa.String(length=500), nullable=True),
        sa.Column('raw_ocr_text', sa.Text(), nullable=True),
        sa.Column('parsed_json', sa.JSON(), nullable=True),
        sa.Column('is_manual', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_bills_user_id', 'bills', ['user_id'])
    op.create_index('ix_bills_source_file_hash', 'bills', ['source_file_hash'], unique=True)

    # 4. meter_readings
    op.create_table(
        'meter_readings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('kwh', sa.Float(), nullable=False),
        sa.Column('source_file_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_meter_readings_user_id', 'meter_readings', ['user_id'])
    op.create_index('ix_user_meter_time', 'meter_readings', ['user_id', 'timestamp'])

    # 5. appliance_profiles
    op.create_table(
        'appliance_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('appliance_type', sa.String(length=100), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('wattage_watts', sa.Float(), nullable=False),
        sa.Column('star_rating', sa.Integer(), nullable=True),
        sa.Column('daily_hours', sa.Float(), nullable=False, server_default='4.0'),
        sa.Column('estimated_monthly_kwh', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_appliance_profiles_user_id', 'appliance_profiles', ['user_id'])

    # 6. spikes
    op.create_table(
        'spikes',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('bill_id', sa.String(length=36), sa.ForeignKey('bills.id', ondelete='SET NULL'), nullable=True),
        sa.Column('spike_type', sa.String(length=20), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('threshold_kwh', sa.Float(), nullable=False),
        sa.Column('actual_kwh', sa.Float(), nullable=False),
        sa.Column('deviation_pct', sa.Float(), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_spikes_user_id', 'spikes', ['user_id'])

    # 7. forecasts
    op.create_table(
        'forecasts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('forecast_type', sa.String(length=20), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('predicted_kwh', sa.Float(), nullable=False),
        sa.Column('estimated_cost_inr', sa.Float(), nullable=False),
        sa.Column('confidence_tier', sa.String(length=20), nullable=False),
        sa.Column('model_used', sa.String(length=100), nullable=False),
        sa.Column('feature_snapshot', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_forecasts_user_id', 'forecasts', ['user_id'])

    # 8. recommendations
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('investment_inr', sa.Float(), nullable=False),
        sa.Column('monthly_savings_inr', sa.Float(), nullable=False),
        sa.Column('payback_period_years', sa.Float(), nullable=False),
        sa.Column('co2_reduction_kg_yr', sa.Float(), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_recommendations_user_id', 'recommendations', ['user_id'])

    # 9. reports
    op.create_table(
        'reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('report_period', sa.String(length=50), nullable=False),
        sa.Column('pdf_file_path', sa.String(length=500), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
    )
    op.create_index('ix_reports_user_id', 'reports', ['user_id'])

    # 10. jobs
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('task_name', sa.String(length=100), nullable=False),
        sa.Column('celery_task_id', sa.String(length=100), unique=True, nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retries', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_jobs_user_id', 'jobs', ['user_id'])

    # 11. utilities
    op.create_table(
        'utilities',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(length=50), unique=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('customer_care_number', sa.String(length=50), nullable=True),
        sa.Column('active', sa.Boolean(), server_default='true'),
    )

    # 12. tariffs
    op.create_table(
        'tariffs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('utility_code', sa.String(length=50), nullable=False),
        sa.Column('tariff_category', sa.String(length=50), nullable=False),
        sa.Column('min_units', sa.Float(), nullable=False),
        sa.Column('max_units', sa.Float(), nullable=False),
        sa.Column('rate_per_kwh', sa.Float(), nullable=False),
        sa.Column('fixed_charge', sa.Float(), server_default='0.0'),
        sa.Column('customer_charge', sa.Float(), server_default='0.0'),
        sa.Column('effective_from', sa.Date(), nullable=False),
    )
    op.create_index('ix_tariffs_utility_code', 'tariffs', ['utility_code'])

    # 13. subsidies
    op.create_table(
        'subsidies',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('utility_code', sa.String(length=50), nullable=False),
        sa.Column('scheme_name', sa.String(length=100), nullable=False),
        sa.Column('max_units_free', sa.Float(), nullable=False),
        sa.Column('criteria', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), server_default='true'),
    )
    op.create_index('ix_subsidies_utility_code', 'subsidies', ['utility_code'])

    # 14. reference_consumption
    op.create_table(
        'reference_consumption',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('household_size', sa.Integer(), nullable=False),
        sa.Column('monthly_average_kwh', sa.Float(), nullable=False),
        sa.Column('seasonal_factor', sa.Float(), server_default='1.0'),
    )

def downgrade() -> None:
    op.drop_table('reference_consumption')
    op.drop_table('subsidies')
    op.drop_table('tariffs')
    op.drop_table('utilities')
    op.drop_table('jobs')
    op.drop_table('reports')
    op.drop_table('recommendations')
    op.drop_table('forecasts')
    op.drop_table('spikes')
    op.drop_table('appliance_profiles')
    op.drop_table('meter_readings')
    op.drop_table('bills')
    op.drop_table('consents')
    op.drop_table('users')

