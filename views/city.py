"""City View — owners: Anahid, Juwon.

Meter-rate layer, ticket concentration, and infraction breakdown (Downtown).
Spec: mvp_implementation_handoff_en.md, Sections 9–10.
"""
import json
import math
import re
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="CurbCheck — City View", page_icon="🏙️", layout="wide")

DATA = Path(__file__).resolve().parent.parent / "data"
DOWNTOWN = (49.2820, -123.1180)
PERIOD = "January 2025 – June 2026"
RATE_FIELDS = {"Daytime (9 am – 6 pm)": "rate_day", "Evening (6 pm – 10 pm)": "rate_evening"}
RATE_BINS = [  # (upper bound exclusive, colour, label)
    (2.00, "#c6dbef", "under $2.00/hr"),
    (3.00, "#6baed6", "$2.00–$2.99/hr"),
    (4.50, "#2171b5", "$3.00–$4.49/hr"),
    (math.inf, "#08306b", "$4.50/hr and up"),
]
# Red and amber mean "conflict" and "uncertain" on the Driver View, so tickets use purple.
TICKET_COLOUR = "#8250df"
ESTIMATED_COLOUR = "#a475f9"
HIGHLIGHT_COLOUR = "#1f2328"
TOOLTIP_STYLE = "white-space: normal; width: max-content; max-width: 280px; font-size: 13px;"


@st.cache_data
def meters():
    df = pd.read_csv(DATA / "meters_clean.csv", low_memory=False,
                     usecols=["meter_id", "lat", "lon", "local_area", "rate_day", "rate_evening"],
                     dtype={"meter_id": str})
    return df.dropna(subset=["lat", "lon"])


@st.cache_data
def tickets():
    return pd.read_csv(DATA / "tickets_block_agg.csv")


@st.cache_data
def insights():
    """Insight blocks from the JSON, wording and review status from the reviewed Markdown."""
    blocks = json.loads((DATA / "city_insights.json").read_text(encoding="utf-8"))
    md = (DATA / "city_insights.md").read_text(encoding="utf-8")
    bodies = {int(n): body.strip() for n, body in re.findall(
        r"^## Insight (\d+) — .+?\n(.*?)(?=^## |\Z)", md, flags=re.M | re.S)}
    status = re.search(r"^Status: (.+)$", md, flags=re.M)
    for item in blocks:
        # ==phrase== in the Markdown marks a key phrase, shown with a light highlight.
        item["body"] = re.sub(r"==(.+?)==", r":yellow-background[\1]", bodies.get(item["id"], ""))
    return blocks, status.group(1).strip() if status else None


def rate_style(rate):
    for upper, colour, _ in RATE_BINS:
        if rate < upper:
            return colour
    return RATE_BINS[-1][1]


@st.cache_data
def rate_geojson(rate_field, rate_label):
    features = [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [round(m.lon, 6), round(m.lat, 6)]},
         "properties": {"colour": rate_style(getattr(m, rate_field)),
                        "tip": f"<b>Meter {m.meter_id}</b><br>{rate_label}: "
                               f"${getattr(m, rate_field):.2f}/hr"}}
        for m in meters().dropna(subset=[rate_field]).itertuples()
    ]
    return {"type": "FeatureCollection", "features": features}


def tooltip(html):
    return folium.Tooltip(html, style=TOOLTIP_STYLE)


def block_totals(df):
    return (df.groupby("block_key")
              .agg(lat=("lat", "first"), lon=("lon", "first"),
                   coord_estimated=("coord_estimated", "first"), count=("count", "sum"))
              .reset_index()
              .sort_values("count", ascending=False))


def dot(colour, label, ring=False):
    style = (f"border:2px dashed {colour};" if ring else f"color:{colour};")
    sym = "&nbsp;&nbsp;&nbsp;" if ring else "●"
    return (f"<span style='{style}border-radius:50%;display:inline-block;"
            f"line-height:1'>{sym}</span> {label}")


# --- Session state --------------------------------------------------------------

state = st.session_state
state.setdefault("city_block", None)
state.setdefault("city_insight", None)
state.setdefault("city_last_click", None)

tix = tickets()
all_blocks = block_totals(tix)
insight_list, insight_status = insights()
insight_by_id = {i["id"]: i for i in insight_list}

# --- Header -----------------------------------------------------------------------

