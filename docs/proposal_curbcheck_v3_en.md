# CurbCheck — Datathon Proposal (English v0.3: One Problem, Two Views)

> Status: Draft v0.3 · Team of 3 · 3 build days · Demo Day: Tue 10/13
> This version combines three proposals: Anahid's revised proposal (block cards, data-cleaning details), a teammate's City-facing problem statement (pricing and enforcement analysis), and Yan-Bo's v0.2 (time-window cost and legality guide).
> Event: Trilemma × Northeastern Datathon, Vancouver (rules TBC)

---

## 1. One-Sentence Value

Vancouver's street parking rules switch by time of day, and drivers get them wrong. CurbCheck helps **drivers** see whether their whole stay is legal and what it will cost, and shows the **City** where its rules trip people up most.

## 2. Problem

- **Rules switch by time of day**: daytime and evening rates differ, time limits differ, rush-hour restrictions apply, and meters are free after 10 pm. In the meter data, about 92% of meters have different daytime and evening time limits.
- **Drivers slip up when a stay crosses a time boundary**, like parking at 5 pm in a spot restricted from 3 to 6 pm. Existing tools (PayByPhone for payment, SpotAngels and ParkMe for prices) rarely check whether a whole stay is legal.
- **The City lacks a combined view**: it publishes ticket and meter data, but no tool puts the rules next to where people actually get them wrong, which makes it hard to see where signs or rules need work.

## 3. Who It's For

| View | Users | Question they want answered |
| --- | --- | --- |
| **Driver** (demo lead) | Drivers heading downtown, delivery and service drivers, visitors | "I need 3 hours from 5 pm — where nearby is legal and cheap?" |
| **City** | Parking management, enforcement, transportation planners | "Which areas and infraction types are most concentrated? Are our rules easy to get wrong?" |

**Not for**: finding an open spot right now. No public real-time occupancy data exists.

## 4. Worked Example: Downtown Meter `081034`

Rules: daytime (9am–6pm) $5.00/hr, 2-hour limit; evening (6pm–10pm) $3.50/hr, 4-hour limit; PM rush hours 3pm–6pm.

| Your plan | CurbCheck's answer |
| --- | --- |
| Arrive 1 pm, stay 3 hours | ❌ Daytime limit is 2 hours, and rush hours start at 3 pm |
| Arrive 5 pm, stay 3 hours | ❌ 5–6 pm falls in rush hours; you can't park here |
| Arrive 6 pm, stay 3 hours | ✅ Evening rate, $10.50 total, within the 4-hour limit |

(Rush hours typically mean no parking or tow-away; confirm the exact rule against posted signs.)

## 5. Two Views, One Map

A "Driver / City" toggle at the top switches views on the same meter map.

**Driver view**
- Tap a destination on the map, then enter arrival time and duration.
- See the top three options within walking distance that are **legal for the whole stay**, sorted by total cost and walking distance.
- Get a block heads-up, e.g., "The most common ticket near here is an expired meter."

**City view**
- Map layers: rates by area, ticket concentration, and coloring by infraction type.
- Hour-of-day pattern of 311 parking enforcement requests (tickets have no time; requests do).
- Two or three key insights, e.g., "Blocks where one infraction type is unusually concentrated may have unclear signs or rules."

## 6. Competitors and Differentiation

| Product | What it does | How CurbCheck differs |
| --- | --- | --- |
| PayByPhone | Street parking payment | We help you plan before you go |
| SpotAngels, ParkMe | Find cheap parking, compare prices | We check legality across your **whole stay** and total the cost across time windows |
| EasyPark app | City-owned parking lots | We focus on street parking rules |

We have not found a direct public competitor for the City view.

## 7. Data Sources (Trilemma Catalog First)

| Data | In Trilemma catalog? | Use | View |
| --- | --- | --- | --- |
| Parking tickets (`vancouver-parking-tickets`) | ✅ | Infraction types, enforcement concentration, block heads-ups | Both |
| Property addresses (`vancouver-property-addresses`) | ✅ | Turn ticket "100-block + street" into coordinates | Both |
| 311 parking enforcement requests (`vancouver-311-service-requests`) | ✅ | Request times (with timestamps and coordinates) | City |
| Parking meters (City open data `parking-meters`) | ❌ Supplementary public data | Coordinates, rates, limits, and rush hours for 3,642 meters; also the base map | Both |

