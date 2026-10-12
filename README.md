# CurbCheck

Vancouver's street parking rules switch by time of day. CurbCheck helps drivers check whether a whole stay is legal and what it will cost, and shows the City where its rules trip people up.

Built for the Trilemma × Northeastern Datathon, Vancouver (2026).

**Demo video (60 s):** https://youtu.be/AlxIEvF085s

## What it does

**Driver View** — for someone about to park.

- Choose a destination by tapping the map (or entering coordinates), then set the arrival time and duration.
- CurbCheck checks every metered record within 250 m against the whole stay: rates, time limits, and rush-hour restrictions that start or end during the stay.
- It recommends up to three options, ranked by estimated cost and then distance, and explains why the closest meter is or is not recommended.
- It shows how many nearby meter records conflict with the stay, so changing the arrival time shows how the answer changes.
- Each recommendation has a Directions link that opens Google Maps to the meter's block (a URL link; no API key or Google service call).

**City View** — for City staff and planners.

- Overlays meter rates (citywide) with ticket counts for Downtown blocks, 2025-01-01 to 2026-06-30.
- Filter the map by infraction category and inspect any block's ticket breakdown.
- Three precomputed insights, reviewed against the ticket aggregate, highlight where tickets concentrate (for example, rush-hour tickets on Seymour, Howe, and West Pender).

CurbCheck gives data-based guidance, not a legal guarantee.

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `pytest`.

Posted signs take precedence over CurbCheck's results.

## Data sources and licence

All data comes from the City of Vancouver Open Data portal. The Trilemma Foundation data catalog links to these datasets; it does not host or relicense them. Raw snapshots are kept in `data/raw/` and are not committed; the app reads only the processed files in `data/`.

| Dataset (ID) | Used for | Source | Snapshot |
| --- | --- | --- | --- |
| Parking meters (`parking-meters`) | Driver View rules, rates, map; City View rate layer | https://opendata.vancouver.ca/explore/dataset/parking-meters/ | Downloaded 2026-10-11 19:11 UTC, 3,642 records |
| Parking tickets 2026 (`parking-tickets`) | City View, 2026-01-01 to 2026-06-30 | https://opendata.vancouver.ca/explore/dataset/parking-tickets/ | Downloaded October 2026 |
| Parking tickets 2020–2025 (`parking-tickets-2020-2025`) | City View, 2025 rows | https://opendata.vancouver.ca/explore/dataset/parking-tickets-2020-2025/ | Downloaded October 2026 |
| Property addresses (`property-addresses`) | Block coordinates for tickets; demo destination coordinate | https://opendata.vancouver.ca/explore/dataset/property-addresses/ | Downloaded October 2026 |

