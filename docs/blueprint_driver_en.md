# CurbCheck Blueprint — Driver View (English)

> Owner: Yan-Bo · Version: Draft v0.1 · Demo Day: Tue 10/13
> Companion document: `blueprint_city_en.md` (City view, owned by Anahid and Juwon)

---

## 1. Goal

On a real map of Vancouver, the user picks a destination and enters an arrival time and duration. CurbCheck lists the top three street parking options within walking distance that are **legal for the whole stay** at the **lowest total cost**, and explains why the closest meter can't be used.

Scope: **all parking meters in Vancouver** (3,642 records, of which 3,264 are In Service — small enough to cover the whole city).

## 2. User Flow

1. **Pick a destination**: tap a location on the real map.
2. **Enter the stay**: arrival time, duration, weekday or weekend.
3. **Find candidate meters**: meters within walking distance of the destination (default 250 m).
4. **Evaluate each one**: is the whole stay legal (rush hours, prohibitions, per-window time limits), and what is the total cost across time windows?
5. **Rank**: legal options first, then by total cost and walking distance; keep the top three.
6. **Show results**: the map marks the top three and the spots that can't be used; the side panel lists cost, walking distance, and why the closest meter can't be used.
7. **Block heads-up** (stretch): the most common infraction type near the top options, using data from the City view team.

## 3. Architecture

| Component | Description |
| --- | --- |
| Data prep | Download meter data, keep only meters whose `service_status` is In Service, parse rule text, output `meters_clean` |
| Rules engine | Input "meter rules + arrival time + duration," output "legal or not, reasons, total cost" |
| Driver page | The `driver` page of a Streamlit multipage app: map, inputs, results list |
| Map | `folium` (with `streamlit-folium`) on OpenStreetMap tiles |

### Rules Engine Spec

- **Input**: one meter's rules, arrival time, duration, weekday or weekend.
- **Time windows**: daytime 9am–6pm, evening 6pm–10pm, free from 10pm to 9am.
- **Legality**: the stay must not overlap rush hours or prohibition periods, and time spent in each window must not exceed that window's limit.
- **Cost**: hours in each window × that window's rate, summed.
- **Output**: `legal`, `reasons` (why it isn't legal), `cost`.

## 4. Data Sources

| Data | Source / dataset ID | URL | Fields used | In Trilemma catalog? | Role |
| --- | --- | --- | --- | --- | --- |
| Parking meters | City of Vancouver open data `parking-meters` | https://opendata.vancouver.ca/explore/dataset/parking-meters/ | `meter_id`, `geo_point_2d`, `local_area`, `rate_9am_6pm`, `rate_6pm_10pm`, `flat_rate`, `time_limit_9am_6pm`, `time_limit_6pm_10pm`, `time_limit_weekend_9am_6pm`, `time_limit_weekend_6pm_10pm`, `am_rush_hours`, `pm_rush_hours`, `prohibition_1_days`, `prohibition_1_time`, `prohibition_1_zone`, `vehicle_type`, `service_status` | ❌ (supplementary public data) | **Core** |
| Base map | OpenStreetMap tiles | https://www.openstreetmap.org/ | — | — (attribution required) | Base map |
| Ticket summary | `tickets_block_agg`, produced by the City view team | — | See Section 5 | Derived from catalog data | Stretch (block heads-up) |

Known limitations:

- Meter data has **no street field** — only coordinates and local area.
- One record may be **one pay station covering several spaces**.
- 359 meters are Out of Service and 19 are Removed; these are excluded so the app never recommends a meter that can't be used.
- No real-time availability; the UI reminds users that posted signs win.

## 5. Shared Interface

> The authoritative shared-data schemas are defined in `mvp_implementation_handoff_en.md`.

Both views live in **one Streamlit multipage app**, each in its own page file, so neither team blocks the other.

| Item | Agreement |
| --- | --- |
| Page files | Driver view: `pages/driver.py` (Yan-Bo); City view: `pages/city.py` (Anahid, Juwon) |
| Coordinates | WGS84 latitude/longitude (`lat`, `lon`) |
| Map component | `folium` + `streamlit-folium`, OpenStreetMap tiles, centered on downtown Vancouver by default |
| Data file format | CSV, stored in the `data/` folder |

### Exchanged Data Files

| File | Columns | Produced by | Used by |
| --- | --- | --- | --- |
| `meters_clean.csv` | `meter_id`, `lat`, `lon`, `local_area`, `rate_day`, `rate_evening`, `flat_rate`, `limit_day_hr`, `limit_evening_hr`, `limit_wkend_day_hr`, `limit_wkend_evening_hr`, `am_rush_start`, `am_rush_end`, `pm_rush_start`, `pm_rush_end`, `prohibition_text`, `vehicle_type` | Driver view | Driver view; City view (optional, e.g., a rate layer) |
| `tickets_block_agg.csv` | `block_key`, `lat`, `lon`, `weekday`, `category`, `count` | City view | City view; Driver view (stretch: block heads-up) |

`tickets_block_agg.csv` is a stretch dependency: if the City view team can't deliver it in time, the Driver view's core features are unaffected.

## 6. Completion Levels

| Level | Scope | Target |
| --- | --- | --- |
| **Must have** | Steps 1–6, real map, deployed online | End of Day 2 |
| **Stretch** | Step 7 block heads-up (needs `tickets_block_agg.csv`) | Before noon on Day 3 |
| **Out of scope** | Real-time availability, parkade prices, native app | — |
