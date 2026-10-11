"""Driver rules engine (handoff §7). Pure functions; no Streamlit.

A stay is evaluated on a single timeline split at 9:00 am, 6:00 pm, 10:00 pm,
and midnight. Daytime (9:00 am-6:00 pm) and evening (6:00-10:00 pm) segments are
paid; 10:00 pm-9:00 am is free and does not consume the meter time limit.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

NO_TIME_LIMIT = -1
MAX_STAY_MINUTES = 24 * 60
THREE_HOUR_GUARD_MINUTES = 180

# Day 2 deployment restriction (handoff §3.2). The timeline tests in handoff §12
# pass, so the restriction is off; set to True to restore the same-day window.
SAME_DAY_WINDOW_ONLY = False

DAY_START = 9 * 60       # 9:00 am
EVENING_START = 18 * 60  # 6:00 pm
METER_END = 22 * 60      # 10:00 pm
GUARD_START = 8 * 60     # general three-hour rule window, 8:00 am-6:00 pm
GUARD_END = 18 * 60

SCOPE_REASON = "CurbCheck currently evaluates same-day stays between 9:00 am and 10:00 pm."
TOO_LONG_REASON = ("Stays longer than 24 hours or crossing more than one midnight "
                   "are not supported.")
TRI_STATE_REASON = ("This stay crosses 6:00 pm and depends on an unverified "
                    "time-limit reset rule.")
GUARD_REASON = ("This stay may exceed Vancouver's general three-hour daytime "
                "parking rule. Exceptions may apply.")
OVERNIGHT_WARNING = ("No meter fee is charged from 10:00 pm to 9:00 am, but posted "
                     "restrictions and other parking rules still apply.")


# --- Data -------------------------------------------------------------------

@dataclass(frozen=True)
class Restriction:
    """A rush-hour interval or a prohibition from the meter dataset."""
    kind: str                  # "rush" or "prohibition"
    label: str                 # "AM rush-hour", "PM rush-hour", or the prohibition zone
    start_min: int             # minutes after midnight
    end_min: int               # minutes after midnight; earlier than start if it crosses midnight
    weekdays: frozenset[int]   # Monday = 0; the day on which the interval starts
    days_text: str = ""
    time_text: str = ""

    @property
    def crosses_midnight(self) -> bool:
        return self.end_min < self.start_min


@dataclass(frozen=True)
class MeterRule:
    object_id: str
    meter_id: str
    supported: bool
    unsupported_reason: str
    rate_day: float | None
    rate_evening: float | None
    limit_day: int | None
    limit_evening: int | None
    limit_weekend_day: int | None
    limit_weekend_evening: int | None
    restrictions: tuple[Restriction, ...] = ()

    @classmethod
    def from_row(cls, row) -> "MeterRule":
        """Build from one row of data/meters_clean.csv (dict or pandas Series)."""
        restrictions: list[Restriction] = []
        for prefix, label in (("am_rush", "AM rush-hour"), ("pm_rush", "PM rush-hour")):
            s, e = _int(row.get(f"{prefix}_start")), _int(row.get(f"{prefix}_end"))
            if s is not None and e is not None:
                restrictions.append(Restriction(
                    "rush", label, s, e, frozenset(range(7)),
                    "every day", f"{format_clock(s)}–{format_clock(e)}"))
        for n in (1, 2):
            s = _int(row.get(f"prohibition_{n}_start_min"))
            e = _int(row.get(f"prohibition_{n}_end_min"))
            days = row.get(f"prohibition_{n}_weekdays")
            if s is not None and e is not None and not _missing(days):
                restrictions.append(Restriction(
                    "prohibition", _text(row.get(f"prohibition_{n}_zone")), s, e,
                    frozenset(int(float(x)) for x in str(days).split(",")),
                    _text(row.get(f"prohibition_{n}_days")),
                    _text(row.get(f"prohibition_{n}_time"))))
        return cls(
            object_id=_text(row.get("object_id")),
            meter_id=_text(row.get("meter_id")),
            supported=_bool(row.get("supported")),
            unsupported_reason=_text(row.get("unsupported_reason")),
            rate_day=_float(row.get("rate_day")),
            rate_evening=_float(row.get("rate_evening")),
            limit_day=_int(row.get("limit_day_min")),
            limit_evening=_int(row.get("limit_evening_min")),
            limit_weekend_day=_int(row.get("limit_weekend_day_min")),
            limit_weekend_evening=_int(row.get("limit_weekend_evening_min")),
            restrictions=tuple(restrictions),
        )


@dataclass
class EvaluationResult:
    supported: bool
    legal: bool | None
    estimated_cost: float | None
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# --- Evaluation ---------------------------------------------------------------

def stay_scope_reason(arrival_datetime: datetime, duration_minutes: int,
                      *, same_day_only: bool | None = None) -> str | None:
    """Return why a stay is outside the supported scope, or None (handoff §7.2 steps 1-2)."""
    if same_day_only is None:
        same_day_only = SAME_DAY_WINDOW_ONLY
    if (isinstance(duration_minutes, bool) or not isinstance(duration_minutes, (int, float))
            or duration_minutes <= 0):
        return "Duration must be a positive number of minutes."
    start = arrival_datetime
    end = start + timedelta(minutes=duration_minutes)
    last_day = (end - timedelta(microseconds=1)).date()
    if duration_minutes > MAX_STAY_MINUTES or (last_day - start.date()).days > 1:
        return TOO_LONG_REASON
    if same_day_only:
        d = start.date()
        if last_day != d or start < _at(d, DAY_START) or end > _at(d, METER_END):
            return SCOPE_REASON
    return None


def evaluate_meter(meter: MeterRule, arrival_datetime: datetime, duration_minutes: int,
                   *, same_day_only: bool | None = None) -> EvaluationResult:
    """Evaluate one meter for a stay (handoff §7.2)."""
    # Steps 1-2: validate and check the supported scope.
    scope = stay_scope_reason(arrival_datetime, duration_minutes, same_day_only=same_day_only)
    if scope:
        return _unsupported(scope)
    start = arrival_datetime
    end = start + timedelta(minutes=duration_minutes)
    last_day = (end - timedelta(microseconds=1)).date()

    # Step 4: records that preprocessing could not evaluate safely.
    if not meter.supported:
        return _unsupported(meter.unsupported_reason or "This meter record is not supported.")

    verdicts: list[bool | None] = []
    reasons: list[str] = []
    warnings: list[str] = []
    days = [start.date() + timedelta(days=i) for i in range((last_day - start.date()).days + 1)]

    # Steps 6-7: rush hours and prohibitions on each actual calendar day.
    # The previous day is included so that a cross-midnight prohibition that
    # started the evening before the stay is caught.
    for r in meter.restrictions:
        for d in [days[0] - timedelta(days=1), *days]:
            if d.weekday() not in r.weekdays:
                continue
            r_start = _at(d, r.start_min)
            r_end = _at(d + timedelta(days=1) if r.crosses_midnight else d, r.end_min)
            if _overlap(start, end, r_start, r_end) > 0:
                verdicts.append(False)
                reasons.append(_restriction_reason(r))
                break

    # Steps 5, 8, 9, 11: per-day paid periods, time limits, guard, and cost.
    cost = 0.0
    paid_minutes = 0.0
    for d in days:
        weekend = d.weekday() >= 5
        limit_day = meter.limit_weekend_day if weekend else meter.limit_day
        limit_evening = meter.limit_weekend_evening if weekend else meter.limit_evening
        day_min = _overlap(start, end, _at(d, DAY_START), _at(d, EVENING_START))
        eve_min = _overlap(start, end, _at(d, EVENING_START), _at(d, METER_END))
        paid_minutes += day_min + eve_min
        cost += day_min / 60 * meter.rate_day + eve_min / 60 * meter.rate_evening

        if day_min and eve_min:
            reset_ok = _within(day_min, limit_day) and _within(eve_min, limit_evening)
            continuous_ok = _within(day_min + eve_min, _strictest(limit_day, limit_evening))
            if not reset_ok:
                verdicts.append(False)
                reasons.append(_limit_reason(day_min, limit_day, eve_min, limit_evening))
            elif not continuous_ok:
                verdicts.append(None)
                reasons.append(TRI_STATE_REASON)
        elif day_min and not _within(day_min, limit_day):
            verdicts.append(False)
            reasons.append(f"Exceeds the {format_duration(limit_day)} daytime time limit.")
        elif eve_min and not _within(eve_min, limit_evening):
            verdicts.append(False)
            reasons.append(f"Exceeds the {format_duration(limit_evening)} evening time limit.")

        guard_min = _overlap(start, end, _at(d, GUARD_START), _at(d, GUARD_END))
        if guard_min > THREE_HOUR_GUARD_MINUTES and GUARD_REASON not in reasons:
            verdicts.append(None)
            reasons.append(GUARD_REASON)

    if paid_minutes < duration_minutes:
        warnings.append(OVERNIGHT_WARNING)

    # Step 10: combine conservatively.
    if False in verdicts:
        legal = False
    elif None in verdicts:
        legal = None
    else:
        legal = True
    return EvaluationResult(True, legal, round(cost, 2), reasons, warnings)


# --- Helpers ------------------------------------------------------------------

def format_clock(minute: int) -> str:
    """420 -> '7:00 am', 720 -> '12:00 pm', 1440 -> 'midnight'."""
    if minute in (0, 1440):
        return "midnight"
    h, m = divmod(minute, 60)
    suffix = "am" if h < 12 else "pm"
    return f"{h % 12 or 12}:{m:02d} {suffix}"


def format_duration(minutes: int | None) -> str:
    if minutes is None or minutes == NO_TIME_LIMIT:
        return "no"
    if minutes % 60 == 0:
        return f"{minutes // 60}-hour"
    return f"{minutes}-minute"


def _unsupported(reason: str) -> EvaluationResult:
    return EvaluationResult(False, None, None, [reason])


def _at(d: date, minute: int) -> datetime:
    return datetime.combine(d, time()) + timedelta(minutes=minute)


def _overlap(a0: datetime, a1: datetime, b0: datetime, b1: datetime) -> float:
    return max(0.0, (min(a1, b1) - max(a0, b0)).total_seconds() / 60)


def _within(minutes: float, limit: int | None) -> bool:
    return limit == NO_TIME_LIMIT or (limit is not None and minutes <= limit)


def _strictest(*limits: int | None) -> int | None:
    real = [x for x in limits if x != NO_TIME_LIMIT]
    return min(real) if real else NO_TIME_LIMIT


def _limit_reason(day_min, limit_day, eve_min, limit_evening) -> str:
    if not _within(day_min, limit_day):
        return f"Exceeds the {format_duration(limit_day)} daytime time limit."
    return f"Exceeds the {format_duration(limit_evening)} evening time limit."


def _restriction_reason(r: Restriction) -> str:
    if r.kind == "rush":
        return (f"Overlaps the listed {r.label} restriction ({r.time_text}). The data does "
                "not list applicable days, so CurbCheck applies it every day.")
    return (f"Overlaps a {r.label} restriction listed in the meter dataset "
            f"({r.days_text}, {r.time_text}).")


def _missing(value) -> bool:
    return (value is None
            or (isinstance(value, float) and math.isnan(value))
            or (isinstance(value, str) and value.strip() == ""))


def _text(value) -> str:
    return "" if _missing(value) else str(value).strip()


def _int(value) -> int | None:
    return None if _missing(value) else int(float(value))


def _float(value) -> float | None:
    return None if _missing(value) else float(value)


def _bool(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False if _missing(value) else bool(value)