**Licence.** Contains information licensed under the Open Government Licence – Vancouver (https://opendata.vancouver.ca/pages/licence/).

**Map.** Base map tiles and map data © OpenStreetMap contributors (https://www.openstreetmap.org/copyright).

**Parking rules.** The by-laws, City pages, and Council records used to interpret parking rules are listed in `references.md`.

Team conventions are in `CONTRIBUTING.md`.

## Driver View meter data

`python -m curbcheck.meters` reads the meter snapshot in `data/raw/` and writes `data/meters_clean.csv` and `data/meters_preprocessing_report.json`.

**Source:** City of Vancouver open data, `parking-meters`, snapshot downloaded 2026-10-11 19:11 UTC (3,642 records). After preprocessing, 2,760 records citywide (636 Downtown) can be evaluated by the rules engine; the report lists every reason a record was excluded. Rule interpretations and their official sources are in `references.md`, Section 5.

## Demo scenario

`Load demo example` on the Driver View loads **400 W Hastings St, Tuesday, October 13, 2026, arriving at 6:00 pm for 2 hours**. The coordinate is the 400 W Hastings block location from `data/block_coords.csv`.

**Why this location.** We checked every Downtown block with a known coordinate against three criteria: at least three recommendations at 6:00 pm, a closest meter that is rejected by a specific parking rule rather than by missing data, and a clear change when the arrival time moves earlier. 400 W Hastings met all three most clearly:

1. **The closest meter, about 17 m away, is not recommended at 6:00 pm.** Its listed PM rush-hour restriction runs from 3:00 pm to 7:00 pm, so a driver who assumes the evening has started would still be parking in a rush-hour zone.
2. **Legal options exist and the trade-off is visible.** The three recommendations cost an estimated $4.00 each and are about 130–170 m away, while other legal meters nearby cost more, so the cheapest option is not the closest one.
3. **Time changes the answer.** Moving the arrival to 5:00 pm raises the number of conflicting meters within 250 m from 12 to 32, mostly because of rush-hour overlaps.

**Demo flow.** Load the demo example and walk through the recommendations; hover over the closest red marker to show the rush-hour reason; then change the arrival time to 5:00 pm and show how many more meters conflict.

These results come from the 2026-10-11 snapshot. A later snapshot may change them.

## City View ticket data

`python scripts/build_tickets.py` reads the raw files in `data/raw/` and writes `data/tickets_block_agg.csv` (plus `data/block_coords.csv` and a run log, `data/tickets_report.txt`). The page reads the CSV; it does not clean raw data.

**Sources (snapshot downloaded October 2026, City of Vancouver open data):** `parking-tickets-2020-2025` (2025 rows), `parking-tickets` (2026-01-01 to 2026-06-30), `property-addresses` (block coordinates). Scope: Downtown Vancouver, 2025-01-01 to 2026-06-30.

**Processing rules**

| Step | Rule | Result |
| --- | --- | --- |
| Issued tickets | `status == "IS"` | 578,439 kept |
| De-duplication | One row per `bi_id` | 40,642 duplicates removed |
| Water tickets | Removed when `bylaw == 12086` (Water Conservation By-law, the only water bylaw in the data) or the text contains "WATER"/"WATERING". Both tests removed the same rows. | 1,317 removed |
| Street names | One normalizer for tickets and addresses (uppercase, punctuation stripped, AVE→AV, BLVD→BOULEVARD, RD→ROAD, DR→DRIVE, HWY→HIGHWAY, leading WEST/EAST/NORTH/SOUTH→W/E/N/S) | |
| Block | Civic number rounded down to the hundred + normalized street = `block_key`; coordinates are the mean of the addresses in that block | 9,694 blocks |
| Downtown | `local_area == "Downtown"`, taken from the property-address `Geo Local Area` after the join | 183,188 tickets |
| Categories | Explicit bylaw/section mapping first, keyword rules second: Meter expired, Overstayed limit, Rush-hour no stopping, Loading zone, Fire hydrant, Posted sign restriction, Residential permit zone, Other | See below |

**Estimated block coordinates.** The property-address data is incomplete: 1,256 ticket blocks have no address, including busy Downtown blocks such as 700 Nelson St and 400 Hamilton St. For 756 of them we estimate the location as the mean of known blocks on the same street within ±100 (or ±200 if none are that close). Those rows carry `coord_estimated = True` and cover 32,273 tickets, so their map positions are approximate. Blocks with no neighbour within 200 stay unmatched.

**Data quality**

- Matched to a block coordinate: 528,043 of 536,480 tickets (98.4%). Unmatched: 8,437 tickets, mostly in newer areas (e.g. Coal Harbour Quay, River District, Sawmill Crescent). They are excluded from the map and counted here.
- Of the matched tickets, 183,188 fall in Downtown and are in the aggregate; the aggregate reconciles with those source rows.
- "Residential permit zone" has no matching tickets in this data and appears with a count of zero (or not at all).
- Tickets have a date but no time of day, and locations are only to the 100-block.
- The data excludes VPD-issued tickets. Ticket counts show where enforcement happened, not parking demand.
