from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TeslaSnapshotIn(BaseModel):
    recorded_at: datetime
    vehicle_id: Optional[str] = None
    display_name: Optional[str] = None

    battery_level: Optional[int] = None
    usable_battery_level: Optional[int] = None
    battery_range_miles: Optional[float] = None
    est_battery_range_miles: Optional[float] = None
    ideal_battery_range_miles: Optional[float] = None
    charging_state: Optional[str] = None
    charge_rate_mph: Optional[float] = None
    charger_power_kw: Optional[float] = None
    charger_voltage: Optional[int] = None
    charger_actual_current: Optional[int] = None
    charge_limit_soc: Optional[int] = None
    charge_energy_added_kwh: Optional[float] = None
    charge_miles_added: Optional[float] = None
    time_to_full_charge_hours: Optional[float] = None
    minutes_to_full_charge: Optional[int] = None
    fast_charger_present: Optional[bool] = None
    fast_charger_type: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    heading: Optional[int] = None
    speed_mph: Optional[float] = None
    power_kw: Optional[float] = None
    shift_state: Optional[str] = None
    odometer_miles: Optional[float] = None

    inside_temp_c: Optional[float] = None
    outside_temp_c: Optional[float] = None
    driver_temp_setting_c: Optional[float] = None
    passenger_temp_setting_c: Optional[float] = None
    is_climate_on: Optional[bool] = None
    is_preconditioning: Optional[bool] = None
    fan_status: Optional[int] = None
    battery_heater: Optional[bool] = None

    locked: Optional[bool] = None
    sentry_mode: Optional[bool] = None
    valet_mode: Optional[bool] = None
    software_version: Optional[str] = None
    df: Optional[int] = None
    dr: Optional[int] = None
    pf: Optional[int] = None
    pr: Optional[int] = None
    ft: Optional[int] = None
    rt: Optional[int] = None
    fd_window: Optional[int] = None
    rd_window: Optional[int] = None
    fp_window: Optional[int] = None
    rp_window: Optional[int] = None

    tpms_fl: Optional[float] = None
    tpms_fr: Optional[float] = None
    tpms_rl: Optional[float] = None
    tpms_rr: Optional[float] = None


class TeslaIngestRequest(BaseModel):
    snapshots: list[TeslaSnapshotIn]


class TeslaIngestResponse(BaseModel):
    accepted: int
    duplicate_skipped: int


class TeslaSnapshotOut(TeslaSnapshotIn):
    id: int
    inserted_at: datetime

    model_config = {"from_attributes": True}
