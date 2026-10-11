"""Driver View — owner: Yan-Bo.

Find street parking that is legal for the whole stay and estimate its cost.
Spec: mvp_implementation_handoff_en.md, Sections 6–8.
"""
from collections import Counter
from datetime import date, datetime, time, timedelta

import folium
import streamlit as st
from streamlit_folium import st_folium

from curbcheck.ranking import SEARCH_RADIUS_M, find_parking, load_meters
from curbcheck.rules import NO_TIME_LIMIT, SAME_DAY_WINDOW_ONLY

st.set_page_config(page_title="CurbCheck — Driver View", page_icon="🚗", layout="wide")

DOWNTOWN = (49.2820, -123.1180)
DEMO = {  # provisional demo values (next_steps_driver.md, Step 0)
    "dest": (49.2827, -123.1207),
    "date": date(2026, 10, 13),
    "time": time(18, 0),
    "hours": 2.0,
}
SCOPE_TEXT = ("Same-day stays between 9:00 am and 10:00 pm." if SAME_DAY_WINDOW_ONLY
              else "Stays of up to 24 hours that cross at most one midnight.")
STATUS_STYLE = {  # status -> (marker colour, label)
    "recommended": ("#1a7f37", "Recommended"),
    "legal": ("#4c9a5a", "Appears legal (not in top 3)"),
    "conflict": ("#cf222e", "Conflicts with a listed restriction or limit"),
    "uncertain": ("#bf8700", "Uncertain rule — not recommended"),
    "unsupported": ("#8c959f", "Data not supported"),
}


@st.cache_data
def meters():
    return load_meters()


# --- Session state --------------------------------------------------------------

state = st.session_state
state.setdefault("dest", None)
state.setdefault("last_click", None)
state.setdefault("arrival_date", date.today())
state.setdefault("arrival_time", time(18, 0))
state.setdefault("duration_hours", 2.0)
state.setdefault("adv_lat", DOWNTOWN[0])
state.setdefault("adv_lon", DOWNTOWN[1])


def load_demo():
    state.dest = DEMO["dest"]
    state.arrival_date = DEMO["date"]
    state.arrival_time = DEMO["time"]
    state.duration_hours = DEMO["hours"]
    state.adv_lat, state.adv_lon = DEMO["dest"]


def use_coordinates():
    state.dest = (state.adv_lat, state.adv_lon)


def limit_text(minutes):
    if minutes is None:
        return "—"
    return "No limit" if minutes == NO_TIME_LIMIT else f"{minutes} min"


TOOLTIP_STYLE = ("white-space: normal; width: max-content; max-width: 280px; "
                 "font-size: 13px;")


def tooltip(title, label, reason=""):
    """A wrapped tooltip so long reasons stay inside the map."""
    html = f"<b>{title}</b><br>{label}" + (f"<br><i>{reason}</i>" if reason else "")
    return folium.Tooltip(html, style=TOOLTIP_STYLE)


def status_of(candidate, recommended_ids):
    r = candidate.result
    if not r.supported:
        return "unsupported"
    if candidate.meter.object_id in recommended_ids:
        return "recommended"
    if r.legal is True:
        return "legal"
    return "conflict" if r.legal is False else "uncertain"


# --- Inputs -----------------------------------------------------------------------

st.page_link("app.py", label="Home", icon="🏠")
st.title("Driver View")
st.caption("Find metered street parking that appears legal for your whole stay.")

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Your stay")
    st.date_input("Date", key="arrival_date")
    st.time_input("Arrival time", key="arrival_time", step=timedelta(minutes=15))
    st.number_input("Duration (hours)", key="duration_hours",
                    min_value=0.25, max_value=24.0, step=0.25)
    st.caption(f"Currently supported: {SCOPE_TEXT}")
    st.button("Load demo example", on_click=load_demo)

    with st.expander("Advanced: enter coordinates"):
        st.number_input("Latitude", key="adv_lat", format="%.6f")
        st.number_input("Longitude", key="adv_lon", format="%.6f")
        st.button("Use these coordinates", on_click=use_coordinates)

arrival = datetime.combine(state.arrival_date, state.arrival_time)
duration = int(round(state.duration_hours * 60))
result = (find_parking(meters(), *state.dest, arrival, duration)
          if state.dest else None)

# --- Map --------------------------------------------------------------------------

