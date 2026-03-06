from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, String, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class TeslaSnapshot(Base):
    __tablename__ = "tesla_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, unique=True)
    inserted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vehicle_id: Mapped[Optional[str]] = mapped_column(String(64))
    display_name: Mapped[Optional[str]] = mapped_column(String(128))

    # Charge state
    battery_level: Mapped[Optional[int]] = mapped_column(Integer)
    usable_battery_level: Mapped[Optional[int]] = mapped_column(Integer)
    battery_range_miles: Mapped[Optional[float]] = mapped_column(Float)
    est_battery_range_miles: Mapped[Optional[float]] = mapped_column(Float)
    ideal_battery_range_miles: Mapped[Optional[float]] = mapped_column(Float)
    charging_state: Mapped[Optional[str]] = mapped_column(String(32))   # Charging/Complete/Disconnected/Stopped
    charge_rate_mph: Mapped[Optional[float]] = mapped_column(Float)
    charger_power_kw: Mapped[Optional[float]] = mapped_column(Float)
    charger_voltage: Mapped[Optional[int]] = mapped_column(Integer)
    charger_actual_current: Mapped[Optional[int]] = mapped_column(Integer)
    charge_limit_soc: Mapped[Optional[int]] = mapped_column(Integer)
    charge_energy_added_kwh: Mapped[Optional[float]] = mapped_column(Float)
    charge_miles_added: Mapped[Optional[float]] = mapped_column(Float)
    time_to_full_charge_hours: Mapped[Optional[float]] = mapped_column(Float)
    minutes_to_full_charge: Mapped[Optional[int]] = mapped_column(Integer)
    fast_charger_present: Mapped[Optional[bool]] = mapped_column(Boolean)
    fast_charger_type: Mapped[Optional[str]] = mapped_column(String(32))

    # Drive state
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    heading: Mapped[Optional[int]] = mapped_column(Integer)
    speed_mph: Mapped[Optional[float]] = mapped_column(Float)
    power_kw: Mapped[Optional[float]] = mapped_column(Float)
    shift_state: Mapped[Optional[str]] = mapped_column(String(8))       # P/D/R/N/null
    odometer_miles: Mapped[Optional[float]] = mapped_column(Float)

    # Climate state
    inside_temp_c: Mapped[Optional[float]] = mapped_column(Float)
    outside_temp_c: Mapped[Optional[float]] = mapped_column(Float)
    driver_temp_setting_c: Mapped[Optional[float]] = mapped_column(Float)
    passenger_temp_setting_c: Mapped[Optional[float]] = mapped_column(Float)
    is_climate_on: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_preconditioning: Mapped[Optional[bool]] = mapped_column(Boolean)
    fan_status: Mapped[Optional[int]] = mapped_column(Integer)
    battery_heater: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Vehicle state
    locked: Mapped[Optional[bool]] = mapped_column(Boolean)
    sentry_mode: Mapped[Optional[bool]] = mapped_column(Boolean)
    valet_mode: Mapped[Optional[bool]] = mapped_column(Boolean)
    software_version: Mapped[Optional[str]] = mapped_column(String(32))
    df: Mapped[Optional[int]] = mapped_column(Integer)   # driver front door
    dr: Mapped[Optional[int]] = mapped_column(Integer)   # driver rear door
    pf: Mapped[Optional[int]] = mapped_column(Integer)   # passenger front door
    pr: Mapped[Optional[int]] = mapped_column(Integer)   # passenger rear door
    ft: Mapped[Optional[int]] = mapped_column(Integer)   # front trunk
    rt: Mapped[Optional[int]] = mapped_column(Integer)   # rear trunk
    fd_window: Mapped[Optional[int]] = mapped_column(Integer)
    rd_window: Mapped[Optional[int]] = mapped_column(Integer)
    fp_window: Mapped[Optional[int]] = mapped_column(Integer)
    rp_window: Mapped[Optional[int]] = mapped_column(Integer)

    # TPMS tire pressure (bar)
    tpms_fl: Mapped[Optional[float]] = mapped_column(Float)
    tpms_fr: Mapped[Optional[float]] = mapped_column(Float)
    tpms_rl: Mapped[Optional[float]] = mapped_column(Float)
    tpms_rr: Mapped[Optional[float]] = mapped_column(Float)

    __table_args__ = (
        Index("ix_tesla_recorded", "recorded_at"),
    )