st.title("City View")
st.caption("See meter rates and where tickets concentrate Downtown.")
st.info(f"Ticket analysis covers Downtown Vancouver, {PERIOD}. "
        "Ticket circles appear only for Downtown blocks; meter rates cover the whole city.")

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Map layers")
    rate_label = st.radio("Meter rate shown", list(RATE_FIELDS))
    categories = tix.groupby("category")["count"].sum().sort_values(ascending=False).index.tolist()
    picked = st.multiselect("Infraction categories on the map", categories,
                            placeholder="All categories", wrap=True)
rate_field = RATE_FIELDS[rate_label]

shown_blocks = block_totals(tix[tix.category.isin(picked)]) if picked else all_blocks
if picked and shown_blocks.empty:
    left.warning("No Downtown tickets match the selected categories.")
highlight = insight_by_id.get(state.city_insight)

# --- Map --------------------------------------------------------------------------

with right:
    # Canvas rendering keeps ~4,000 markers responsive in the browser.
    fmap = folium.Map(location=DOWNTOWN, zoom_start=14, tiles="OpenStreetMap",
                      control_scale=True, prefer_canvas=True)

    # One GeoJSON layer instead of one marker per meter keeps the page small.
    folium.GeoJson(
        rate_geojson(rate_field, rate_label),
        name=f"Meter rate — {rate_label}",
        marker=folium.CircleMarker(radius=3, fill=True, fill_opacity=0.9, weight=0),
        style_function=lambda f: {"color": f["properties"]["colour"],
                                  "fillColor": f["properties"]["colour"]},
        tooltip=folium.GeoJsonTooltip(["tip"], labels=False, style=TOOLTIP_STYLE),
    ).add_to(fmap)

    ticket_layer = folium.FeatureGroup(
        name="Tickets by 100-block" + (f" — {', '.join(picked)}" if picked else ""))
    peak = max(shown_blocks["count"].max(), 1) if len(shown_blocks) else 1
    for b in shown_blocks.itertuples():
        estimated = bool(b.coord_estimated)
        colour = ESTIMATED_COLOUR if estimated else TICKET_COLOUR
        note = "<br><i>Estimated location (no address data for this block)</i>" if estimated else ""
        folium.CircleMarker(
            (b.lat, b.lon), radius=3 + 22 * math.sqrt(b.count / peak),
            color=colour, fill=True, fill_opacity=0.35, weight=2,
            dash_array="4" if estimated else None,
            tooltip=tooltip(f"<b>{b.block_key}</b><br>{b.count:,} tickets"
                            f"{' in selected categories' if picked else ''}{note}"
                            "<br>Click for details"),
        ).add_to(ticket_layer)
    ticket_layer.add_to(fmap)

    focus = []
    if highlight:
        focus += [(b["block_key"], b["lat"], b["lon"]) for b in highlight["blocks"]]
    if state.city_block:
        row = all_blocks.loc[all_blocks.block_key == state.city_block].iloc[0]
        focus.append((row.block_key, row.lat, row.lon))
    if focus:
        focus_layer = folium.FeatureGroup(name="Highlighted blocks")
        for key, lat, lon in focus:
            folium.CircleMarker((lat, lon), radius=14, color=HIGHLIGHT_COLOUR, fill=False,
                                weight=4, tooltip=tooltip(f"<b>{key}</b>")).add_to(focus_layer)
        focus_layer.add_to(fmap)
        if highlight:
            lats = [f[1] for f in focus]
            lons = [f[2] for f in focus]
            fmap.fit_bounds([(min(lats), min(lons)), (max(lats), max(lons))], padding=(30, 30))

    folium.LayerControl(collapsed=True).add_to(fmap)

    out = st_folium(fmap, key="city_map", height=520, use_container_width=True,
                    returned_objects=["last_object_clicked", "last_object_clicked_tooltip"])
    # Identify the clicked circle by its tooltip, which starts with the block key. The
    # clicked position is not reliable on a canvas map, and some blocks share a coordinate.
    click = ((out or {}).get("last_object_clicked_tooltip"), (out or {}).get("last_object_clicked"))
    if click[0] and click != state.city_last_click:
        state.city_last_click = click
        hit = [k for k in shown_blocks.block_key if click[0].startswith(k)]
        if hit:
            state.city_block = max(hit, key=len)
            st.rerun()

    st.caption(" · ".join([dot(c, l.replace("$", r"\$")) for _, c, l in RATE_BINS]),
               unsafe_allow_html=True)
    st.caption(" · ".join([dot(TICKET_COLOUR, "Tickets (circle size = count)"),
                           dot(ESTIMATED_COLOUR, "Tickets, estimated block location", ring=True),
                           dot(HIGHLIGHT_COLOUR, "Highlighted block")]),
               unsafe_allow_html=True)
    st.caption("Meter rate is a demand proxy, not real-time occupancy. Ticket volume shows "
               "enforcement activity, not parking demand. Map data © OpenStreetMap contributors.")

