"""Tests for meter preprocessing (handoff §6)."""
import pandas as pd
import pytest

from curbcheck.meters import (
    NO_TIME_LIMIT,
    RAW_COLUMNS,
    ParseError,
    parse_days,
    parse_interval,
    parse_limit,
    parse_rate,
    preprocess,
)


def make_row(**overrides):
    row = {c: "" for c in RAW_COLUMNS}
    row.update(
        object_id="1", meter_id="M1", service_status="In Service", local_area="Downtown",
        rate_9am_6pm="$5.00", rate_6pm_10pm="$3.00",
        time_limit_9am_6pm="2 Hr", time_limit_6pm_10pm="4 Hr",
        time_limit_weekend_9am_6pm="2 Hr", time_limit_weekend_6pm_10pm="4 Hr",
        time_limit_override="No", prohibition_override="No",
        vehicle_type="Any Vehicle", geo_point_2d="49.28, -123.12",
    )
    row.update(overrides)
    return row


def run(*rows):
    clean, report = preprocess(pd.DataFrame(list(rows), columns=RAW_COLUMNS))
    return clean, report


# --- Parsers -----------------------------------------------------------------

def test_parse_rate():
    assert parse_rate("$5.00") == 5.0
    assert parse_rate("") is None
    with pytest.raises(ParseError):
        parse_rate("five dollars")


def test_parse_limit():
    assert parse_limit("30 Min") == 30
    assert parse_limit("2 Hr") == 120
    assert parse_limit("13 Hr") == 780
    assert parse_limit("No Time Limit") == NO_TIME_LIMIT
    assert parse_limit("") is None
    with pytest.raises(ParseError):
        parse_limit("2 hours")


@pytest.mark.parametrize("text, expected", [
    ("7:00am to 10:00am", (420, 600)),
    ("7:00am to Noon", (420, 720)),
    ("5:00pm to Midnight", (1020, 1440)),
    ("Anytime", (0, 1440)),
    ("6:00pm to 2:00am", (1080, 120)),
    ("3:00pm to 9:30am", (900, 570)),
])
def test_parse_interval(text, expected):
    assert parse_interval(text) == expected


def test_parse_interval_rejects_unknown_text():
    with pytest.raises(ParseError):
        parse_interval("evenings")


def test_parse_days():
    assert parse_days("Mon-Fri") == [0, 1, 2, 3, 4]
    assert parse_days("Sat-Sun") == [5, 6]
    assert parse_days("Tuesdays") == [1]
    assert parse_days("7 Days a Week") == list(range(7))
    with pytest.raises(ParseError):
        parse_days("Weekdays")


# --- Records -----------------------------------------------------------------

def test_supported_record_is_parsed():
    clean, _ = run(make_row())
    r = clean.iloc[0]
    assert r["supported"]
    assert r["rate_day"] == 5.0
    assert r["limit_day_min"] == 120
    assert r["limit_evening_min"] == 240
    assert (r["lat"], r["lon"]) == (49.28, -123.12)
    assert r["rate_9am_6pm"] == "$5.00"  # raw column kept unchanged


def test_cross_midnight_prohibition_is_kept_in_full():
    clean, _ = run(make_row(prohibition_1_days="7 Days a Week",
                            prohibition_1_time="6:00pm to 2:00am",
                            prohibition_1_zone="TAXI ZONE"))
    r = clean.iloc[0]
    assert r["supported"]
    assert (r["prohibition_1_start_min"], r["prohibition_1_end_min"]) == (1080, 120)
    assert r["prohibition_1_crosses_midnight"]
    assert not r["prohibition_1_all_day"]
    assert r["prohibition_1_weekdays"] == "0,1,2,3,4,5,6"


def test_anytime_prohibition_is_all_day():
    clean, _ = run(make_row(prohibition_1_days="Mon-Fri", prohibition_1_time="Anytime",
                            prohibition_1_zone="NO STOPPING"))
    r = clean.iloc[0]
    assert r["prohibition_1_all_day"]
    assert not r["prohibition_1_crosses_midnight"]


def test_no_time_limit_is_minus_one():
    clean, _ = run(make_row(time_limit_9am_6pm="No Time Limit"))
    assert clean.iloc[0]["limit_day_min"] == NO_TIME_LIMIT
    assert clean.iloc[0]["supported"]


@pytest.mark.parametrize("overrides, reason", [
    ({"service_status": "Out of Service"}, "Not in service."),
    ({"vehicle_type": "Motorcycle"}, "Vehicle-specific record."),
    ({"flat_rate": "$10.00 flat rate option"}, "Flat-rate option not supported."),
    ({"time_limit_override": "Yes"}, "Time-limit override semantics not verified."),
    ({"prohibition_override": "Yes"}, "Prohibition override semantics not verified."),
    ({"time_limit_weekend_6pm_10pm": ""}, "Missing time_limit_weekend_6pm_10pm."),
    ({"rate_6pm_10pm": ""}, "Missing rate_6pm_10pm."),
    ({"prohibition_1_time": "7:00am to 11:00am", "prohibition_1_zone": "CVLZ"},
     "Partially filled prohibition group 1."),
    ({"geo_point_2d": ""}, "Missing coordinates."),
])
def test_unsupported_records(overrides, reason):
    clean, _ = run(make_row(**overrides))
    r = clean.iloc[0]
    assert not r["supported"]
    assert reason in r["unsupported_reason"]


def test_unparseable_value_is_unsupported_and_counted():
    clean, report = run(make_row(rate_9am_6pm="TBD"))
    assert not clean.iloc[0]["supported"]
    assert report["parse_failures_by_field"] == {"rate_9am_6pm": 1}


# --- Report and schema -------------------------------------------------------

def test_report_reconciles_counts():
    _, report = run(
        make_row(object_id="1", meter_id="A"),
        make_row(object_id="2", meter_id="A", service_status="Removed"),
        make_row(object_id="3", meter_id="B", local_area="Fairview"),
    )
    assert report["total_records"] == 3
    assert report["supported_records"] == 2
    assert report["supported_downtown"] == 1
    assert report["supported_records"] + report["unsupported_records"] == 3
    assert report["duplicate_meter_id_values"] == 1
    assert report["duplicate_meter_id_records"] == 2


def test_duplicate_object_id_is_rejected():
    with pytest.raises(ValueError):
        run(make_row(object_id="1"), make_row(object_id="1"))


def test_unexpected_schema_is_rejected():
    df = pd.DataFrame([make_row()], columns=RAW_COLUMNS).drop(columns=["geom"])
    with pytest.raises(ValueError):
        preprocess(df)
