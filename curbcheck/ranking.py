"""Nearby meter search and ranking (handoff §7.3). Pure functions; no Streamlit."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from curbcheck.rules import EvaluationResult, MeterRule, evaluate_meter, stay_scope_reason

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "meters_clean.csv"

SEARCH_RADIUS_M = 250
MAX_RECOMMENDATIONS = 3
EARTH_RADIUS_M = 6_371_000


@dataclass
class Candidate:
    meter: MeterRule
    lat: float
    lon: float
    distance_m: float
    result: EvaluationResult

    @property
    def recommendable(self) -> bool:
        return self.result.supported and self.result.legal is True


@dataclass
class SearchResult:
    scope_reason: str | None          # the stay itself is outside the supported scope
    candidates: list[Candidate]       # every meter record within the radius, nearest first
    recommendations: list[Candidate]  # up to three, cheapest first, then nearest

    @property
    def closest(self) -> Candidate | None:
        return self.candidates[0] if self.candidates else None

    @property
    def closest_legal(self) -> Candidate | None:
        """The nearest meter that appears legal for the stay, whatever its cost."""
        return next((c for c in self.candidates if c.recommendable), None)


def load_meters(path: Path = CLEAN_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def distances_m(lat: float, lon: float, lats, lons) -> np.ndarray:
    """Straight-line (haversine) distance in metres."""
    p1, p2 = np.radians(lat), np.radians(np.asarray(lats, dtype=float))
    dlat = p2 - p1
    dlon = np.radians(np.asarray(lons, dtype=float) - lon)
    a = np.sin(dlat / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def find_parking(meters: pd.DataFrame, dest_lat: float, dest_lon: float,
                 arrival: datetime, duration_minutes: int, *,
                 radius_m: float = SEARCH_RADIUS_M,
                 same_day_only: bool | None = None) -> SearchResult:
    """Evaluate meters within the radius and rank the legal ones (handoff §7.3)."""
    scope = stay_scope_reason(arrival, duration_minutes, same_day_only=same_day_only)

    dist = distances_m(dest_lat, dest_lon, meters["lat"], meters["lon"])
    nearby = meters.assign(distance_m=dist)
    nearby = nearby[nearby["distance_m"] <= radius_m].sort_values("distance_m")

    candidates = [
        Candidate(
            meter=(rule := MeterRule.from_row(row)),
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            distance_m=float(row["distance_m"]),
            result=evaluate_meter(rule, arrival, duration_minutes, same_day_only=same_day_only),
        )
        for _, row in nearby.iterrows()
    ]
    legal = [c for c in candidates if c.recommendable]
    legal.sort(key=lambda c: (c.result.estimated_cost, c.distance_m))
    return SearchResult(scope, candidates, legal[:MAX_RECOMMENDATIONS])
