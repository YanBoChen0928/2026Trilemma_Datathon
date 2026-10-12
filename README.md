# CurbCheck

Vancouver's street parking rules switch by time of day. CurbCheck helps drivers check whether a whole stay is legal and what it will cost, and shows the City where its rules trip people up.

Built for the Trilemma × Northeastern Datathon, Vancouver (2026) by Anahid Raisrohani, Juwon Park, and Yan-Bo Chen.

**Live app:** https://curbcheck.streamlit.app

**Demo video (60 s):** https://youtu.be/AlxIEvF085s

## One-sentence value

Vancouver's street parking rules switch by time of day, and drivers get them wrong. CurbCheck helps drivers see whether their whole stay is legal and what it will cost, and shows the City where its rules trip people up most.

## Problem

- Rules switch by time of day: daytime and evening rates differ, time limits differ, rush-hour restrictions apply, and meters are free after 10 pm. In the meter data, about 92% of meters have different daytime and evening time limits.
- Drivers slip up when a stay crosses a time boundary, like parking at 5 pm in a spot restricted from 3 to 6 pm. Existing tools (PayByPhone for payment, SpotAngels and ParkMe for prices) rarely check whether a whole stay is legal.
- The City lacks a combined view: it publishes ticket and meter data, but no tool puts the rules next to where people actually get them wrong, which makes it hard to see where signs or rules need work.
- The project is intentionally scoped to help before parking, not to show live spot availability.

## Users and use cases

| View | Users | Question they want answered |
| --- | --- | --- |
| Driver (demo lead) | Drivers heading downtown, delivery and service drivers, visitors | "I need 3 hours from 5 pm — where nearby is legal and cheap?" |
| City | Parking management, enforcement, transportation planners | "Which areas and infraction types are most concentrated? Are our rules easy to get wrong?" |

**Not for**: finding an open spot right now. No public real-time occupancy data exists.

## Solution

CurbCheck brings the two audiences together on one map and one rules engine:

- A Driver View that checks a full stay (arrival time + duration) against nearby meter rules and totals the cost across time windows.
- A City View that overlays meter rates with ticket concentrations and highlights where enforcement clusters by infraction type and block.
- A transparent rules engine and preprocessed data so users can see why a meter is recommended, rejected, or unsupported.

The app is designed as a decision-support prototype, not a legal guarantee.

## What it does

### Driver View

For someone about to park:

- Choose a destination by searching for a Vancouver block (type part of a street name, for example "400 W Hastings"), tapping the map, or entering coordinates. Then set the arrival time and duration.
- CurbCheck checks every metered record within 250 m against the whole stay: rates, time limits, and rush-hour restrictions that start or end during the stay.
- It recommends up to three options, ranked by estimated cost and then distance, and explains why the closest meter is or is not recommended.
- It shows how many nearby meter records conflict with the stay, so changing the arrival time shows how the answer changes.
- Each recommendation has a Directions link that opens Google Maps to the meter's block (a URL link; no API key or Google service call).

### City View

For City staff and planners:

- Overlays meter rates (citywide) with ticket counts for Downtown blocks, 2025-01-01 to 2026-06-30.
- Filter the map by infraction category and inspect any block's ticket breakdown.
- Three precomputed insights, reviewed against the ticket aggregate, highlight where tickets concentrate (for example, rush-hour tickets on Seymour, Howe, and West Pender).

The app also has a Home page with the 60-second demo and an About page with the problem, the team, the organizers, and the data sources.

CurbCheck gives data-based guidance, not a legal guarantee.

## Worked example

Rules: daytime (9am–6pm) $5.00/hr, 2-hour limit; evening (6pm–10pm) $3.50/hr, 4-hour limit; PM rush hours 3pm–6pm.

| Your plan | CurbCheck's answer |
| --- | --- |
| Arrive 1 pm, stay 3 hours | ❌ Daytime limit is 2 hours, and rush hours start at 3 pm |
| Arrive 5 pm, stay 3 hours | ❌ 5–6 pm falls in rush hours; you can't park here |
| Arrive 6 pm, stay 3 hours | ✅ Evening rate, $10.50 total, within the 4-hour limit |

