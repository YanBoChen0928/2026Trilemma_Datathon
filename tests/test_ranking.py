"""Tests for nearby meter ranking (handoff §7.3)."""
from datetime import datetime

import pandas as pd

from curbcheck.ranking import distances_m, find_parking

DEST = (49.2827, -123.1207)
TUESDAY_6PM = datetime(2026, 10, 13, 18, 0)


def row(object_id, north_m, rate_evening=2.0, supported=True, limit_evening=240):
    """A clean-CSV row placed `north_m` metres north of DEST."""
    return {
        "object_id": object_id, "meter_id": f"M{object_id}",
        "lat": DEST[0] + north_m / 111_195, "lon": DEST[1],
        "supported": supported, "unsupported_reason": "" if supported else "Not in service.",
        "rate_day": 3.0, "rate_evening": rate_evening,
        "limit_day_min": 120, "limit_evening_min": limit_evening,
        "limit_weekend_day_min": 120, "limit_weekend_evening_min": limit_evening,
    }


def search(*rows, minutes=120, same_day_only=None):
    return find_parking(pd.DataFrame(rows), *DEST, TUESDAY_6PM, minutes,
                        same_day_only=same_day_only)


def test_distance_is_about_right():
    assert abs(distances_m(*DEST, [DEST[0] + 100 / 111_195], [DEST[1]])[0] - 100) < 1


def test_ranks_by_cost_then_distance_and_keeps_three():
    r = search(row("a", 50, rate_evening=3.0), row("b", 200, rate_evening=1.0),
               row("c", 100, rate_evening=2.0), row("d", 150, rate_evening=2.0),
               row("e", 120, rate_evening=4.0))
    assert [c.meter.object_id for c in r.recommendations] == ["b", "c", "d"]


def test_excludes_records_outside_radius_and_not_recommendable():
    r = search(row("far", 400), row("off", 30, supported=False),
               row("short", 60, limit_evening=60), row("ok", 90))
    assert [c.meter.object_id for c in r.candidates] == ["off", "short", "ok"]
    assert [c.meter.object_id for c in r.recommendations] == ["ok"]


def test_closest_record_is_reported_even_if_rejected():
    r = search(row("off", 30, supported=False), row("ok", 90))
    assert r.closest.meter.object_id == "off"
    assert r.closest.result.reasons == ["Not in service."]


def test_out_of_scope_stay():
    r = search(row("ok", 90), minutes=5 * 60, same_day_only=True)  # past the Day 2 window
    assert r.scope_reason is not None
    assert r.recommendations == []
