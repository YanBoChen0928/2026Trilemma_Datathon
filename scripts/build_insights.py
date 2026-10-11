"""Attach map locations to the reviewed City insights.

Reads data/tickets_block_agg.csv and writes data/city_insights.json.
Texts live in data/city_insights.md; this script only computes the blocks
(with lat/lon and counts) each insight refers to. Run after build_tickets.py.
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "data" / "tickets_block_agg.csv")


def block_rows(keys, category=None):
    out = []
    for k in keys:
        b = d[d.block_key == k]
        row = {
            "block_key": k,
            "lat": round(float(b["lat"].iloc[0]), 6),
            "lon": round(float(b["lon"].iloc[0]), 6),
            "total_tickets": int(b["count"].sum()),
            "coord_estimated": bool(b["coord_estimated"].iloc[0]),
        }
        if category:
            c = int(b.loc[b.category == category, "count"].sum())
            row["category"] = category
            row["category_tickets"] = c
            row["category_share"] = round(c / row["total_tickets"], 2)
        out.append(row)
    return out


rush = (d[d.category == "Rush-hour no stopping"].groupby("block_key")["count"]
        .sum().sort_values(ascending=False).head(10).index.tolist())
top = d.groupby("block_key")["count"].sum().sort_values(ascending=False).head(10).index.tolist()

insights = [
    {"id": 1, "title": "Rush-hour tickets cluster on a few streets",
     "blocks": block_rows(rush, "Rush-hour no stopping")},
    {"id": 2, "title": "Some blocks are dominated by a single infraction type",
     "blocks": (block_rows(["400 HELMCKEN ST", "500 NICOLA ST", "1400 W HASTINGS ST"], "Meter expired")
                + block_rows(["100 KEEFER PLACE", "600 ABBOTT ST"], "Posted sign restriction")
                + block_rows(["400 BEACH CRESCENT"], "Overstayed limit"))},
    {"id": 3, "title": "Enforcement is concentrated in a small share of blocks",
     "blocks": block_rows(top)},
]
(ROOT / "data" / "city_insights.json").write_text(json.dumps(insights, indent=2), encoding="utf-8")
for i in insights:
    print(i["id"], i["title"], len(i["blocks"]), "blocks")