(Rush hours typically mean no parking or tow-away; confirm the exact rule against posted signs.)

## What works now vs. what remains

### What works now

- The full driver flow works end to end: select a destination, choose arrival and duration, evaluate nearby meters, and review a recommendation ranked by price and proximity.
- The app explains reasons for rejection, including restrictions that overlap a stay, time limits, and other nearby conflicts.
- The map and results are auditable: each recommendation has a transparent reason and a user-facing explanation.
- City View loads a downtown ticket aggregate, overlays meter rates, and surfaces category filters and precomputed insights.
- The preprocessing pipeline, rule engine, and ranking logic are implemented in Python and tested separately from the Streamlit interface.
- The project includes a single deployable Streamlit app, a block-search workflow, and a City/Driver toggle.

### What remains / future improvements

- Improve the mobile and responsive layout so the app is easier to use on a phone.
- Add more compact result summaries and filters for recommended, conflicting, and unsupported meters.
- Improve the no-result state with clear next actions when no legal option exists.
- Keep the current offline block-search flow as the reliable default, while future address-search features would require external geocoding and privacy review.
- Keep the rule engine and pricing logic in a backend-safe Python layer so a future React or FastAPI version can reuse the same logic without duplication.
- Expand the City View with more filters and richer explanatory insights.
- Add stronger accessibility, map clustering, and more compact explanations.

The main future goal is to make CurbCheck easier to use on a phone and easier to evolve into a production web application without rewriting verified parking rules.

## Live app and demo flow

**Live app:** https://curbcheck.streamlit.app

**Demo video (60 s):** https://youtu.be/AlxIEvF085s

The Home page includes the 60-second demo. The app is designed to show the full decision path for both the driver and the city-side analysis. In the default demo, the app loads the 400 W Hastings example and demonstrates how a nearby meter can be rejected because of a rush-hour restriction even when it is close.

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `pytest`.

## Project structure

```text
app.py              Entry point: top navigation and the shared footer
views/              Pages: home.py, driver.py, city.py, about.py
curbcheck/          Meter preprocessing, rules engine, and ranking
scripts/            Ticket data pipeline (build_tickets.py)
data/               Processed data the app reads (raw snapshots stay local)
assets/             Logo, favicon, team photos, and QR codes
.streamlit/         Theme
docs/               Planning, design, and team process documents
tests/              pytest tests
```

Pages live in `views/` rather than `pages/`, because Streamlit treats a `pages/` folder as its own automatic navigation.

Posted signs take precedence over CurbCheck's results.

## How the app works

At a high level, the system combines the rules interpretation layer with a cleaned data layer:

1. Meter and ticket data are downloaded from the City of Vancouver Open Data portal.
2. Raw records are normalized and filtered into processed CSVs and aggregate outputs used by the app.
3. The rules engine evaluates the full stay across nearby meters and identifies conflicts with time limits and rush-hour restrictions.
4. The ranking layer orders the legal options by estimated price first, then distance.
5. The Streamlit UI presents the final recommendation, nearby conflicts, and city-level insights.

This separation keeps the parking rules and ranking logic reusable, even if the interface later moves to a richer frontend stack.

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

**Parking rules.** The by-laws, City pages, and Council records used to interpret parking rules are listed in [`docs/references.md`](docs/references.md).

Team conventions are in [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md); planning and design documents are in [`docs/`](docs/).

## Driver View meter data

`python -m curbcheck.meters` reads the meter snapshot in `data/raw/` and writes `data/meters_clean.csv` and `data/meters_preprocessing_report.json`.

**Source:** City of Vancouver open data, `parking-meters`, snapshot downloaded 2026-10-11 19:11 UTC (3,642 records). After preprocessing, 2,760 records citywide (636 Downtown) can be evaluated by the rules engine; the report lists every reason a record was excluded. Rule interpretations and their official sources are in [`docs/references.md`](docs/references.md), Section 5.

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

