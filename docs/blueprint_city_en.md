# CurbCheck Blueprint — City View (English)

> Owners: Anahid, Juwon · Version: Draft v0.1 · Demo Day: Tue 10/13
> Companion document: `blueprint_driver_en.md` (Driver view, owned by Yan-Bo)

---

## 1. Goal

Show City parking management, enforcement, and transportation planning staff **which blocks tickets concentrate on, which infraction types are most common, and when 311 parking enforcement requests peak**, with two or three insights, e.g., "Blocks where one infraction type is unusually concentrated may have unclear signs or rules."

Scope: **downtown Vancouver**, January 2025 – June 2026 tickets. If progress allows, extend the aggregated results to the whole city.

Metric principle: ticket counts show **where enforcement happened**, not parking demand or the probability of a ticket.

## 2. User Flow

1. **Set the scope**: downtown, January 2025 – June 2026, optional weekday filter.
2. **Ticket concentration layer**: blocks colored by ticket volume; stronger color means more tickets.
3. **Select a block**: show that block's infraction-type breakdown.
4. **311 hour-of-day chart**: requests by hour, filling the time-of-day gap that tickets lack.
5. **Insights panel**: two or three key findings.

## 3. Architecture

| Component | Description |
| --- | --- |
| Ticket cleaning | Keep issued tickets only (by `status`), de-duplicate by `bi_id`, filter out water tickets, limit to downtown and January 2025 – June 2026 |
| Infraction categories | Group by `bylaw`, `section`, and `infractiontext` keywords into: meter expired, overstayed limit, rush-hour no stopping, loading zone, fire hydrant, residential permit zone, other |
| Block coordinates | Group the address data by "civic number rounded down to the hundred + street," average the coordinates, output `block_coords`, then join to tickets on `block` + `street` |
| 311 processing | Filter `service_request_type` to Parking Enforcement Request Case; aggregate by hour and weekday |
| City page | The `city` page of a Streamlit multipage app: ticket layer, block details, 311 chart, insights |
| Map | `folium` (with `streamlit-folium`) on OpenStreetMap tiles |

## 4. Internal Split

| Member | Responsibilities |
| --- | --- |
| Anahid | (to be filled in) |
| Juwon | (to be filled in) |

## 5. Data Sources

| Data | Source / dataset ID | URL | Fields used | In Trilemma catalog? | Role |
| --- | --- | --- | --- | --- | --- |
| Parking tickets 2026 | Trilemma `vancouver-parking-tickets`; City open data `parking-tickets` | https://opendata.vancouver.ca/explore/dataset/parking-tickets/ | `block`, `street`, `entrydate`, `bylaw`, `section`, `status`, `infractiontext`, `year`, `bi_id` | ✅ | **Core** (2026-01-02 to 2026-06-30, ~238k records) |
| Parking tickets 2020–2025 | City open data `parking-tickets-2020-2025` | https://opendata.vancouver.ca/explore/dataset/parking-tickets-2020-2025/ | Same as above | History for the same series (the Trilemma entry links to the 2026 version) | Supplementary (2025 only) |
| Property addresses | Trilemma `vancouver-property-addresses`; City open data `property-addresses` | https://opendata.vancouver.ca/explore/dataset/property-addresses/ | `civic_number`, `std_street`, `geo_point_2d` | ✅ | **Core** (block coordinates) |
| 3-1-1 service requests | Trilemma `vancouver-311-service-requests`; City open data `3-1-1-service-requests` | https://opendata.vancouver.ca/explore/dataset/3-1-1-service-requests/ | `service_request_type`, `service_request_open_timestamp`, `latitude`, `longitude`, `local_area` | ✅ | **Core** (time of day) |
| Parking meters | `meters_clean`, produced by the Driver view | — | See Section 6 | ❌ (supplementary public data) | Optional (rate layer) |
| Base map | OpenStreetMap tiles | https://www.openstreetmap.org/ | — | — (attribution required) | Base map |

Known limitations:

- Tickets have **a date but no time of day**, and locations only to the 100-block.
- 2026 data currently runs to June 30 and is updated quarterly.
- Ticket data **excludes VPD-issued tickets**.
- The 2020-onward ticket data **includes water tickets**, which must be filtered out.
- 311 records are **resident complaints**, not tickets issued; present them separately.

## 6. Shared Interface

> The authoritative shared-data schemas are defined in `mvp_implementation_handoff_en.md`.

Both views live in **one Streamlit multipage app**, each in its own page file, so neither team blocks the other.

| Item | Agreement |
| --- | --- |
| Page files | Driver view: `views/driver.py` (Yan-Bo); City view: `views/city.py` (Anahid, Juwon) |
| Coordinates | WGS84 latitude/longitude (`lat`, `lon`) |
| Map component | `folium` + `streamlit-folium`, OpenStreetMap tiles, centered on downtown Vancouver by default |
| Data file format | CSV, stored in the `data/` folder |

### Exchanged Data Files

| File | Columns | Produced by | Used by |
| --- | --- | --- | --- |
| `meters_clean.csv` | `meter_id`, `lat`, `lon`, `local_area`, `rate_day`, `rate_evening`, `flat_rate`, `limit_day_hr`, `limit_evening_hr`, `limit_wkend_day_hr`, `limit_wkend_evening_hr`, `am_rush_start`, `am_rush_end`, `pm_rush_start`, `pm_rush_end`, `prohibition_text`, `vehicle_type` | Driver view | Driver view; City view (optional, e.g., a rate layer) |
| `tickets_block_agg.csv` | `block_key`, `lat`, `lon`, `weekday`, `category`, `count` | City view | City view; Driver view (stretch: block heads-up) |

## 7. Completion Levels

| Level | Scope | Target |
| --- | --- | --- |
| **Must have** | Steps 1–5; output `tickets_block_agg.csv` | End of Day 2 |
| **Fallback** | If the page isn't working by the end of Day 2, turn it into one analysis slide (charts + insights) | Decide at the end of Day 2 |
| **Out of scope** | Forecasting models, natural-language queries, citywide ticket analysis (in the MVP) | — |
