"""Build data/tickets_block_agg.csv (City View ticket aggregate).

Spec: mvp_implementation_handoff_en.md, Section 9.
Run from the repo root:  python scripts/build_tickets.py

Raw inputs (data/raw/, semicolon-delimited, UTF-8 BOM):
  parking-tickets-2020-2025.csv   (2025 rows are used)
  parking-tickets_2026.csv        (2026-01-01 .. 2026-06-30)
  property-addresses.csv          (block coordinates)

Steps 1-8 of the ticket-processing list in Section 9.2:
  1 keep issued tickets      2 de-dup on bi_id          3 combine + date filter
  4 remove water tickets     5 normalize street names   6 civic number -> 100-block
  7 block coordinates        8 join, Downtown, categorize, aggregate, write
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "tickets_block_agg.csv"

TICKET_FILES = ["parking-tickets-2020-2025.csv", "parking-tickets_2026.csv"]
ADDRESS_FILE = "property-addresses.csv"

DATE_START = "2025-01-01"
DATE_END = "2026-06-30"
ISSUED_STATUS = "IS"
DOWNTOWN_AREA = "Downtown"  # Geo Local Area value in the property-address data
WATER_BYLAW = "12086"  # Water Conservation By-law: the only water bylaw in the data

REPORT: list[str] = []


def log(msg: str) -> None:
    print(msg)
    REPORT.append(msg)


# ---------------------------------------------------------------- Step 5 helper
# Ticket street names use the abbreviations on the left; the property-address
# data spells them the way on the right. Both sides go through normalize_street.
SUFFIX_MAP = {
    "AVE": "AV",
    "AVENUE": "AV",
    "BLVD": "BOULEVARD",
    "RD": "ROAD",
    "DR": "DRIVE",
    "HWY": "HIGHWAY",
    "CRES": "CRESCENT",
    "PL": "PLACE",
    "STREET": "ST",
    "LN": "LANE",
    "PKWY": "PARKWAY",
}
DIRECTION_MAP = {"WEST": "W", "EAST": "E", "NORTH": "N", "SOUTH": "S"}


def normalize_street(name: str) -> str:
    """Uppercase, strip punctuation, and standardize suffixes/directions.

    Used for both the ticket streets and the property-address streets so the
    join keys agree. Leading directions (W 16TH AV) are kept as tokens.
    """
    if not isinstance(name, str):
        return ""
    s = re.sub(r"[.,'’]", "", name.upper())
    s = re.sub(r"\s+", " ", s).strip()
    tokens = s.split(" ")
    if len(tokens) > 1:
        # Leading direction word -> single letter (WEST 16TH AVE -> W 16TH AV)
        tokens[0] = DIRECTION_MAP.get(tokens[0], tokens[0])
        # Trailing suffix
        tokens[-1] = SUFFIX_MAP.get(tokens[-1], tokens[-1])
    return " ".join(tokens)


# ---------------------------------------------------------------- Step 8 helper
def categorize(bylaw: str, section: str, text: str) -> str:
    """Explicit bylaw/section mapping first, reviewed keyword rules second."""
    section = (section or "").upper()
    text = (text or "").upper()

    explicit = {
        ("2952", "5(4)(B)"): "Meter expired",
        ("2952", "5(4)(A)(II)"): "Meter expired",
        ("2849", "17.6(E)"): "Overstayed limit",
        ("2849", "17.6(F)"): "Overstayed limit",
        ("2849", "20.1(A)"): "Overstayed limit",
        ("2849", "17.2(K)"): "Rush-hour no stopping",
        ("2849", "21.5"): "Loading zone",
        ("2849", "21.3"): "Loading zone",
        ("2849", "17.2(C)"): "Fire hydrant",
        ("2849", "17.1(B)"): "Posted sign restriction",  # sign prohibits stopping
        ("2849", "17.6(B)"): "Posted sign restriction",  # sign restricts parking
        ("2849", "17.6(A)"): "Posted sign restriction",  # sign prohibits parking
    }
    hit = explicit.get((str(bylaw), section))
    if hit:
        return hit

    # Keyword fallbacks (reviewed against the 2025-26 infraction texts)
    if "HYDRANT" in text:
        return "Fire hydrant"
    if "LOADING ZONE" in text:
        return "Loading zone"
    if re.search(r"RUSH|PEAK|CONGESTION", text):
        return "Rush-hour no stopping"
    if "METERED SPACE" in text and ("EXPIRED" in text or "ZEROS" in text):
        return "Meter expired"
    if re.search(r"LONGER PERIOD|MORE THAN \d+ HRS|MORE THAN THREE HOURS", text):
        return "Overstayed limit"
    if re.search(r"RESIDENT(IAL)? (PARKING )?PERMIT|PERMIT ZONE", text):
        return "Residential permit zone"
    return "Other"



def estimate_missing_blocks(coords: pd.DataFrame, missing_keys: set) -> pd.DataFrame:
    """Estimate coordinates for ticket blocks with no property addresses.

    For a missing block, average the known blocks on the same street within
    +/-100 (nearest neighbours); if none, within +/-200. Anything further is
    left unmatched rather than guessed. Estimated rows are flagged.
    """
    coords = coords.copy()
    coords["_street"] = coords["block_key"].str.split(" ", n=1).str[1]
    coords["_block"] = coords["block_key"].str.split(" ", n=1).str[0].astype(int)
    by_street = {k: g for k, g in coords.groupby("_street")}
    rows = []
    for key in missing_keys:
        num, _, street = key.partition(" ")
        if not num.isdigit() or street not in by_street:
            continue
        g = by_street[street]
        dist = (g["_block"] - int(num)).abs()
        for radius in (100, 200):
            near = g[dist <= radius]
            if len(near):
                rows.append({
                    "block_key": key,
                    "lat": near["lat"].mean(),
                    "lon": near["lon"].mean(),
                    "local_area": near["local_area"].mode().iat[0],
                })
                break
    return pd.DataFrame(rows, columns=["block_key", "lat", "lon", "local_area"])


def load_tickets() -> pd.DataFrame:
    frames = []
    for name in TICKET_FILES:
        df = pd.read_csv(RAW / name, sep=";", encoding="utf-8-sig", dtype=str)
        df.columns = [c.lower() for c in df.columns]
        df["source_file"] = name
        frames.append(df)
        log(f"loaded {name}: {len(df):,} rows")
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    # ---- Step 3 (first half): combine + date window
    t = load_tickets()
    n0 = len(t)
    t = t[(t["entrydate"] >= DATE_START) & (t["entrydate"] <= DATE_END)].copy()
    log(f"[3] combined {n0:,} rows; within {DATE_START}..{DATE_END}: {len(t):,}")

    # ---- Step 1: issued tickets only
    n = len(t)
    t = t[t["status"] == ISSUED_STATUS].copy()
    log(f"[1] status == '{ISSUED_STATUS}': kept {len(t):,}, dropped {n - len(t):,}")

    # ---- Step 2: de-duplicate on bi_id
    n = len(t)
    t = t.drop_duplicates(subset="bi_id", keep="first").copy()
    log(f"[2] de-duplicated on bi_id: removed {n - len(t):,} duplicates; {len(t):,} remain")
    assert t["bi_id"].is_unique

    # ---- Step 4: remove water tickets (Water Conservation By-law 12086)
    water = (t["bylaw"] == WATER_BYLAW) | t["infractiontext"].str.contains(
        r"\bWATER(?:ING)?\b", case=False, regex=True, na=False
    )
    log(f"[4] water tickets removed: {int(water.sum()):,} "
        f"(bylaw {WATER_BYLAW}: {int((t['bylaw'] == WATER_BYLAW).sum()):,})")
    t = t[~water].copy()
    log(f"    tickets after water filter: {len(t):,}")

    # ---- Steps 5 + 6: normalize street, civic number -> 100-block
    t["street_normalized"] = t["street"].map(normalize_street)
    t["block"] = pd.to_numeric(t["block"], errors="coerce")
    bad_block = t["block"].isna()
    if bad_block.any():
        log(f"[6] tickets with non-numeric block (kept as unmatched): {int(bad_block.sum()):,}")
    t["block"] = (t["block"] // 100 * 100).astype("Int64")
    t["block_key"] = t["block"].astype(str) + " " + t["street_normalized"]

    # ---- Step 7: block coordinates from property addresses
    a = pd.read_csv(RAW / ADDRESS_FILE, sep=";", encoding="utf-8-sig", dtype=str)
    a = a.rename(columns={"Geo Local Area": "local_area"})
    a["local_area"] = a["local_area"].fillna("Unknown")
    a["civic"] = pd.to_numeric(a["CIVIC_NUMBER"], errors="coerce")
    ll = a["geo_point_2d"].str.split(",", expand=True)
    a["lat"] = pd.to_numeric(ll[0], errors="coerce")
    a["lon"] = pd.to_numeric(ll[1], errors="coerce")
    n = len(a)
    a = a.dropna(subset=["civic", "lat", "lon"]).copy()
    log(f"[7] property addresses: {n:,} rows, {len(a):,} usable (civic number + coordinates)")
    a["street_normalized"] = a["STD_STREET"].map(normalize_street)
    a["block"] = (a["civic"] // 100 * 100).astype(int)
    a["block_key"] = a["block"].astype(str) + " " + a["street_normalized"]

    coords = (
        a.groupby("block_key")
        .agg(
            lat=("lat", "mean"),
            lon=("lon", "mean"),
            # most frequent local area among the block's addresses
            local_area=("local_area", lambda s: s.mode().iat[0]),
        )
        .reset_index()
    )
    log(f"    block_coords: {len(coords):,} blocks")
    coords.to_csv(ROOT / "data" / "block_coords.csv", index=False)

    # ---- Step 8: join, report match rate, Downtown, categorize, aggregate
    coords["coord_estimated"] = False
    missing = set(t["block_key"]) - set(coords["block_key"])
    est = estimate_missing_blocks(coords, missing)
    est["coord_estimated"] = True
    est_tickets = int(t["block_key"].isin(est["block_key"]).sum())
    log(f"    estimated coordinates for {len(est):,} of {len(missing):,} blocks without "
        f"addresses (neighbouring blocks on the same street, within 200); "
        f"covers {est_tickets:,} tickets")
    coords = pd.concat([coords, est], ignore_index=True)
    coords.to_csv(ROOT / "data" / "block_coords.csv", index=False)
    t = t.merge(coords, on="block_key", how="left")
    matched = t["lat"].notna()
    log(f"[8] join: matched {int(matched.sum()):,} / {len(t):,} "
        f"({matched.mean():.1%}); unmatched {int((~matched).sum()):,}")
    unm = (
        t.loc[~matched, "block_key"].value_counts().head(15)
    )
    log("    top unmatched block_keys:\n" + unm.to_string())

    t = t[matched].copy()
    n = len(t)
    t = t[t["local_area"] == DOWNTOWN_AREA].copy()
    log(f"    Downtown (local_area == '{DOWNTOWN_AREA}'): {len(t):,} of {n:,} matched tickets")

    t["category"] = [
        categorize(b, s, x) for b, s, x in zip(t["bylaw"], t["section"], t["infractiontext"])
    ]
    t["weekday"] = pd.to_datetime(t["entrydate"]).dt.day_name()
    t["year"] = t["entrydate"].str[:4].astype(int)

    agg = (
        t.groupby(
            ["block_key", "block", "street_normalized", "lat", "lon",
             "local_area", "coord_estimated", "year", "weekday", "category"]
        )
        .size()
        .reset_index(name="count")
    )
    assert agg["count"].sum() == len(t), "aggregate does not reconcile with source rows"
    agg.to_csv(OUT, index=False)
    log(f"    wrote {OUT.relative_to(ROOT)}: {len(agg):,} rows, "
        f"{int(agg['count'].sum()):,} tickets (reconciles with source)")

    log("\ncategory totals:\n" + agg.groupby("category")["count"].sum()
        .sort_values(ascending=False).to_string())
    log("\ntop 10 blocks (manual plausibility check):\n" + agg.groupby("block_key")["count"]
        .sum().sort_values(ascending=False).head(10).to_string())

    (ROOT / "data" / "tickets_report.txt").write_text("\n".join(REPORT), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