# --- Selected block details -------------------------------------------------------

with left:
    st.subheader("Block details")
    keys = all_blocks.block_key.tolist()
    st.selectbox("Block", keys, key="city_block",
                 placeholder="Click a ticket circle or choose a block")
    if state.city_block:
        rows = tix[tix.block_key == state.city_block]
        by_cat = rows.groupby("category")["count"].sum().sort_values(ascending=False)
        total = int(by_cat.sum())
        st.metric("Tickets", f"{total:,}")
        st.markdown(f"Most common: **{by_cat.index[0]}** ({by_cat.iloc[0] / total:.0%})")
        if bool(rows.coord_estimated.iloc[0]):
            st.warning("Estimated location: this block has no address data, so its map "
                       "position is averaged from neighbouring blocks on the same street.")
        here = all_blocks.loc[all_blocks.block_key == state.city_block].iloc[0]
        shared = all_blocks[(all_blocks.lat == here.lat) & (all_blocks.lon == here.lon)
                            & (all_blocks.block_key != here.block_key)]
        if len(shared):
            st.caption("Shares its map position with: " + ", ".join(shared.block_key)
                       + ". Choose a block above to see the others.")
        breakdown = pd.DataFrame({"Category": by_cat.index, "Tickets": by_cat.values,
                                  "Share": (by_cat / total).values})
        st.dataframe(
            breakdown, hide_index=True, width="stretch",
            column_config={"Share": st.column_config.ProgressColumn(
                "Share", format="percent", min_value=0, max_value=1)},
        )
        st.caption(f"Downtown Vancouver, {PERIOD}. All categories are shown here, whatever "
                   "the map filter. Locations are approximate at the 100-block level.")
    else:
        st.write("Select a block to see its infraction breakdown.")

# --- Insights ---------------------------------------------------------------------


def toggle_insight(insight_id):
    state.city_insight = None if state.city_insight == insight_id else insight_id


st.subheader("Insights")
st.caption("Precomputed from the ticket aggregate before the demo (not generated live); they "
           "describe where tickets were issued, not why."
           + (f" Review status: {insight_status}" if insight_status else ""))
st.html("<style>[class*='st-key-cc_insight_'] > :last-child {margin-top: auto;}</style>")
cols = st.columns(len(insight_list))
for col, item in zip(cols, insight_list):
    with col, st.container(border=True, height="stretch", key=f"cc_insight_{item['id']}"):
        active = state.city_insight == item["id"]
        st.markdown(f"**{item['title']}**")
        st.write(item["body"])
        estimated = [b["block_key"] for b in item["blocks"] if b["coord_estimated"]]
        if estimated:
            st.caption("Estimated location: " + ", ".join(estimated))
        st.button("Clear highlight" if active else f"Show {len(item['blocks'])} blocks on map",
                  key=f"insight_{item['id']}", on_click=toggle_insight, args=(item["id"],),
                  type="primary" if active else "secondary")

# --- Data period and limitations --------------------------------------------------

st.divider()
st.markdown("**Data period and limitations**")
st.caption(
    f"Tickets: City of Vancouver open data (`parking-tickets-2020-2025`, `parking-tickets`), "
    f"Downtown, {PERIOD}, {int(tix['count'].sum()):,} issued tickets across "
    f"{len(all_blocks)} 100-blocks; water tickets removed. Meters: `parking-meters` snapshot "
    "2026-10-11, all records with a listed rate."
)
st.caption(
    "Ticket volume shows enforcement activity, not parking demand or the chance of a ticket. "
    "Meter rate is a demand proxy, not real-time occupancy. Ticket locations are approximate "
    "at the 100-block level, and tickets have a date but no time of day. VPD-issued tickets "
    "are not included. 98.4% of tickets were matched to a block (8,437 unmatched tickets are "
    "not mapped); 32,273 matched tickets citywide sit on blocks with estimated coordinates."
)
