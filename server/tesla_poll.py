#!/usr/bin/env python3
"""
Tesla data poller — fetches all available vehicle data and POSTs to the health server.
Run every 5 minutes via cron on the NUC:

    crontab -e
    */5 * * * * /usr/bin/python3 /path/to/health-dashboard/server/tesla_poll.py >> /var/log/tesla_poll.log 2>&1

Requires:
    pip install teslapy requests
    ~/.tesla_cache.json  (created by tesla_auth.py)

Environment variables (optional, have defaults):
    TESLA_EMAIL         Tesla account email
    TESLA_CACHE_PATH    Path to token cache (default ~/.tesla_cache.json)
    HEALTH_API_URL      Health server URL (default http://192.168.1.26:8000)
    HEALTH_API_KEY      API key
"""

import json
import os
import sys
from datetime import datetime, timezone

try:
    import teslapy
    import requests
except ImportError as e:
    print(f"Missing dependency: {e}. Run: pip install teslapy requests")
    sys.exit(1)

EMAIL = os.environ.get("TESLA_EMAIL", "")
CACHE_PATH = os.environ.get("TESLA_CACHE_PATH", os.path.expanduser("~/.tesla_cache.json"))
API_URL = os.environ.get("HEALTH_API_URL", "http://192.168.1.26:8000")
API_KEY = os.environ.get("HEALTH_API_KEY", "ae43d94ce0f674df640831189d3462c0a5d51b87")

if not os.path.exists(CACHE_PATH):
    print(f"Token cache not found at {CACHE_PATH}. Run tesla_auth.py first.")
    sys.exit(1)

if not EMAIL:
    # Try to read email from cache file
    try:
        with open(CACHE_PATH) as f:
            cache = json.load(f)
        EMAIL = next(iter(cache.keys()), "")
    except Exception:
        pass

if not EMAIL:
    print("TESLA_EMAIL not set and could not read from cache. Set TESLA_EMAIL env var.")
    sys.exit(1)


def _get(data, *keys, default=None):
    """Safe nested dict getter."""
    for key in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(key, None)
        if data is None:
            return default
    return data


def build_snapshot(vehicle_data: dict, recorded_at: str) -> dict:
    cs = vehicle_data.get("charge_state", {})
    ds = vehicle_data.get("drive_state", {})
    cl = vehicle_data.get("climate_state", {})
    vs = vehicle_data.get("vehicle_state", {})
    vi = vehicle_data  # top-level vehicle info

    return {
        "recorded_at": recorded_at,
        "vehicle_id": str(vi.get("id_s") or vi.get("id", "")),
        "display_name": vi.get("display_name"),

        # Charge state
        "battery_level": cs.get("battery_level"),
        "usable_battery_level": cs.get("usable_battery_level"),
        "battery_range_miles": cs.get("battery_range"),
        "est_battery_range_miles": cs.get("est_battery_range"),
        "ideal_battery_range_miles": cs.get("ideal_battery_range"),
        "charging_state": cs.get("charging_state"),
        "charge_rate_mph": cs.get("charge_rate") or None,
        "charger_power_kw": cs.get("charger_power") or None,
        "charger_voltage": cs.get("charger_voltage") or None,
        "charger_actual_current": cs.get("charger_actual_current") or None,
        "charge_limit_soc": cs.get("charge_limit_soc"),
        "charge_energy_added_kwh": cs.get("charge_energy_added"),
        "charge_miles_added": cs.get("charge_miles_added_rated"),
        "time_to_full_charge_hours": cs.get("time_to_full_charge"),
        "minutes_to_full_charge": cs.get("minutes_to_full_charge"),
        "fast_charger_present": cs.get("fast_charger_present"),
        "fast_charger_type": cs.get("fast_charger_type") or None,

        # Drive state
        "latitude": ds.get("latitude"),
        "longitude": ds.get("longitude"),
        "heading": ds.get("heading"),
        "speed_mph": ds.get("speed"),
        "power_kw": ds.get("power"),
        "shift_state": ds.get("shift_state") or None,
        "odometer_miles": vs.get("odometer"),

        # Climate state
        "inside_temp_c": cl.get("inside_temp"),
        "outside_temp_c": cl.get("outside_temp"),
        "driver_temp_setting_c": cl.get("driver_temp_setting"),
        "passenger_temp_setting_c": cl.get("passenger_temp_setting"),
        "is_climate_on": cl.get("is_climate_on"),
        "is_preconditioning": cl.get("is_preconditioning"),
        "fan_status": cl.get("fan_status"),
        "battery_heater": cl.get("battery_heater"),

        # Vehicle state
        "locked": vs.get("locked"),
        "sentry_mode": vs.get("sentry_mode"),
        "valet_mode": vs.get("valet_mode"),
        "software_version": _get(vs, "software_update", "version") or vs.get("car_version", "").split(" ")[0] or None,
        "df": vs.get("df"),
        "dr": vs.get("dr"),
        "pf": vs.get("pf"),
        "pr": vs.get("pr"),
        "ft": vs.get("ft"),
        "rt": vs.get("rt"),
        "fd_window": vs.get("fd_window"),
        "rd_window": vs.get("rd_window"),
        "fp_window": vs.get("fp_window"),
        "rp_window": vs.get("rp_window"),

        # TPMS (bar)
        "tpms_fl": cs.get("tpms_pressure_fl"),
        "tpms_fr": cs.get("tpms_pressure_fr"),
        "tpms_rl": cs.get("tpms_pressure_rl"),
        "tpms_rr": cs.get("tpms_pressure_rr"),
    }


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    snapshots = []

    with teslapy.Tesla(EMAIL, cache_file=CACHE_PATH) as tesla:
        vehicles = tesla.vehicle_list()
        if not vehicles:
            print("No vehicles found.")
            return

        for vehicle in vehicles:
            name = vehicle.get("display_name", vehicle.get("vin", "unknown"))
            state = vehicle.get("state", "")

            if state == "asleep":
                print(f"  {name}: asleep — skipping (not waking to preserve battery)")
                continue

            if state == "offline":
                print(f"  {name}: offline — skipping")
                continue

            try:
                data = vehicle.get_vehicle_data()
                snapshot = build_snapshot(data, now)
                snapshots.append(snapshot)
                print(f"  {name}: fetched OK — battery={snapshot.get('battery_level')}% "
                      f"state={snapshot.get('charging_state')} "
                      f"range={snapshot.get('battery_range_miles'):.0f}mi")
            except Exception as e:
                print(f"  {name}: ERROR fetching data — {e}", file=sys.stderr)

    if not snapshots:
        print("Nothing to ingest.")
        return

    resp = requests.post(
        f"{API_URL}/ingest/tesla",
        json={"snapshots": snapshots},
        headers={"X-API-Key": API_KEY},
        timeout=15,
    )
    resp.raise_for_status()
    result = resp.json()
    print(f"Ingested: accepted={result['accepted']} duplicate_skipped={result['duplicate_skipped']}")


if __name__ == "__main__":
    main()
