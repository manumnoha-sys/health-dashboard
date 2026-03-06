#!/usr/bin/env python3
"""
One-time Tesla authentication — run this interactively on a machine with a browser.
It will open a Tesla login page, and after you log in, saves tokens to
~/.tesla_cache.json (or TESLA_CACHE_PATH env var).

Usage:
    pip install teslapy
    python3 tesla_auth.py

The saved cache file should be copied to the NUC where tesla_poll.py runs:
    scp ~/.tesla_cache.json manumohan@100.83.146.119:~/.tesla_cache.json
"""

import os
import sys

try:
    import teslapy
except ImportError:
    print("teslapy not installed. Run: pip install teslapy")
    sys.exit(1)

EMAIL = os.environ.get("TESLA_EMAIL") or input("Tesla account email: ").strip()
CACHE_PATH = os.environ.get("TESLA_CACHE_PATH", os.path.expanduser("~/.tesla_cache.json"))

with teslapy.Tesla(EMAIL, cache_file=CACHE_PATH) as tesla:
    if not tesla.authorized:
        print("Opening browser for Tesla login...")
        tesla.fetch_token()
    vehicles = tesla.vehicle_list()
    print(f"\nAuthenticated! Found {len(vehicles)} vehicle(s):")
    for v in vehicles:
        print(f"  [{v['id']}] {v['display_name']} — {v['vin']}")
    print(f"\nToken cache saved to: {CACHE_PATH}")
    print("Copy this file to the NUC, then run tesla_poll.py")