## Architecture and implementation notes

The project is intentionally structured so that the logic is separated from the visual layer:

- `app.py` contains the top-level Streamlit navigation and shared footer.
- `views/` contains the interface pages: Home, Driver View, City View, and About.
- `curbcheck/` contains the preprocessing, rules, and ranking logic used to compute candidate parking outcomes.
- `scripts/` contains the ticket-building pipeline for the city-side analysis.
- `data/` holds the processed data that the app reads at runtime.

This separation keeps the parking rules and ranking logic reusable, even if the interface later moves to a richer frontend stack.

## Documentation and contribution

- `docs/CONTRIBUTING.md` holds project team conventions.
- `docs/` contains planning, design, and process materials.
- `docs/references.md` contains the rule interpretations and official source references used by the driver engine.
- `docs/proposal_curbcheck_v3_en.md` carries the original product narrative and user problem framing.
- `docs/mvp_implementation_handoff_en.md` is the engineering source of truth for the implementation scope.

## Implementation status

This project is a working datathon prototype and demo. The current version is focused on validating the idea end-to-end:

- The driver experience works for a realistic Vancouver stay.
- The city-side ticket analysis is available and interpretable.
- The app is live and demonstrates the concept without requiring an API or external geocoding service.

The project is not presented as a legal or production-grade parking authority tool. It is a transparent, data-driven proof of concept for showing how rule complexity affects parking outcomes.

## Future road map

The current MVP already does well:

- The full driver flow works: choose a destination and stay, evaluate nearby meters, and explain the result.
- The map and result explanations make the recommendation auditable.
- The UI communicates the supported scope and keeps the posted-sign disclaimer visible.
- Parking rules and ranking already live outside the Streamlit page, which makes a future frontend replacement practical.

### Immediate improvements

- Add map filters for Recommended, Conflicts, and Unsupported meters.
- Cluster dense markers or hide most rejected meters by default.
- Replace long repeated rejection paragraphs with a compact summary.
- Make the no-result state actionable.
- Keep advanced coordinates and the full candidate table collapsed by default.
- Show the parking-data snapshot date near the results.
- Use icons and text in addition to colour so red/green is never the only status signal.

### Mobile and responsive design

Use a single task flow on narrow screens:

1. Choose destination.
2. Enter arrival and duration.
3. Review the best result.
4. Open the map or full explanation as needed.

Suggested behaviour:

- Use a Map / List segmented control.
- Use a map height based on the viewport, approximately 40–50vh.
- Show the best recommendation or no-result state in a bottom sheet.
- Keep key controls large enough for touch interaction.

### Possible future architecture

A formal React application is feasible, but should be a progressive migration rather than a rewrite of the parking logic.

```text
React / Next.js frontend
        |
        | JSON over HTTPS
        v
Python FastAPI backend
        |
        +-- existing curbcheck.rules
        +-- existing curbcheck.ranking
        +-- cleaned meter data and data-version metadata
```

Suggested responsibilities:

| Layer | Responsibility |
| --- | --- |
| React / Next.js | Responsive layout, form state, map interactions, result presentation, accessibility, and API requests |
| Python / FastAPI | Input validation, rule evaluation, cost calculation, ranking, structured reasons, and data-version reporting |
| Data pipeline | Download, validate, preprocess, and version the City of Vancouver datasets |

The frontend should not reproduce legal or parking calculations. Keeping those rules in Python prevents the Streamlit and React versions from producing different answers.

## License

This project includes data and map sources as noted above. The project code is presented under the repository licence in [LICENSE](LICENSE), while the Open Data content remains governed by the City of Vancouver licensing terms.

## References

- City of Vancouver Open Data portal
- Trilemma Foundation data catalog
- [docs/references.md](docs/references.md)
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- [docs/proposal_curbcheck_v3_en.md](docs/proposal_curbcheck_v3_en.md)
- [docs/mvp_implementation_handoff_en.md](docs/mvp_implementation_handoff_en.md)
- [docs/](docs/)

---

