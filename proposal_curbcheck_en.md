# CurbCheck — Datathon Proposal (English v0.2)

> Status: Draft v0.2 · Team of 3 · 3 build days · Demo Day: Tue 10/13
> Direction update: the core is now a time-window street parking guide; ticket data becomes a supporting reference. The earlier version (driver block cards) is kept in the git history.
> Event: Trilemma × Northeastern Datathon, Vancouver (rules TBC)

---

## 1. One-Sentence Value

Enter a destination, an arrival time, and how long you'll stay, and CurbCheck shows nearby street parking that is **legal for your whole stay**, **what it will cost in total**, and which tickets are most common on that block.

## 2. Problem

- Vancouver street parking rules **switch by time of day**: daytime and evening rates differ, time limits differ, rush-hour restrictions apply, and meters are free after 10 pm.
- Parking is a stretch of time, not a moment. **Mistakes happen when a stay crosses a time boundary**, like parking at 5 pm in a spot restricted from 3 to 6 pm.
- Existing tools each cover one piece: PayByPhone handles payment, SpotAngels and ParkMe show prices, but few tools check whether your whole stay is legal and what it will cost in total.

## 3. Who It's For

- **Drivers heading downtown** for errands or dinner who want the cheapest legal option, before leaving or as they arrive.
- **Delivery and service drivers** who park many times a day, where tickets eat directly into margins.
- **Visitors** who don't know how to read Vancouver's sign stacks.

**Not for**: finding an open spot right now. No public real-time occupancy data exists, so the app shows the top three options — if the first is full, try the next.

## 4. Worked Example: Downtown Meter `081034`

Rules: daytime (9am–6pm) $5.00/hr, 2-hour limit; evening (6pm–10pm) $3.50/hr, 4-hour limit; PM rush hours 3pm–6pm.

| Your plan | CurbCheck's answer |
| --- | --- |
| Arrive 1 pm, stay 3 hours | ❌ Daytime limit is 2 hours, and rush hours start at 3 pm |
| Arrive 5 pm, stay 3 hours | ❌ 5–6 pm falls in rush hours; you can't park here |
| Arrive 6 pm, stay 3 hours | ✅ Evening rate, $10.50 total, within the 4-hour limit |

(Rush hours typically mean no parking or tow-away; confirm the exact rule against posted signs.)

## 5. Competitors and Differentiation

| Product | What it does | What it doesn't |
| --- | --- | --- |
| PayByPhone | The main payment app for Vancouver street parking | Doesn't help you plan where to park |
| SpotAngels | Finds cheap and free parking | Price-focused |
| ParkMe (INRIX) | Shows expected prices on a map before you arrive | Focused on lots and garages |
| EasyPark app | Locations and payment for City-owned lots, sometimes live availability | Only its own lots |

**What makes CurbCheck different**:

- **Legality checked across your whole stay**: rush-hour restrictions and time limits, automatically.
- **Total cost across time windows**: daytime to evening, free after 10 pm, weekend limits.
- **Ticket reference**: the most common infraction types on that block, as a heads-up.

## 6. Data Sources

| Data | In Trilemma catalog? | Use | Role |
| --- | --- | --- | --- |
| Parking meters (`parking-meters`) | ❌ City open data | 3,642 meters **with coordinates**, day/evening rates, weekday/weekend limits, rush hours, prohibitions | **Core** |
| Property addresses (`vancouver-property-addresses`) | ✅ | Build a "100-block → coordinates" lookup | Supporting |
| Parking tickets (`vancouver-parking-tickets`) | ✅ | Ticket counts and common infraction types per block (January 2025 – June 2026 recommended) | Reference |
| OSM parking (`osm-overpass`) | ✅ | Locations of nearby paid lots (no prices) | Stretch |

How common are time-window switches? (Measured from the meter data)

| Situation | Meters |
| --- | --- |
| Daytime and evening rates differ | 2,390 (~66%) |
| Daytime and evening time limits differ | 3,356 (~92%) |
| PM rush-hour restriction | 745 |
| Other prohibitions | 271 |

## 7. Method

