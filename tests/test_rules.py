"""Tests for the Driver rules engine (handoff §7, §12)."""
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from curbcheck.rules import (
    GUARD_REASON,
    NO_TIME_LIMIT,
    SCOPE_REASON,
    TOO_LONG_REASON,
    TRI_STATE_REASON,
    MeterRule,
    Restriction,
    evaluate_meter,
)

# 2026-10-13 is a Tuesday.
TUE, WED, FRI, SAT = 13, 14, 16, 17


def at(day, hour, minute=0):
    return datetime(2026, 10, day, hour, minute)


def meter(**overrides):
    base = dict(
        object_id="1", meter_id="M1", supported=True, unsupported_reason="",
        rate_day=2.0, rate_evening=1.0,
        limit_day=120, limit_evening=240, limit_weekend_day=120, limit_weekend_evening=240,
        restrictions=(),
    )
    base.update(overrides)
    return MeterRule(**base)


def rush(start, end):
    return Restriction("rush", "AM rush-hour", start, end, frozenset(range(7)))


def prohibition(days, start, end, zone="TAXI ZONE"):
    return Restriction("prohibition", zone, start, end, frozenset(days))


def same_day(m, arrival, minutes):
    return evaluate_meter(m, arrival, minutes, same_day_only=True)


def timeline(m, arrival, minutes):
    return evaluate_meter(m, arrival, minutes, same_day_only=False)


# --- handoff §12: minimum tests ---------------------------------------------------

def test_stay_within_daytime():
    r = same_day(meter(), at(TUE, 10), 120)
    assert (r.supported, r.legal, r.estimated_cost) == (True, True, 4.0)


def test_stay_within_evening():
    r = same_day(meter(), at(TUE, 18), 120)
    assert (r.legal, r.estimated_cost) == (True, 2.0)


@pytest.mark.parametrize("arrival, minutes, expected", [
    (at(TUE, 17, 30), 90, True),    # reset: legal; continuous: legal
    (at(TUE, 17, 30), 180, None),   # reset: legal; continuous: not legal
    (at(TUE, 15), 300, False),      # both not legal
])
def test_stay_crossing_6pm(arrival, minutes, expected):
    r = same_day(meter(), arrival, minutes)
    assert r.legal is expected
    if expected is None:
        assert TRI_STATE_REASON in r.reasons


def test_rush_hour_overlap_at_9am():
    r = same_day(meter(restrictions=(rush(420, 570),)), at(TUE, 9), 60)
    assert r.legal is False


def test_weekday_and_weekend_limits_differ():
    m = meter(limit_day=120, limit_weekend_day=240)
    assert same_day(m, at(SAT, 10), 180).legal is True
    assert same_day(m, at(TUE, 10), 180).legal is False


def test_specific_weekday_prohibition():
    m = meter(restrictions=(prohibition([1], 540, 720, "LOADING ZONE"),))  # Tuesdays
    assert same_day(m, at(TUE, 10), 60).legal is False
    assert same_day(m, at(WED, 10), 60).legal is True


@pytest.mark.parametrize("reason", ["Missing time_limit_9am_6pm.", "Not in service."])
def test_unsupported_record(reason):
    r = same_day(meter(supported=False, unsupported_reason=reason), at(TUE, 10), 60)
    assert (r.supported, r.legal, r.estimated_cost) == (False, None, None)
    assert r.reasons == [reason]


def test_day2_window_restriction():
    r = same_day(meter(), at(TUE, 21), 120)
    assert (r.supported, r.reasons) == (False, [SCOPE_REASON])


# --- handoff §12: timeline tests --------------------------------------------------

def test_overnight_stay_is_free():
    r = timeline(meter(), at(TUE, 23), 420)
    assert (r.legal, r.estimated_cost) == (True, 0.0)
    assert r.warnings


def test_cross_midnight_taxi_zone():
    m = meter(restrictions=(prohibition(range(7), 1080, 120),))  # 6:00 pm to 2:00 am
    assert timeline(m, at(TUE, 19), 360).legal is False


def test_evening_limit_stops_counting_at_10pm():
    r = timeline(meter(), at(TUE, 19), 360)
    assert (r.legal, r.estimated_cost) == (True, 3.0)


def test_prohibition_uses_actual_calendar_day():
    m = meter(restrictions=(prohibition(range(5), 0, 540, "NO STOPPING"),))  # Mon-Fri
    assert timeline(m, at(SAT, 1), 420).legal is True
    assert timeline(m, at(FRI, 1), 420).legal is False


def test_overnight_stay_overlapping_am_rush():
    assert timeline(meter(restrictions=(rush(420, 570),)), at(TUE, 1), 420).legal is False


def test_three_hour_guard_after_overnight_stay():
    m = meter(limit_day=180, limit_weekend_day=180)
    noon = timeline(m, at(TUE, 20), 16 * 60)       # Tue 8:00 pm to Wed 12:00 pm
    eleven = timeline(m, at(TUE, 20), 15 * 60)     # Tue 8:00 pm to Wed 11:00 am
    assert noon.legal is None and GUARD_REASON in noon.reasons
    assert eleven.legal is True


def test_stay_longer_than_24_hours():
    r = timeline(meter(), at(TUE, 10), 24 * 60 + 1)
    assert (r.supported, r.reasons) == (False, [TOO_LONG_REASON])


@pytest.mark.parametrize("limit_day, minutes, expected", [
    (240, 240, None),             # 4 Hr, 9:00 am-1:00 pm: guard
    (240, 180, True),             # exactly 180 minutes: no guard
    (NO_TIME_LIMIT, 240, None),   # No Time Limit: guard
    (180, 240, False),            # 3 Hr: meter limit exceeded
])
def test_three_hour_guard_same_day(limit_day, minutes, expected):
    m = meter(limit_day=limit_day, limit_weekend_day=limit_day)
    assert same_day(m, at(TUE, 9), minutes).legal is expected


def test_three_hour_guard_alone_across_6pm():
    m = meter(limit_day=240, limit_evening=240)
    r = same_day(m, at(TUE, 14, 30), 240)
    assert r.legal is None
    assert r.reasons == [GUARD_REASON]


# --- Integration with data/meters_clean.csv ---------------------------------------

CLEAN = Path(__file__).resolve().parent.parent / "data" / "meters_clean.csv"


@pytest.mark.skipif(not CLEAN.exists(), reason="meters_clean.csv not generated")
def test_every_record_loads_and_evaluates():
    df = pd.read_csv(CLEAN)
    results = [evaluate_meter(MeterRule.from_row(row), at(TUE, 18), 120)
               for _, row in df.iterrows()]
    supported = sum(r.supported for r in results)
    assert supported == int(df["supported"].sum())
    assert any(r.legal is True for r in results)