Known data limitations (combining Anahid's notes and our own checks):

- Tickets have **a date but no time of day**, and locations only to the 100-block.
- Ticket data currently runs to the end of June 2026 (the 2026 dataset `parking-tickets` is the one the Trilemma catalog links to; 2020–2025 is a separate history dataset) and **excludes VPD-issued tickets**.
- The 2020-onward ticket data **includes water tickets**, which must be filtered out.
- One meter row may be **one pay station covering several spaces**; we call these "meters (pay stations)."
- Meter data has **no street field**, so matching relies on coordinates.

## 8. Method

**Shared core: time-window rules engine**
- Turn text like `$5.00`, `2 Hr`, and `3:00pm to 6:00pm` into computable values.
- Given an arrival time and duration, check for rush-hour or prohibition overlaps and per-window time limits, and total the cost window by window (free from 10 pm to 9 am).

**Ticket processing** (following Anahid's plan)
- Keep issued tickets only (exclude voids and warnings by Status), de-duplicate by `(year, BI_ID)` because IDs are reused across years, and filter out water tickets.
- Use January 2025 – June 2026 data to reduce mismatch with current rules.
- Group by bylaw section and keywords: meter expired, overstayed limit, rush-hour no stopping, loading zone, fire hydrant, residential permit zone, and so on.

**Geocoding**
- Group the address data by "civic number rounded down to the hundred + street" and average the coordinates to get block locations, then join to tickets. No external geocoding service needed.

**Metric principles**
- Ticket counts show **where enforcement happened**, not parking demand or the probability of a ticket.
- **Meter rates** serve as the demand proxy: Vancouver adjusts rates based on occupancy.
- Fines vs. fees are shown only as a **gap**, never as "not paying is cheaper." Fine amounts come from Schedule A of By-law No. 10201, with a 40% discount for payment within 14 days (current amounts to be confirmed).

## 9. MVP and Stretch Features

**MVP**
- Shared map with a "Driver / City" toggle.
- Driver view: destination, time, duration → top three legal options with total cost.
- City view: ticket concentration and infraction-type layers, 311 hour-of-day chart, two or three insights.
- Data page: sources, update dates, limitations.

**Stretch (only if time allows)**
- Typed questions (Anahid's idea): a language model **only extracts** the location, weekday, and duration; all numbers and verdicts come from the data and rules.
- A chart of the gap between meter fees and fines.
- Voice input (last step).

## 10. Out of Scope

- Real-time availability and parkade prices (no open data).
- Forecasting models and language-model-written verdicts.
- A native app (we build a mobile-friendly Streamlit web app).

## 11. Team Roles (3 People)

| Member | Responsibilities |
| --- | --- |
| Yan-Bo | Time-window rules engine (shared core) + Driver view |
| Juwon | Streamlit scaffold and map + City view |
| Anahid | Ticket cleaning, infraction categories, block-coordinate lookup, feeding both views |

## 12. Three-Day Schedule (Demo Day: Tue 10/13)

| | Yan-Bo: rules engine + Driver view | Juwon: map + City view | Anahid: ticket data | Done when |
| --- | --- | --- | --- | --- |
| **Day 1** | Parse time-window rules; write the "arrival time + duration → legal? + cost" function | Streamlit scaffold and meter map; rate layer | Clean tickets (voids, duplicates, water tickets); build the block-coordinate lookup | The map renders; cost can be computed for any meter |
| **Day 2** | Driver view: tap a destination, list the top three options | City view: ticket concentration and infraction-type layers; 311 hour-of-day chart | Infraction categories; attach tickets to the map for both views | Both views work; **deploy once today** |
| **Day 3** | Test edge cases (crossing windows, crossing 10 pm) | Write up two or three City insights | Write data notes and limitations | **Feature freeze at noon**, rehearse in the afternoon |

**Stop-loss**: if the City view isn't working by the end of Day 2, shrink it to one analysis slide. The Driver view must ship. If the team gets smaller, cut the City view's interactive features first.

Ground rules:

- Spend about 30 minutes before Day 1 locking the shared data format (columns and file names).
- Each evening sync answers only three things: what I finished today, what I'll do tomorrow, and whether I'm blocked.
- If anyone is stuck for more than 2 hours, raise it in the group chat.

## 13. Demo Script (2 Minutes)

1. Open: "92% of Vancouver's meters have different daytime and evening time limits. Park here at 5 pm and you're already breaking the rules."
2. Driver view: a judge taps a destination and a time; the app lists three legal, low-cost options. The same spot costs just $10.50 for 3 hours from 6 pm.
3. Switch to City view: "With the same rules, the City sees these blocks where one infraction type stands out — a sign the signage may be unclear."
4. Close: one data engine — drivers know how to park, and the City knows what to fix.

## 14. Risks

- **Two views split the team's effort**: managed by the stop-loss; the Driver view comes first.
- **What rush hours actually mean**: confirm whether it's no stopping, tow-away, or something else.
- **Mapping tickets is error-prone**: use the address-grouping method and spot-check a sample by hand.
- **Tickets currently end in June 2026 and exclude VPD tickets**: show the date range and limitations.
- **Data vs. posted signs**: the UI reminds users that posted signs win.
- **Meter data is outside the Trilemma catalog**: used as supplementary public data; confirm datathon rules.