- **Rule parsing**: turn text like `$5.00`, `2 Hr`, and `3:00pm to 6:00pm` into computable values.
- **Legality check**: given an arrival time and duration, check for rush-hour or prohibition overlaps and whether each window's time limit is exceeded.
- **Cost calculation**: sum each window at its rate; 10 pm to 9 am is free.
- **Ranking**: keep options legal for the whole stay, then sort by total cost and walking distance; show the top three.
- **Ticket reference**: group addresses by "civic number rounded down to the hundred + street" and average their coordinates to get block locations, then join to the ticket block field — no external geocoding service needed.
- **Infraction categories**: group by bylaw section and keywords into meter expired, overstayed limit, rush-hour no stopping, loading zone, fire hydrant, residential permit zone, and so on.

## 8. MVP Features

- **Tap a destination on the map**, then enter arrival time and duration.
- **Top three recommendations**: legality, total cost, walking distance.
- **Block heads-up**: e.g., "60% of tickets near here are for expired meters."
- **Data page**: sources, update dates, limitations.

## 9. Out of Scope

- Real-time availability.
- Parkade prices (no open data).
- Fine vs. fee comparison, natural-language queries, trend and seasonal analysis (listed as next steps).
- A native app (we build a mobile-friendly web app instead).

## 10. Team Roles (3 People)

| Role | Responsibilities |
| --- | --- |
| A: Data & Rules | Meter data, rule parsing, legality and cost calculation, ranking |
| B: Ticket Reference | Block-coordinate lookup, ticket aggregation, infraction categories, limitations notes |
| C: UI & Deployment | Mobile map, input and results screens, deployment, slides |

## 11. Three-Day Schedule (Demo Day: Tue 10/13)

| | A: Data & Rules | B: Ticket Reference | C: UI & Deployment | Done when |
| --- | --- | --- | --- | --- |
| **Day 1** | Download meters; parse time-window rules; write the "arrival time + duration → legal? + total cost" function | Build the "100-block → coordinates" lookup; aggregate January 2025 – June 2026 tickets: count and top 3 infractions per block | Build the mobile map: tap a destination, show nearby meters | Legality and cost can be computed for any meter and time window |
| **Day 2** | Ranking: legal → cost → distance; handle free after 10 pm and weekend limits | Group infractions into categories; attach ticket reference to meter locations | Connect frontend and backend; results list shows top three; **deploy once today** | The live site works end to end |
| **Day 3** | Test edge cases (crossing windows, crossing 10 pm); write data notes | Write limitations notes; prepare demo locations | Fix bugs; finish slides; **feature freeze at noon**, rehearse in the afternoon | Ready for a live demo |

Ground rules:

- Spend 30 minutes before Day 1 locking the data format (columns and file names) so all three can work in parallel.
- **The ticket reference is a stretch item**: if it isn't connected by the end of Day 2, drop it and ship the street parking guide alone — the product is still complete.
- Each evening sync answers only three things: what I finished today, what I'll do tomorrow, and whether I'm blocked.
- If anyone is stuck for more than 2 hours, raise it in the group chat.

## 12. Demo Script (2 Minutes)

1. Open: "92% of Vancouver's meters have different daytime and evening time limits. Park here at 5 pm and you'll get towed."
2. Live: a judge taps a destination and picks a time; the app lists three legal, low-cost options.
3. Show the time-window math: the same spot is off-limits at 5 pm, but 3 hours from 6 pm costs just $10.50.
4. Close: next steps are a fine vs. fee analysis and route mode for delivery drivers.

## 13. Risks

- **No real-time availability**: we guarantee legality and cost, not an open spot; the top-three list softens this.
- **What rush hours actually mean**: confirm whether it's no stopping, tow-away, or something else, so the legality check is right.
- **Rule-text edge cases**: most formats are consistent, but a few special cases may need handling.
- **Data vs. posted signs**: the data was updated Oct 5, but posted signs always win — the UI says so.
- **Tickets currently end in June 2026 and exclude VPD-issued tickets**: reference only, with the date range shown.
- **Meter data is outside the Trilemma catalog**: confirm datathon rules.

## 14. Open Questions

1. Does the datathon allow non-catalog data (parking meters)?
2. What exactly do rush-hour restrictions mean on these meters?
3. Does a teammate already have data-exploration code we can reuse?
