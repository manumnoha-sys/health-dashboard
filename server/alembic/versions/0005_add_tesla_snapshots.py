"""add tesla_snapshots table

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-06
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tesla_snapshots",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, unique=True),
        sa.Column("inserted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),

        sa.Column("vehicle_id", sa.String(64), nullable=True),
        sa.Column("display_name", sa.String(128), nullable=True),

        # Charge state
        sa.Column("battery_level", sa.Integer(), nullable=True),
        sa.Column("usable_battery_level", sa.Integer(), nullable=True),
        sa.Column("battery_range_miles", sa.Float(), nullable=True),
        sa.Column("est_battery_range_miles", sa.Float(), nullable=True),
        sa.Column("ideal_battery_range_miles", sa.Float(), nullable=True),
        sa.Column("charging_state", sa.String(32), nullable=True),
        sa.Column("charge_rate_mph", sa.Float(), nullable=True),
        sa.Column("charger_power_kw", sa.Float(), nullable=True),
        sa.Column("charger_voltage", sa.Integer(), nullable=True),
        sa.Column("charger_actual_current", sa.Integer(), nullable=True),
        sa.Column("charge_limit_soc", sa.Integer(), nullable=True),
        sa.Column("charge_energy_added_kwh", sa.Float(), nullable=True),
        sa.Column("charge_miles_added", sa.Float(), nullable=True),
        sa.Column("time_to_full_charge_hours", sa.Float(), nullable=True),
        sa.Column("minutes_to_full_charge", sa.Integer(), nullable=True),
        sa.Column("fast_charger_present", sa.Boolean(), nullable=True),
        sa.Column("fast_charger_type", sa.String(32), nullable=True),

        # Drive state
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("heading", sa.Integer(), nullable=True),
        sa.Column("speed_mph", sa.Float(), nullable=True),
        sa.Column("power_kw", sa.Float(), nullable=True),
        sa.Column("shift_state", sa.String(8), nullable=True),
        sa.Column("odometer_miles", sa.Float(), nullable=True),

        # Climate state
        sa.Column("inside_temp_c", sa.Float(), nullable=True),
        sa.Column("outside_temp_c", sa.Float(), nullable=True),
        sa.Column("driver_temp_setting_c", sa.Float(), nullable=True),
        sa.Column("passenger_temp_setting_c", sa.Float(), nullable=True),
        sa.Column("is_climate_on", sa.Boolean(), nullable=True),
        sa.Column("is_preconditioning", sa.Boolean(), nullable=True),
        sa.Column("fan_status", sa.Integer(), nullable=True),
        sa.Column("battery_heater", sa.Boolean(), nullable=True),

        # Vehicle state
        sa.Column("locked", sa.Boolean(), nullable=True),
        sa.Column("sentry_mode", sa.Boolean(), nullable=True),
        sa.Column("valet_mode", sa.Boolean(), nullable=True),
        sa.Column("software_version", sa.String(32), nullable=True),
        sa.Column("df", sa.Integer(), nullable=True),
        sa.Column("dr", sa.Integer(), nullable=True),
        sa.Column("pf", sa.Integer(), nullable=True),
        sa.Column("pr", sa.Integer(), nullable=True),
        sa.Column("ft", sa.Integer(), nullable=True),
        sa.Column("rt", sa.Integer(), nullable=True),
        sa.Column("fd_window", sa.Integer(), nullable=True),
        sa.Column("rd_window", sa.Integer(), nullable=True),
        sa.Column("fp_window", sa.Integer(), nullable=True),
        sa.Column("rp_window", sa.Integer(), nullable=True),

        # TPMS
        sa.Column("tpms_fl", sa.Float(), nullable=True),
        sa.Column("tpms_fr", sa.Float(), nullable=True),
        sa.Column("tpms_rl", sa.Float(), nullable=True),
        sa.Column("tpms_rr", sa.Float(), nullable=True),
    )
    op.create_index("ix_tesla_recorded", "tesla_snapshots", ["recorded_at"])


def downgrade():
    op.drop_index("ix_tesla_recorded", table_name="tesla_snapshots")
    op.drop_table("tesla_snapshots")
