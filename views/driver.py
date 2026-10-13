"""Driver View — owner: Yan-Bo.

Find street parking that is legal for the whole stay and estimate its cost.
Spec: docs/mvp_implementation_handoff_en.md, Sections 6–8.
"""
import json
import math
import re
from collections import Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from curbcheck.ranking import SEARCH_RADIUS_M, distances_m, find_parking, load_meters
from curbcheck.rules import NO_TIME_LIMIT, SAME_DAY_WINDOW_ONLY

st.set_page_config(page_title="CurbCheck — Driver View", page_icon="🚗", layout="wide")

DATA = Path(__file__).resolve().parent.parent / "data"
DOWNTOWN = (49.2820, -123.1180)
DEMO = {  # 400 W Hastings St, Tuesday 6:00 pm, 2 hours (README, "Demo scenario")
    "dest": (49.28370197906036, -123.11137913860121),
    "date": date(2026, 10, 13),
    "time": time(18, 0),
    "duration": "2 hr",
    "block": "400 W HASTINGS ST",
}
DURATIONS = {"30 min": 30, "1 hr": 60, "2 hr": 120, "3 hr": 180, "Custom": None}
SCOPE_TEXT = ("Same-day stays between 9:00 am and 10:00 pm." if SAME_DAY_WINDOW_ONLY
              else "Stays of up to 24 hours that cross at most one midnight.")
STATUS_STYLE = {  # status -> (marker colour, label)
    "recommended": ("#1a7f37", "Recommended"),
    "legal": ("#4c9a5a", "Appears legal (not in top 3)"),
    "conflict": ("#cf222e", "Conflicts with a listed restriction or limit"),
    "uncertain": ("#bf8700", "Uncertain rule — not recommended"),
    "unsupported": ("#8c959f", "Data not supported"),
}
WARN = "#bc4c00"
CLOSEST_LEGAL_LABEL = "★ Closest legal option"
TOOLTIP_STYLE = ("white-space: normal; width: max-content; max-width: 280px; "
                 "font-size: 13px;")
RUSH_RE = re.compile(r"Overlaps the listed (.+?) restriction \((.+?)\)\. (.*)")
PROHIBITION_RE = re.compile(r"Overlaps a (.+?) restriction listed in the meter dataset \((.+)\)\.$")


@st.cache_data
def meters():
    return load_meters()


@st.cache_resource
def blocks():
    """100-block centres from data/block_coords.csv, keyed by block, ordered by street then number.

    Read-only, so cache_resource: cache_data would copy the whole table on every call.
    """
    df = pd.read_csv(DATA / "block_coords.csv")
    df["street"] = df["block_key"].str.split(n=1).str[1]
    df["number"] = df["block_key"].str.split(n=1).str[0].astype(int)
    df = df.sort_values(["street", "number"])
    return {key: (float(lat), float(lon), area, bool(est), f"{key.title()} · {area}")
            for key, lat, lon, area, est in zip(df["block_key"], df["lat"], df["lon"],
                                                 df["local_area"], df["coord_estimated"])}


# --- Session state ----------------------------------------------------------------

state = st.session_state
state.setdefault("dest", None)
state.setdefault("last_click", None)
state.setdefault("arrival_date", date.today())
state.setdefault("arrival_time", time(18, 0))
state.setdefault("duration_choice", "2 hr")
state.setdefault("custom_hours", 2.0)
state.setdefault("adv_lat", DOWNTOWN[0])
state.setdefault("adv_lon", DOWNTOWN[1])
state.setdefault("show_all", False)
state.setdefault("dest_block", None)


def load_demo():
    state.dest = DEMO["dest"]
    state.arrival_date = DEMO["date"]
    state.arrival_time = DEMO["time"]
    state.duration_choice = DEMO["duration"]
    state.adv_lat, state.adv_lon = DEMO["dest"]
    state.dest_block = DEMO["block"]


