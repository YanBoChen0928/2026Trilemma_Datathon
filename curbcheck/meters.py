"""Meter preprocessing: raw parking-meters snapshot -> data/meters_clean.csv (handoff §6).

Run from the repo root:  python -m curbcheck.meters
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "parking-meters_2026-10-11.csv"
OUT_CSV = ROOT / "data" / "meters_clean.csv"
OUT_REPORT = ROOT / "data" / "meters_preprocessing_report.json"

SNAPSHOT_META = {
    "dataset_id": "parking-meters",
    "source_url": "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/"
                  "parking-meters/exports/csv?delimiter=%2C",
    "snapshot_file": RAW_PATH.name,
    "downloaded_at": "2026-10-11T19:11:12Z",
}

RAW_COLUMNS = [
    "object_id", "meter_id", "service_status", "meter_head", "credit_card",
    "mobile_payment_number", "local_area", "sector", "direction",
    "rate_9am_6pm", "rate_6pm_10pm", "flat_rate",
    "time_limit_9am_6pm", "time_limit_6pm_10pm",
    "time_limit_weekend_9am_6pm", "time_limit_weekend_6pm_10pm",
    "time_limit_override", "am_rush_hours", "pm_rush_hours",
    "prohibition_1_days", "prohibition_1_time", "prohibition_1_zone",
    "prohibition_2_days", "prohibition_2_time", "prohibition_2_zone",
    "prohibition_override", "vehicle_type", "feature_id", "post_feature_id",
    "meter_mechanism", "meter_manufacturer", "parking_zone_feature_id",
    "geom", "geo_point_2d",
]

NO_TIME_LIMIT = -1
LIMIT_FIELDS = {
    "limit_day_min": "time_limit_9am_6pm",
    "limit_evening_min": "time_limit_6pm_10pm",
    "limit_weekend_day_min": "time_limit_weekend_9am_6pm",
    "limit_weekend_evening_min": "time_limit_weekend_6pm_10pm",
}
RATE_FIELDS = {"rate_day": "rate_9am_6pm", "rate_evening": "rate_6pm_10pm"}
DAY_INDEX = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
PLURAL_DAYS = {"Mondays": 0, "Tuesdays": 1, "Wednesdays": 2, "Thursdays": 3,
               "Fridays": 4, "Saturdays": 5, "Sundays": 6}


class ParseError(ValueError):
    """A non-blank source value that cannot be parsed safely."""


def _blank(value) -> bool:
    return value is None or str(value).strip() == ""


def parse_rate(value) -> float | None:
    """'$5.00' -> 5.0; blank -> None (never zero)."""
    if _blank(value):
        return None
    m = re.fullmatch(r"\$(\d+(?:\.\d{1,2})?)", str(value).strip())
    if not m:
        raise ParseError(f"rate: {value!r}")
    return float(m.group(1))


def parse_limit(value) -> int | None:
    """'2 Hr' -> 120, '30 Min' -> 30, 'No Time Limit' -> -1, blank -> None."""
    if _blank(value):
        return None
    s = str(value).strip()
    if s == "No Time Limit":
        return NO_TIME_LIMIT
    m = re.fullmatch(r"(\d+) (Min|Hr)", s)
    if not m:
        raise ParseError(f"time limit: {value!r}")
    n = int(m.group(1))
    return n if m.group(2) == "Min" else n * 60


def parse_clock(text: str, *, is_end: bool) -> int:
    """'7:00am' -> 420, 'Noon' -> 720, 'Midnight' -> 1440 as an end, 0 as a start."""
    s = text.strip()
    if s.lower() == "noon":
        return 720
    if s.lower() == "midnight":
        return 1440 if is_end else 0
    m = re.fullmatch(r"(\d{1,2}):(\d{2})(am|pm)", s, flags=re.IGNORECASE)
    if not m:
        raise ParseError(f"clock: {text!r}")
    hour, minute, ampm = int(m.group(1)), int(m.group(2)), m.group(3).lower()
    if not (1 <= hour <= 12 and 0 <= minute < 60):
        raise ParseError(f"clock: {text!r}")
    hour = hour % 12 + (12 if ampm == "pm" else 0)
    return hour * 60 + minute


def parse_interval(value) -> tuple[int, int] | None:
    """'6:00pm to 2:00am' -> (1080, 120); 'Anytime' -> (0, 1440); blank -> None."""
    if _blank(value):
        return None
    s = str(value).strip()
    if s.lower() == "anytime":
        return (0, 1440)
    parts = re.split(r"\s+to\s+", s, flags=re.IGNORECASE)
    if len(parts) != 2:
        raise ParseError(f"interval: {value!r}")
    start = parse_clock(parts[0], is_end=False)
    end = parse_clock(parts[1], is_end=True)
    if start == end:
        raise ParseError(f"interval with equal endpoints: {value!r}")
    return start, end


def parse_days(value) -> list[int] | None:
    """'Mon-Fri' -> [0, 1, 2, 3, 4]; 'Tuesdays' -> [1]; '7 Days a Week' -> [0..6]."""
    if _blank(value):
        return None
    s = str(value).strip()
    if s == "7 Days a Week":
        return list(range(7))
    if s in PLURAL_DAYS:
        return [PLURAL_DAYS[s]]
    m = re.fullmatch(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)-(Mon|Tue|Wed|Thu|Fri|Sat|Sun)", s)
    if m:
        a, b = DAY_INDEX[m.group(1)], DAY_INDEX[m.group(2)]
        if a <= b:
            return list(range(a, b + 1))
    raise ParseError(f"days: {value!r}")


def parse_point(value) -> tuple[float, float] | None:
    """'49.28, -123.12' -> (49.28, -123.12)."""
    if _blank(value):
        return None
    try:
        lat_s, lon_s = str(value).split(",")
        lat, lon = float(lat_s), float(lon_s)
    except ValueError as exc:
        raise ParseError(f"coordinates: {value!r}") from exc
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ParseError(f"coordinates out of range: {value!r}")
    return lat, lon


def _process_row(row: dict, failures: Counter) -> dict:
    out: dict = {}
    reasons: list[str] = []

    def attempt(field: str, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ParseError:
            failures[field] += 1
            reasons.append(f"Unparseable {field}.")
            return None

    # Eligibility (handoff §6.2 rules 2, 3, 8, 10, 11)
    if row["service_status"].strip() != "In Service":
        reasons.append("Not in service.")
    if row["vehicle_type"].strip() != "Any Vehicle":
        reasons.append("Vehicle-specific record.")
    out["flat_rate_raw"] = row["flat_rate"]
    if not _blank(row["flat_rate"]):
        reasons.append("Flat-rate option not supported.")
    if row["time_limit_override"].strip() == "Yes":
        reasons.append("Time-limit override semantics not verified.")
    if row["prohibition_override"].strip() == "Yes":
        reasons.append("Prohibition override semantics not verified.")

    # Rates and limits (rules 4-6, 12, 13)
    for col, src in RATE_FIELDS.items():
        out[col] = attempt(src, parse_rate, row[src])
        if out[col] is None and _blank(row[src]):
            reasons.append(f"Missing {src}.")
    for col, src in LIMIT_FIELDS.items():
        out[col] = attempt(src, parse_limit, row[src])
        if out[col] is None and _blank(row[src]):
            reasons.append(f"Missing {src}.")

    # Rush hours (rule 14): a blank field means no rush interval is listed.
    for prefix, src in (("am_rush", "am_rush_hours"), ("pm_rush", "pm_rush_hours")):
        interval = attempt(src, parse_interval, row[src])
        if interval and interval[1] < interval[0]:
            failures[src] += 1
            reasons.append(f"Unparseable {src}.")
            interval = None
        out[f"{prefix}_start"], out[f"{prefix}_end"] = interval or (None, None)

    # Prohibition groups (rules 7, 14): full 24-hour intervals, never clipped.
    for n in (1, 2):
        fields = [f"prohibition_{n}_days", f"prohibition_{n}_time", f"prohibition_{n}_zone"]
        filled = sum(not _blank(row[f]) for f in fields)
        start = end = weekdays = None
        if 0 < filled < 3:
            reasons.append(f"Partially filled prohibition group {n}.")
        elif filled == 3:
            days = attempt(fields[0], parse_days, row[fields[0]])
            interval = attempt(fields[1], parse_interval, row[fields[1]])
            if days is not None:
                weekdays = ",".join(map(str, days))
            if interval is not None:
                start, end = interval
        out[f"prohibition_{n}_start_min"] = start
        out[f"prohibition_{n}_end_min"] = end
        out[f"prohibition_{n}_crosses_midnight"] = (
            start is not None and end is not None and end < start)
        out[f"prohibition_{n}_all_day"] = (start, end) == (0, 1440)
        out[f"prohibition_{n}_weekdays"] = weekdays

    # Coordinates (rule 15)
    point = attempt("geo_point_2d", parse_point, row["geo_point_2d"])
    if point is None and _blank(row["geo_point_2d"]):
        reasons.append("Missing coordinates.")
    out["lat"], out["lon"] = point or (None, None)

    out["supported"] = not reasons
    out["unsupported_reason"] = "; ".join(reasons)
    return out


MINUTE_COLUMNS = (
    list(LIMIT_FIELDS)
    + ["am_rush_start", "am_rush_end", "pm_rush_start", "pm_rush_end"]
    + [f"prohibition_{n}_{e}_min" for n in (1, 2) for e in ("start", "end")]
)


def preprocess(raw: pd.DataFrame, meta: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """Return (all raw columns plus parsed columns, preprocessing report)."""
    if list(raw.columns) != RAW_COLUMNS:
        raise ValueError("Raw schema differs from the expected 34 source columns.")
    if raw["object_id"].duplicated().any():
        raise ValueError("object_id is not unique.")

    failures: Counter = Counter()
    parsed = pd.DataFrame([_process_row(r, failures) for r in raw.to_dict("records")],
                          index=raw.index)
    for col in MINUTE_COLUMNS:
        parsed[col] = parsed[col].astype("Int64")
    clean = pd.concat([raw, parsed], axis=1)

    reasons = Counter(
        reason
        for text in clean.loc[~clean["supported"], "unsupported_reason"]
        for reason in text.split("; ")
    )
    dup = raw["meter_id"][raw["meter_id"].duplicated(keep=False)]
    report = {
        **(meta or {}),
        "total_records": len(clean),
        "supported_records": int(clean["supported"].sum()),
        "supported_downtown": int((clean["supported"]
                                   & (clean["local_area"] == "Downtown")).sum()),
        "unsupported_records": int((~clean["supported"]).sum()),
        "unsupported_by_reason": dict(reasons.most_common()),
        "parse_failures_by_field": dict(failures.most_common()),
        "duplicate_meter_id_values": int(dup.nunique()),
        "duplicate_meter_id_records": int(len(dup)),
    }
    return clean, report


def main() -> None:
    raw = pd.read_csv(RAW_PATH, dtype=str, keep_default_na=False)
    clean, report = preprocess(raw, SNAPSHOT_META)
    clean.to_csv(OUT_CSV, index=False)
    OUT_REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {OUT_CSV.relative_to(ROOT)} ({len(clean)} rows) and "
          f"{OUT_REPORT.relative_to(ROOT)}")
    print(f"Supported: {report['supported_records']} citywide, "
          f"{report['supported_downtown']} Downtown")


if __name__ == "__main__":
    main()
