# CurbCheck

Vancouver's street parking rules switch by time of day. CurbCheck helps drivers check whether a whole stay is legal and what it will cost, and shows the City where its rules trip people up.

Built for the Trilemma × Northeastern Datathon, Vancouver (2026).

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Posted signs take precedence over CurbCheck's results.

Team conventions are in `CONTRIBUTING.md`.

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