def use_block():
    """Set the destination from the block search. Clearing the search keeps the destination."""
    if state.dest_block:
        lat, lon = blocks()[state.dest_block][:2]
        state.dest = (lat, lon)
        state.adv_lat, state.adv_lon = lat, lon


def use_coordinates():
    state.dest = (state.adv_lat, state.adv_lon)
    state.dest_block = None  # the pin is no longer a block centre


def handle_map_click():
    """Set the destination from a map click before the page reruns."""
    click = (state.get("driver_map") or {}).get("last_clicked")
    if click and click != state.last_click:
        state.last_click = click
        state.dest = (click["lat"], click["lng"])
        state.dest_block = None  # a map click replaces the searched block


# --- Helpers ----------------------------------------------------------------------

def money(value):
    """Dollar amount for st.markdown, escaped so Streamlit does not read it as math."""
    return f"\\${value:.2f}"


def limit_text(minutes):
    if minutes is None:
        return "—"
    return "No limit" if minutes == NO_TIME_LIMIT else f"{minutes} min"


def split_reason(reason):
    """Split an engine reason into a short main line and an optional note."""
    if m := RUSH_RE.match(reason):
        return f"{m[1]} restriction: {m[2]}", m[3]
    if m := PROHIBITION_RE.match(reason):
        return f"{m[1].title()} restriction: {m[2]}", "Listed in the meter dataset."
    first, _, rest = reason.partition(". ")
    return (first if not rest else first + "."), rest


def directions_url(lat, lon):
    """Google Maps driving directions by URL; no API key or service call."""
    return ("https://www.google.com/maps/dir/?api=1"
            f"&destination={lat:.6f},{lon:.6f}&travelmode=driving")


def clock(dt):
    return dt.strftime("%I:%M %p").lstrip("0").replace("AM", "am").replace("PM", "pm")


def nearest_supported_meter(lat, lon):
    """The closest meter CurbCheck can evaluate, anywhere in the city."""
    df = meters()
    df = df[df["supported"]]
    d = distances_m(lat, lon, df["lat"], df["lon"])
    i = int(d.argmin())
    return df.iloc[i], float(d[i])


def tooltip(title, label, reason=""):
    html = f"<b>{title}</b><br>{label}" + (f"<br><i>{reason}</i>" if reason else "")
    return folium.Tooltip(html, style=TOOLTIP_STYLE)


def popup(candidate, title, extra=""):
    """Click popup with the card summary and a directions link."""
    return folium.Popup(_popup_html(candidate, title, extra), max_width=280)


def _popup_html(candidate, title, extra=""):
    c, m = candidate, candidate.meter
    cost = c.result.estimated_cost
    html = (f"<div style='font-size:13px;line-height:1.5'><b>{title}</b><br>"
            + (f"${cost:.2f} · " if cost is not None else "")
            + f"About {c.distance_m:.0f} m away<br>"
            + (f"<span style='color:#57606a'>Daytime ${m.rate_day:.2f}/h · "
               f"Evening ${m.rate_evening:.2f}/h</span><br>" if m.rate_day is not None else "")
            + (f"<i>{extra}</i><br>" if extra else "")
            + f"<a href='{directions_url(c.lat, c.lon)}' target='_blank' rel='noopener'>"
              "Directions ↗</a></div>")
    return html