with right:
    fmap = folium.Map(location=state.dest or DOWNTOWN, zoom_start=17,
                      tiles="OpenStreetMap", control_scale=True)
    if state.dest:
        folium.Marker(state.dest, tooltip="Destination",
                      icon=folium.Icon(color="blue", icon="flag")).add_to(fmap)
        folium.Circle(state.dest, radius=SEARCH_RADIUS_M, color="#0969da",
                      weight=1, fill=False, dash_array="6").add_to(fmap)
    if result and not result.scope_reason:
        rec_ids = {c.meter.object_id for c in result.recommendations}
        rank = {c.meter.object_id: i for i, c in enumerate(result.recommendations, 1)}
        for c in result.candidates:
            status = status_of(c, rec_ids)
            colour, label = STATUS_STYLE[status]
            if status == "recommended":
                n = rank[c.meter.object_id]
                folium.Marker(
                    (c.lat, c.lon),
                    tooltip=tooltip(f"#{n} Meter {c.meter.meter_id}", label),
                    icon=folium.DivIcon(
                        icon_size=(26, 26), icon_anchor=(13, 13),
                        html=(f"<div style='width:26px;height:26px;border-radius:50%;"
                              f"background:{colour};color:white;font-weight:700;"
                              f"font-size:14px;line-height:26px;text-align:center;"
                              f"border:2px solid white;box-shadow:0 0 3px #0006'>{n}</div>"),
                    ),
                    z_index_offset=1000,
                ).add_to(fmap)
            else:
                folium.CircleMarker(
                    (c.lat, c.lon), radius=6, color=colour, fill=True,
                    fill_opacity=0.85, weight=2,
                    tooltip=tooltip(f"Meter {c.meter.meter_id}", label,
                                    c.result.reasons[0] if c.result.reasons else ""),
                ).add_to(fmap)

    st.caption("Drag or zoom the map, then click to set your destination.")
    clicked = st_folium(fmap, key="driver_map", height=520, use_container_width=True,
                        returned_objects=["last_clicked"])
    click = (clicked or {}).get("last_clicked")
    if click and click != state.last_click:
        state.last_click = click
        state.dest = (click["lat"], click["lng"])
        st.rerun()
    st.caption("Distances are approximate straight-line distances, not walking routes. "
               "Map data © OpenStreetMap contributors.")
    st.caption(" · ".join(f"<span style='color:{c}'>●</span> {l}"
                          for c, l in STATUS_STYLE.values()), unsafe_allow_html=True)

# --- Results ----------------------------------------------------------------------

with left:
    st.subheader("Results")
    if not state.dest:
        st.write("Click the map to set your destination, or load the demo example.")
    elif result.scope_reason:
        st.warning(result.scope_reason)
    elif not result.candidates:
        st.warning(f"No meter records were found within {SEARCH_RADIUS_M} m of this destination.")
    else:
        if result.recommendations:
            st.caption("Ranked by estimated cost; when costs are equal, the nearer "
                       "meter comes first. Numbers match the map.")
        for i, c in enumerate(result.recommendations, 1):
            m = c.meter
            with st.container(border=True):
                st.markdown(f"**#{i} · Meter {m.meter_id}**")
                st.markdown(f"Estimated cost: **${c.result.estimated_cost:.2f}**  \n"
                            f"About {c.distance_m:.0f} m away  \n"
                            f"Rates: ${m.rate_day:.2f}/h daytime · "
                            f"${m.rate_evening:.2f}/h evening")
                for w in c.result.warnings:
                    st.caption(w)

        if not result.recommendations:
            supported = [c for c in result.candidates if c.result.supported]
            if not supported:
                st.warning("Meter records near this destination could not be evaluated "
                           "safely, so CurbCheck cannot recommend one.")
            else:
                st.warning("Every nearby meter that CurbCheck can evaluate conflicts "
                           "with this stay.")
                top = Counter(r for c in supported for r in c.result.reasons).most_common(3)
                for reason, n in top:
                    st.caption(f"{n} × {reason}")

        closest = result.closest
        if closest.meter.object_id not in {c.meter.object_id for c in result.recommendations}:
            why = closest.result.reasons[0] if closest.result.reasons else "Not in the top three."
            st.info(f"The closest meter ({closest.meter.meter_id}, about "
                    f"{closest.distance_m:.0f} m away) is not recommended: {why}")

        with st.expander(f"All {len(result.candidates)} meter records within {SEARCH_RADIUS_M} m"):
            rec_ids = {c.meter.object_id for c in result.recommendations}
            st.dataframe(
                [{
                    "Meter": c.meter.meter_id,
                    "Distance (m)": round(c.distance_m),
                    "Status": STATUS_STYLE[status_of(c, rec_ids)][1],
                    "Estimated cost": c.result.estimated_cost,
                    "Daytime limit": limit_text(c.meter.limit_day),
                    "Reasons": "; ".join(c.result.reasons),
                } for c in result.candidates],
                hide_index=True, width="stretch",
            )

    st.info("Posted signs take precedence.")