def badge_marker(lat, lon, text, fg, bg, border, tip, z, pop=None):
    width = 26 + 9 * max(0, len(str(text)) - 1)
    return folium.Marker(
        (lat, lon), tooltip=tip, z_index_offset=z, popup=pop,
        icon=folium.DivIcon(
            icon_size=(width, 26), icon_anchor=(width // 2, 13),
            html=(f"<div style='width:{width}px;height:26px;border-radius:13px;background:{bg};"
                  f"color:{fg};font-weight:700;font-size:14px;line-height:22px;"
                  f"text-align:center;border:2px solid {border};"
                  f"box-shadow:0 0 3px #0006'>{text}</div>")))


def status_of(candidate, recommended_ids):
    r = candidate.result
    if not r.supported:
        return "unsupported"
    if candidate.meter.object_id in recommended_ids:
        return "recommended"
    if r.legal is True:
        return "legal"
    return "conflict" if r.legal is False else "uncertain"


# --- Header and inputs ------------------------------------------------------------

BLOCKS = blocks()

st.title("Driver View")
st.caption("Find metered street parking that appears legal for your whole stay.")
with st.expander("Demo tools"):
    st.button("Load demo example", on_click=load_demo)

left, right = st.columns([2, 3], gap="large")

with left:
    st.subheader("Your stay")
    st.caption(f"Search a block, tap the map, or use Advanced: enter coordinates, to check "
               f"metered parking within {SEARCH_RADIUS_M} m of your destination. Then set your "
               "arrival time and duration.")
    st.selectbox("Search a Vancouver block", list(BLOCKS), key="dest_block", index=None,
                 format_func=lambda key: BLOCKS[key][4], on_change=use_block,
                 placeholder="Type a street, e.g. 400 W Hastings")
    if state.dest_block and BLOCKS[state.dest_block][3]:
        st.caption("This block's location is estimated from neighbouring blocks on the same "
                   "street.")
    if state.dest:
        st.markdown(":green[**✓ Destination selected**]")
    else:
        st.markdown(":gray[No destination yet]")
    st.date_input("Date", key="arrival_date")
    st.time_input("Arrival time", key="arrival_time", step=timedelta(minutes=15))
    st.segmented_control("Duration", list(DURATIONS), key="duration_choice")
    if state.duration_choice in (None, "Custom"):
        st.number_input("Custom duration (hours)", key="custom_hours",
                        min_value=0.25, max_value=24.0, step=0.25)
    preset = DURATIONS.get(state.duration_choice or "Custom")
    duration = preset if preset else int(round(state.custom_hours * 60))
    arrival = datetime.combine(state.arrival_date, state.arrival_time)
    departure = arrival + timedelta(minutes=duration)
    end_day = "" if departure.date() == arrival.date() else departure.strftime("%a ")
    st.markdown(f"**{arrival:%a, %b} {arrival.day} · {clock(arrival)} → "
                f"{end_day}{clock(departure)}**")
    st.caption(f"Currently supported: {SCOPE_TEXT}")
    with st.expander("Advanced: enter coordinates"):
        st.number_input("Latitude", key="adv_lat", format="%.6f")
        st.number_input("Longitude", key="adv_lon", format="%.6f")
        st.button("Use these coordinates", on_click=use_coordinates)

if state.dest:
    dest_lat, dest_lon = state.dest
    result = find_parking(meters(), dest_lat, dest_lon, arrival, duration)
else:
    result = None
evaluated = bool(result and not result.scope_reason and result.candidates)
rec_ids = ({c.meter.object_id for c in result.recommendations} if result and evaluated
           else set())
empty = bool(result and not result.scope_reason and not result.candidates)
pointer = nearest_supported_meter(*state.dest) if empty else None

# --- Map --------------------------------------------------------------------------

with right:
    st.toggle("Show all nearby meters", key="show_all")
    fmap = folium.Map(location=DOWNTOWN, zoom_start=16, tiles="OpenStreetMap",
                      control_scale=True)
    layer = folium.FeatureGroup(name="results")
    if state.dest:
        folium.Marker(state.dest, tooltip="Destination",
                      icon=folium.Icon(color="blue", icon="flag")).add_to(layer)
        folium.Circle(state.dest, radius=SEARCH_RADIUS_M, color="#0969da",
                      weight=1, fill=False, dash_array="6").add_to(layer)
    if result and evaluated:
        rank = {c.meter.object_id: i for i, c in enumerate(result.recommendations, 1)}
        near, closest = result.closest_legal, result.closest
        for c in result.candidates:
            status = status_of(c, rec_ids)
            colour, label = STATUS_STYLE[status]
            reason = c.result.reasons[0] if c.result.reasons else ""
            if status == "recommended":
                continue  # drawn below, grouped by location
            elif c is near:
                badge_marker(c.lat, c.lon, "★", colour, "white", colour, None, 900,
                             popup(c, f"★ Meter {c.meter.meter_id}",
                                   "Closest legal option")).add_to(layer)
            elif c is closest:
                folium.CircleMarker(
                    (c.lat, c.lon), radius=9, color="white", weight=3, fill=True,
                    fill_color=colour, fill_opacity=1, bubbling_mouse_events=False,
                    popup=folium.Popup(
                        f"<div style='font-size:13px;line-height:1.5'><b>Closest meter · "
                        f"{c.meter.meter_id}</b><br>About {c.distance_m:.0f} m away<br>"
                        f"<b style='color:{WARN}'>{label}</b><br><i>{reason}</i></div>",
                        max_width=280),
                ).add_to(layer)
            elif state.show_all:
                folium.CircleMarker(
                    (c.lat, c.lon), radius=6, color=colour, fill=True,
                    fill_opacity=0.6, weight=1, bubbling_mouse_events=False,
                    popup=folium.Popup(
                        f"<div style='font-size:13px;line-height:1.5'>"
                        f"<b>Meter {c.meter.meter_id}</b><br>{label}"
                        + (f"<br><i>{split_reason(reason)[0]}</i>" if reason else "")
                        + "</div>", max_width=240),
                ).add_to(layer)

    if result and evaluated:
        # Several meter records can share one block-face coordinate; draw one badge per spot.
        spots = {}
        for n, c in enumerate(result.recommendations, 1):
            spots.setdefault((round(c.lat, 6), round(c.lon, 6)), []).append((n, c))
        green = STATUS_STYLE["recommended"][0]
        for group in spots.values():
            first = group[0][1]
            label = "·".join(str(n) for n, _ in group)
            note = "Same block-face location in the data" if len(group) > 1 else ""
            pop = folium.Popup(
                "<hr style='margin:4px 0'>".join(
                    _popup_html(c, f"#{n} · Meter {c.meter.meter_id}")
                    for n, c in group)
                + (f"<div style='font-size:12px;color:#57606a'><i>{note}</i></div>" if note else ""),
                max_width=280)
            badge_marker(first.lat, first.lon, label, "white", green, "white",
                         None, 1000, pop).add_to(layer)

    if pointer:
        row, dist = pointer
        target = (float(row["lat"]), float(row["lon"]))
        dy = target[0] - state.dest[0]
        dx = (target[1] - state.dest[1]) * math.cos(math.radians(state.dest[0]))
        angle = -math.degrees(math.atan2(dy, dx))  # CSS rotation; 0 = pointing east
        blue = "#0969da"
        folium.PolyLine([state.dest, target], color=blue, weight=3,
                        dash_array="8 8").add_to(layer)
        folium.Marker(target, icon=folium.DivIcon(
            icon_size=(22, 22), icon_anchor=(11, 11),
            html=(f"<div style='transform:rotate({angle:.0f}deg);color:{blue};"
                  f"font-size:22px;line-height:22px'>➤</div>")),
            tooltip=tooltip(f"Nearest meter · {row['meter_id']}",
                            f"About {dist:.0f} m from your destination")).add_to(layer)
        mid = ((state.dest[0] + target[0]) / 2, (state.dest[1] + target[1]) / 2)
        folium.Marker(mid, icon=folium.DivIcon(
            icon_size=(180, 24), icon_anchor=(90, 12),
            html=(f"<div style='background:white;border:1px solid {blue};color:{blue};"
                  f"border-radius:12px;padding:2px 8px;font-size:13px;font-weight:600;"
                  f"white-space:nowrap;box-shadow:0 0 3px #0004;text-align:center'>"
                  f"Nearest meter ≈ {dist:.0f} m</div>"))).add_to(layer)

    st_folium(fmap, key="driver_map", height=520, use_container_width=True,
              feature_group_to_add=layer, center=state.dest or DOWNTOWN,
              returned_objects=["last_clicked"], on_change=handle_map_click)
    green, red = STATUS_STYLE["recommended"][0], STATUS_STYLE["conflict"][0]
    short = {"recommended": "Recommended", "legal": "Legal, not in top 3",
             "conflict": "Conflicts with a rule", "uncertain": "Uncertain rule",
             "unsupported": "Data not supported"}
    items = ([(STATUS_STYLE[k][0], "●", v) for k, v in short.items()] if state.show_all else
             [(green, "●", "Recommended"), (red, "●", "Not recommended")])
    items.append((green, "★", "Closest legal option"))
    st.markdown(
        "<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));"
        "gap:0.25rem 1rem;font-size:0.875rem;color:#6e7781;margin-bottom:0.75rem'>"
        + "".join(f"<span style='white-space:nowrap'><span style='color:{c}'>{s}</span> "
                  f"{text}</span>" for c, s, text in items)
        + "</div>", unsafe_allow_html=True)
    st.caption("Distances are approximate straight-line distances, not walking routes. "
               "Map data © OpenStreetMap contributors.")

# --- Results (full width) -----------------------------------------------------------

st.divider()
st.subheader("Results")

if not state.dest or result is None:
    st.write("Search a block or tap the map to choose a destination, or open Demo tools to "
             "load the example.")
elif result.scope_reason:
    st.warning(result.scope_reason)
elif not result.candidates:
    st.warning(f"No metered parking was found within {SEARCH_RADIUS_M} m. Street parking here "
               "may have no meter fee, but posted time limits, permit zones, and other rules "
               "still apply. CurbCheck does not evaluate unmetered parking.")
    if pointer:
        st.markdown(f"The nearest meter CurbCheck can evaluate is about **{pointer[1]:.0f} m** "
                    "away. Follow the dashed arrow on the map and move the destination pin "
                    "closer to see options there.")
else:
    recs = result.recommendations

    # Summary
    if recs:
        nearest = min(c.distance_m for c in recs)
        cheapest = min(c.result.estimated_cost for c in recs
                       if c.result.estimated_cost is not None)
        st.markdown(f"#### {len(recs)} option{'s' if len(recs) > 1 else ''} found")
        st.markdown(f"From **{money(cheapest)}** · Nearest recommendation about "
                    f"**{nearest:.0f} m** away")

    # Conflict count: supported records whose stay is definitely not legal
    n_conflict = sum(1 for c in result.candidates
                     if c.result.supported and c.result.legal is False)
    st.caption(f"{n_conflict} of {len(result.candidates)} meter records within "
               f"{SEARCH_RADIUS_M} m conflict with this stay.")

    # Closest meter card
    closest = result.closest
    assert closest is not None  # candidates is non-empty in this branch
    status = status_of(closest, rec_ids)
    if status == "recommended":
        n = [c.meter.object_id for c in recs].index(closest.meter.object_id) + 1
        tag, tag_colour, main, note = f"✓ Recommended #{n}", STATUS_STYLE[status][0], "", ""
    elif status == "legal":
        tag, tag_colour = "✓ Appears legal", STATUS_STYLE[status][0]
        main = (f"Not in the top three: estimated ${closest.result.estimated_cost:.2f}, "
                "more than the recommendations.")
        note = ""
    else:
        main, note = split_reason(closest.result.reasons[0] if closest.result.reasons else "")
        tag = {"conflict": "⚠ Not recommended",
               "uncertain": "⚠ Not recommended — uncertain rule",
               "unsupported": "Data not supported"}[status]
        tag_colour = STATUS_STYLE["unsupported"][0] if status == "unsupported" else WARN
    st.markdown(
        f"<div style='padding:0.6rem 1rem;"
        f"background:rgba(188,76,0,0.05);border-radius:4px'>"
        f"<div style='font-size:0.85rem;color:#57606a'>Closest meter</div>"
        f"<div style='font-weight:600'>{closest.meter.meter_id} · About "
        f"{closest.distance_m:.0f} m away</div>"
        f"<div style='color:{tag_colour};font-weight:700;margin-top:0.4rem'>{tag}</div>"
        + (f"<div>{main}</div>" if main else "") + "</div>",
        unsafe_allow_html=True)
    if note:
        label = ("Why CurbCheck applies this every day" if "every day" in note
                 else "More detail")
        with st.expander(label):
            st.caption(note)

    # Recommendation cards
    if recs:
        st.caption("Ranked by estimated cost; when costs are equal, the nearer meter comes "
                   "first. Numbers match the map.")
        for col, (i, c) in zip(st.columns(3), enumerate(recs, 1)):
            m = c.meter
            with col, st.container(border=True):
                st.markdown(f"**#{i} · Meter {m.meter_id}**")
                st.markdown(f"### {money(c.result.estimated_cost)}")
                st.markdown(f"About {c.distance_m:.0f} m away")
                st.caption(f"Daytime {money(m.rate_day)}/h · Evening {money(m.rate_evening)}/h")
                for w in c.result.warnings:
                    st.caption(w)
                st.link_button("Directions ↗", directions_url(c.lat, c.lon))

        near = result.closest_legal
        if near and near not in recs:
            st.markdown(f"★ **Closest legal option:** Meter {near.meter.meter_id}, about "
                        f"{near.distance_m:.0f} m away, estimated "
                        f"{money(near.result.estimated_cost)}. "
                        f"[Directions ↗]({directions_url(near.lat, near.lon)})")
        st.caption("Directions open Google Maps to the meter's block, not an exact space.")
    else:
        supported = [c for c in result.candidates if c.result.supported]
        if not supported:
            st.warning("Meter records near this destination could not be evaluated safely, "
                       "so CurbCheck cannot recommend one.")
        else:
            st.warning("Every nearby meter that CurbCheck can evaluate conflicts with this stay.")
            st.markdown("**Most common reasons:**")
            for reason, n in Counter(split_reason(r)[0] for c in supported
                                     for r in c.result.reasons).most_common(3):
                st.caption(f"{n} × {reason}")
        st.markdown("**Try:** a shorter stay, a later arrival time, or moving the "
                    "destination pin.")

    # Full table
    with st.expander(f"All {len(result.candidates)} meter records within {SEARCH_RADIUS_M} m"):
        details = st.checkbox("Show rates and limits")
        rows = []
        for c in result.candidates:
            row = {
                "Meter": c.meter.meter_id,
                "Distance (m)": round(c.distance_m),
                "Status": STATUS_STYLE[status_of(c, rec_ids)][1],
                "Main reason": split_reason(c.result.reasons[0])[0] if c.result.reasons else "",
            }
            if details:
                row.update({
                    "Estimated cost": c.result.estimated_cost,
                    "Daytime rate": c.meter.rate_day,
                    "Evening rate": c.meter.rate_evening,
                    "Daytime limit": limit_text(c.meter.limit_day),
                    "Evening limit": limit_text(c.meter.limit_evening),
                })
            rows.append(row)
        st.dataframe(rows, hide_index=True, width="stretch")

st.info("Posted signs take precedence.")

# --- Data period and limitations ---------------------------------------------------

meter_report = json.loads((DATA / "meters_preprocessing_report.json").read_text(encoding="utf-8"))
st.divider()
st.markdown("**Data period and limitations**")
st.caption(
    "Meters: City of Vancouver open data (`parking-meters`), snapshot downloaded "
    f"{meter_report['downloaded_at'][:10]} ({meter_report['total_records']:,} records; "
    f"{meter_report['supported_records']:,} can be evaluated by the rules engine, and the rest "
    "are excluded for missing or unsupported data)."
)
st.caption(
    "Results use only the rates, time limits, and rush-hour restrictions listed for each meter. "
    "They do not include posted or temporary signs, construction closures, or real-time space "
    "availability, and unmetered street parking is not covered. Costs are estimates, and "
    "distances are straight-line, not walking routes."
)
