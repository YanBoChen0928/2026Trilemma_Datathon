# CurbCheck MVP — Engineering Handoff and Implementation Specification

> Status: Draft for team confirmation  
> Project: Trilemma × Northeastern Datathon  
> Team size: 3  
> Build window: 3 days  
> Demo day: Tuesday, October 13, 2026  
> Related documents: `proposal_curbcheck_v3_en.md`, `blueprint_driver_en.md`, `blueprint_city_en.md`

## 1. Purpose of This Document

This is the engineering source of truth for the CurbCheck MVP. It translates the proposal and blueprints into an implementation sequence, data contracts, acceptance criteria, and explicit scope limits.

It is written for both human engineers and LLM coding agents.

When this document conflicts with a proposal or blueprint on implementation details, stop and ask the product owner which version is intended. Do not silently expand scope or invent parking rules.

Document rules:

- This handoff is the single engineering source of truth.
- Blueprints point to this document for CSV schemas and implementation rules.
- Proposals keep the product narrative only and do not carry detailed schemas.

## 2. Product Goal

CurbCheck has two views built on Vancouver parking data:

1. **Driver View — demo lead:** A driver selects a destination, arrival date and time, and duration. The app returns up to three nearby meter records that appear legal for the complete stay, estimates the cost, and explains why closer records were rejected.
2. **City View:** City staff compare meter-rate patterns with parking-ticket concentration and inspect the infraction breakdown for a selected block.

The MVP is a decision-support prototype. It does not replace posted signs, guarantee legal parking, show real-time availability, or estimate the probability of receiving a ticket.

## 3. Confirmation Register

### 3.1 Confirmed Product Decisions

- Driver View is the primary demo path.
- City View must-have: meter-rate layer, ticket-concentration layer, and block-level infraction breakdown.
- City View stretch: 311 hour-of-day chart and weekday filter.
- Ticket volume represents enforcement activity, not parking demand or the probability of receiving a ticket.
- Meter rates are used only as a proxy for demand and must be labelled as such.
- Natural-language questions and voice input are not part of the MVP.
- Real-time space availability and parkade prices are out of scope.
- The two views should be developed independently and integrated into one Streamlit app.
- Posted signs take precedence over the prototype's result.

### 3.2 Recommended MVP Defaults — Product Owner Should Confirm

These defaults keep the three-day build achievable. If the team does not change them before implementation, use the recommendation shown here and disclose it in the UI.

| Decision | Recommended MVP default | Reason |
| --- | --- | --- |
| Supported stay | Same calendar day, arrival and departure between 9:00 am and 10:00 pm | Avoid overnight and cross-day rule ambiguity while preserving the important 6:00 pm transition |
| Date input | Full date plus arrival time and duration | Required for Tuesday-only, weekday, and weekend restrictions |
| Vehicle support | Ordinary passenger vehicles; recommend only records whose rules apply to `Any Vehicle` | Avoid vehicle-specific eligibility logic in the MVP |
| Search radius | 250 m straight-line radius | No routing service is required; label the result as approximate distance, not walking-route distance |
| Flat-rate records | Exclude from recommendations until flat-rate semantics are verified | Prevent incorrect cost comparisons |
| Unknown or unparseable rules | Do not recommend the record; show an unsupported-data reason | Never guess a legal verdict |
| City ticket scope | Downtown Vancouver, 2025-01-01 to 2026-06-30 | 2025 from `parking-tickets-2020-2025`; 2026 from `parking-tickets` (the dataset the Trilemma catalog links to); limits geocoding work |
| Ticket visualization | Clickable proportional circles by 100-block | Works with point coordinates and supports block details without requiring block polygons |
| 311 chart | Stretch feature only | It is a separate resident-request signal and is not needed for the core City story |
| Navigation | Streamlit multipage navigation | Allows the Driver and City owners to work independently |

### 3.3 Rule Decisions for the MVP

| Question | MVP decision |
| --- | --- |
| Time limit when a stay crosses 6:00 pm | Do not assume a reset. Use the tri-state rule in Section 7.4. |
| Meaning of AM/PM rush-hour fields | Any overlap means not recommended (`legal=False`). The UI says: "Not recommended: overlaps posted rush-hour restriction." |
| Cost calculation | Proportional by minute within each time window; shown as **Estimated cost**. |
| Flat-rate records | Excluded from recommendations. |
| Null limits or rates | Never treated as free, unrestricted, or `No Time Limit`; the record is unsupported. |
| Override flags | `time_limit_override == "Yes"` or `prohibition_override == "Yes"` makes the record unsupported until official semantics are found. |
| Overnight stays | A departure after 10:00 pm is unsupported (Section 7.2, step 2). |
| Water-ticket filter | The ticket-processing owner decides the rule and records it in the README. |
| Downtown definition | The ticket-processing owner decides the definition and records it in the README. |

Remaining team confirmations:

1. Anahid / Juwon split.
2. Deployment platform, no later than the end of Day 1.

The UI describes results as **data-based guidance** and costs as **Estimated cost**, never as a legal guarantee or an exact payment amount.

## 4. MVP Scope

### 4.1 Must Have

#### Driver View

- Destination selected on a real map.
- Arrival date, arrival time, and duration inputs.
- Candidate meter records within a 250 m straight-line radius.
- Legality evaluation for supported records across daytime and evening windows.
- Rush-hour and prohibition-overlap checks.
- Estimated cost across supported time windows.
- Up to three legal recommendations, sorted by estimated cost and then approximate distance.
- Explanation when a closer record is rejected.
- Clear unsupported, no-result, and data-error states.

#### City View

- Daytime/evening meter-rate selector and rate layer.
- Ticket concentration by 100-block using proportional circles.
- Block-level infraction breakdown.
- Two or three precomputed, human-reviewed findings.
- Visible data scope, date range, source, and limitations.

#### Shared

- One deployable Streamlit app.
- Driver and City pages read preprocessed files rather than cleaning large datasets during page rendering.
- OpenStreetMap attribution is visible.
- The app can run from a clean environment using the committed dependency file and documented start command.

### 4.2 Stretch — Only After the Must-Have MVP Is Deployed

- 311 parking-enforcement requests by local hour and weekday.
- Driver block heads-up using the City ticket aggregate.
- Additional City filters such as weekday or infraction category.
- Support for flat-rate meter records after their semantics are verified.

### 4.3 Out of Scope

- Overnight or cross-day stays in the initial MVP.
- Real-time space availability.
- Route-based walking distance.
- Parkade availability or pricing.
- Fine-versus-fee expected-cost claims.
- Probability of receiving a ticket.
- Forecasting or causal claims.
- Natural-language-to-query functionality.
- Voice input.
- Native mobile applications.

## 5. Source Data

| Dataset | MVP role | Important limitations |
| --- | --- | --- |
| City of Vancouver parking meters | Driver rules, rate layer, map locations | Updated separately from posted signs; records may describe meters, pay stations, or block-face information rather than individual open spaces |
| Parking tickets 2025 (`parking-tickets-2020-2025`) | Ticket concentration and infraction categories, 2025 portion | Date but no time; location only at 100-block level; includes water tickets; excludes VPD-issued tickets |
| Parking tickets 2026 (`parking-tickets`, linked from the Trilemma catalog) | Ticket concentration and infraction categories, 2026-01-01 to 2026-06-30 | Same limitations; updated quarterly |
| Property addresses | Approximate coordinates for ticket blocks | Not a complete address set; duplicate addresses may exist; street normalization is required |
| 3-1-1 service requests | Stretch hour-of-day chart | Resident requests, not tickets or confirmed violations; timestamps must be converted to Vancouver local time |

Use a dated local snapshot for every external dataset used in the demo. Record the download or extraction date.

## 6. Driver Data Contract

### 6.1 Required `meters_clean.csv` Columns

| Column | Meaning |
| --- | --- |
| `meter_id` | Source meter identifier |
| `lat`, `lon` | WGS84 coordinates |
| `local_area` | City local area |
| `service_status` | `In Service`, `Out of Service`, or `Removed` |
| `vehicle_type` | Vehicle eligibility from the source |
| `time_limit_override` | Raw source flag (`Yes` / `No`) |
| `prohibition_override` | Raw source flag (`Yes` / `No`) |
| `rate_day` | Parsed 9:00 am–6:00 pm hourly rate |
| `rate_evening` | Parsed 6:00 pm–10:00 pm hourly rate |
| `flat_rate_raw` | Unmodified source flat-rate text |
| `limit_day_min` | Parsed weekday daytime limit in minutes; explicit sentinel for no limit |
| `limit_evening_min` | Parsed weekday evening limit in minutes; explicit sentinel for no limit |
| `limit_weekend_day_min` | Parsed weekend daytime limit in minutes |
| `limit_weekend_evening_min` | Parsed weekend evening limit in minutes |
| `am_rush_start`, `am_rush_end` | Parsed AM rush interval |
| `pm_rush_start`, `pm_rush_end` | Parsed PM rush interval |
| `prohibition_1_days` | Days when the first special restriction applies |
| `prohibition_1_time` | Time range for the first special restriction |
| `prohibition_1_zone` | First restriction type, such as loading, taxi, or no stopping |
| `prohibition_2_days` | Days when the second special restriction applies |
| `prohibition_2_time` | Time range for the second special restriction |
| `prohibition_2_zone` | Second restriction type |
| `supported` | Boolean: the MVP can safely evaluate this record |
| `unsupported_reason` | Human-readable reason when `supported == false` |

Do not collapse prohibition days, time, and zone into one unstructured field. They are needed separately for rule evaluation and explanations.

### 6.2 Driver Preprocessing Rules

1. Keep the original raw value while creating every parsed value.
2. Mark records not in service as unsupported.
3. For the initial MVP, mark vehicle-specific records as unsupported unless applicability to an ordinary passenger vehicle is explicitly handled.
4. Parse `$5.00` into `5.00`; do not convert a missing rate to zero.
5. Parse `30 Min`, `2 Hr`, `3 Hr`, `4 Hr`, and `13 Hr` into minutes.
6. Represent the literal `No Time Limit` separately from null or unparseable data.
7. Preserve and evaluate both prohibition groups.
8. Do not recommend a record with a flat-rate option until flat-rate semantics are confirmed.
9. Produce a preprocessing report containing total records, supported records, unsupported records by reason, and parse failures by field.
10. If `time_limit_override == "Yes"`: `supported = False`, `unsupported_reason = "Time-limit override semantics not verified."`
11. If `prohibition_override == "Yes"`: `supported = False`, `unsupported_reason = "Prohibition override semantics not verified."`
12. If a required weekday daytime or evening limit or rate is null, mark the record unsupported.
13. Mark any value that cannot be parsed as unsupported; never guess.

### 6.3 Current Evaluable Volume (Snapshot)

After the filters above (In Service, `Any Vehicle`, no flat rate, both overrides `No`, required limits and rates present):

| Scope | Records |
| --- | --- |
| Citywide | 2,761 |
| Downtown (`local_area == "Downtown"`) | 637 |

These figures come from the City open data API, queried 2026-10-10. They are a data snapshot, not constants. They are the records that can be passed to the rules engine; they do not mean every record will be recommended for a given stay. Do not present the raw `Any Vehicle` count (3,394) as the number of recommendable meters.

## 7. Driver Rules Engine

### 7.1 Interface

```python
evaluate_meter(
    meter: MeterRule,
    arrival_datetime: datetime,
    duration_minutes: int,
) -> EvaluationResult
```

```python
EvaluationResult(
    supported: bool,
    legal: bool | None,
    estimated_cost: float | None,
    reasons: list[str],
    warnings: list[str],
)
```

Use `legal=None` when the data cannot support a verdict. Do not return `legal=True` for unknown data.

### 7.2 Evaluation Order

1. Validate arrival date/time and positive duration.
2. If departure is after 10:00 pm (including any departure on a different calendar date):

   ```
   supported = False
   legal = None
   reason = "Overnight stays are not supported in the MVP. Meter parking is generally free after 10:00 pm, but posted restrictions and next-morning rules still apply."
   ```

   Do not calculate costs after 10:00 pm or next-day time limits in the MVP.
3. If arrival is before 9:00 am, return unsupported (outside the supported 9:00 am–10:00 pm window).
4. Reject unsupported or inactive records (Section 6.2).
5. Select weekday or weekend limits from the actual date.
6. Check overlap with AM and PM rush intervals. Any overlap sets `legal=False`. An AM rush interval such as 7:00–9:30 am still overlaps a stay that starts at 9:00 am.
7. Check both prohibition intervals against the date and the complete stay.
8. Split the stay at the 6:00 pm boundary.
9. Apply the tri-state time-limit rule (Section 7.4).
10. Estimate cost: for each window, minutes ÷ 60 × that window's hourly rate, then sum. Label it **Estimated cost**.
11. Return structured reasons and warnings.

### 7.3 Ranking

1. Remove unsupported and illegal records from recommendations.
2. Sort legal records by estimated cost ascending.
3. Break ties by straight-line distance ascending.
4. Return at most three records.
5. Separately evaluate the geographically closest record so the UI can explain why it was rejected, if applicable.

The UI must label distance as approximate. It must not call straight-line distance a walking-route distance.

### 7.4 Crossing 6:00 pm — Tri-State Rule

The Parking Meter By-law prohibits leaving a vehicle continuously in a metered space beyond the indicated time limit, but it does not say whether the limit resets at 6:00 pm. Do not assume a reset.

- **Interpretation A (reset at 6:00 pm):** minutes in the daytime window ≤ daytime limit, and minutes in the evening window ≤ evening limit.
- **Interpretation B (continuous):** total minutes ≤ the strictest limit among the windows the stay touches.

| A | B | Result |
| --- | --- | --- |
| Legal | Legal | `legal=True`; may be recommended |
| Legal | Not legal | `legal=None`; not recommended; reason: "This stay crosses 6:00 pm and depends on an unverified time-limit reset rule." |
| Not legal | Not legal | `legal=False` |

A stay within a single window is evaluated normally, since A and B give the same answer. The demo uses a 6:00 pm arrival to avoid this case.

## 8. Driver UI Requirements

- Map click sets the destination.
- Inputs: date, arrival time, and duration.
- Show the currently supported scope beside the inputs.
- Include stable default demo values or a `Load demo example` action.
- Recommendation cards show meter ID, estimated cost, approximate distance, applicable rates, and important warnings.
- If no supported legal option is found, explain whether the cause was no nearby records, legal conflicts, or unsupported data.
- Always display: `Posted signs take precedence.`

## 9. City Data Contract

### 9.1 Required `tickets_block_agg.csv` Columns

| Column | Meaning |
| --- | --- |
| `block_key` | Normalized `100-block + street` identifier |
| `block` | Source 100-block number |
| `street_normalized` | Normalized street name |
| `lat`, `lon` | Approximate block coordinate |
| `local_area` | Local area inherited from matched address data |
| `year` | Ticket year |
| `weekday` | Weekday derived from `entrydate` |
| `category` | Human-reviewed infraction category |
| `count` | Number of included tickets |

### 9.2 Ticket Processing Steps

1. Keep records with `status == "IS"` unless the team confirms another issued-ticket definition.
2. De-duplicate by `bi_id` and report how many duplicates were removed.
3. Combine 2025 records from `parking-tickets-2020-2025` with 2026 records from `parking-tickets`, filter to 2025-01-01 – 2026-06-30, and apply the same cleaning, categorization, and geocoding to both.
4. Remove water tickets using the owner's rule, recorded in the README.
5. Normalize ticket street names and property-address street names with the same function.
6. Convert civic numbers to 100-block keys.
7. Aggregate property-address coordinates by normalized block key and retain `geo_local_area`.
8. Join tickets to block coordinates.
9. Report the matched and unmatched ticket counts and match rate.
10. Apply the owner's Downtown definition, recorded in the README, after the join.
11. Categorize infractions using explicit bylaw/section mappings first and reviewed keyword rules second.
12. Aggregate and write `tickets_block_agg.csv`.
13. Manually inspect the ten highest-volume mapped blocks before the demo.

Do not hide unmatched records. They may be excluded from the map, but their count must appear in the data-quality notes.

## 10. City UI Requirements

### 10.1 Core Layers

1. **Meter rate:** selectable daytime or evening rates from `meters_clean.csv`.
2. **Ticket concentration:** proportional circles at approximate 100-block coordinates.

Do not describe point markers as colored block polygons. Block polygons are not part of the MVP data contract.

### 10.2 Selected Block Details

When the user selects a ticket marker, show:

- normalized block name;
- total included ticket count;
- most common infraction category;
- category breakdown;
- selected data period.

If reliable map-click state is not ready, a block selector beside the map is an acceptable fallback.

### 10.3 Insights

Use two or three findings computed before the demo and reviewed by a team member. Do not generate claims dynamically with an LLM.

Acceptable wording:

> This block has a high concentration of expired-meter tickets and may be a candidate for operational review.

Avoid causal wording such as:

> This proves the signs are unclear.

### 10.4 Required Caveats

- Ticket volume shows enforcement activity, not parking demand.
- Meter rate is a demand proxy, not direct real-time occupancy.
- Ticket locations are approximate at the 100-block level.
- The dataset excludes VPD-issued tickets.
- The displayed date range must be visible.

## 11. Optional 311 Stretch Feature

Implement only after the deployed must-have MVP works.

If implemented:

1. Filter exactly to `Parking Enforcement Request Case`.
2. Convert `service_request_open_timestamp` to `America/Vancouver` before extracting hour or weekday.
3. Apply and display the selected date and geographic scope.
4. Title the chart `Parking-enforcement requests by hour`.
5. State that requests are resident reports, not tickets or confirmed violations.
6. Do not join request hours to ticket records or present them as ticket-issuance times.

## 12. Minimum Test Cases

The Driver rules engine must pass these deterministic tests first:

1. Stay entirely within the daytime window.
2. Stay entirely within the evening window.
3. Stay crossing 6:00 pm — one parameterized test with a synthetic meter (daytime limit 2 h, evening limit 4 h, no rush-hour or prohibition):

   | Arrival / duration | A | B | Expected |
   | --- | --- | --- | --- |
   | 5:30 pm / 1.5 h | Legal | Legal | `True` |
   | 5:30 pm / 3 h | Legal | Not legal | `None` |
   | 3:00 pm / 5 h | Not legal | Not legal | `False` |

4. Rush-hour overlap, including a 9:00 am arrival that overlaps a 7:00–9:30 am AM rush.
5. Weekday and weekend limits that differ.
6. A specific-weekday prohibition (e.g., Tuesdays).
7. Null limit → unsupported.
8. Out-of-service record → unsupported.

Add after the core works: second prohibition overlap, literal `No Time Limit`, flat-rate record, departure after 10:00 pm, and cross-day departure.

The City pipeline must verify:

1. `bi_id` is unique after de-duplication.
2. Water-ticket filtering removes only the intended records.
3. The coordinate join reports matched and unmatched counts.
4. Aggregated counts reconcile with included source records.
5. The top ten mapped blocks pass manual plausibility checks.

## 13. Build Order and Ownership

### Step 0 — Confirm Scope and Contracts

- Review Section 3 as a team.
- Confirm the two remaining team decisions in Section 3.3.
- Freeze CSV columns and filenames.
- Freeze the demo destination, date, time, and duration.

**Done when:** all three team members are implementing the same rules and schemas.

### Step 1 — Deployable App Shell

Suggested owner: Juwon.

- Create the Streamlit entry point and Driver/City pages.
- Add dependency and run instructions.
- Render an empty map and deploy once.

**Done when:** the team has a working URL from a clean build.

### Step 2 — Meter Preprocessing

Suggested owner: Yan-Bo.

- Produce `meters_clean.csv` and a preprocessing report.
- Implement supported/unsupported classification.

**Done when:** every source record is either safely parsed or has an explicit unsupported reason.

### Step 3 — Rules Engine and Tests

Suggested owner: Yan-Bo.

- Implement the pure evaluation function.
- Pass the minimum deterministic test cases.

**Done when:** evaluation works without the Streamlit UI.

### Step 4 — Driver Page

Suggested owner: Yan-Bo, integrated with Juwon's app shell.

- Add destination and stay inputs.
- Evaluate, rank, and display results.
- Add failure states and the fixed demo example.

**Done when:** the primary demo path works on the deployed app.

### Step 5 — Ticket Processing

Suggested owner: Anahid.

- Clean, normalize, geocode, categorize, aggregate, and report data quality.

**Done when:** `tickets_block_agg.csv` is reproducible and its counts reconcile.

### Step 6 — City Page

Suggested owner: Juwon, using Anahid's aggregate and Yan-Bo's meter file.

- Add rate and ticket layers.
- Add block details, insights, and caveats.

**Done when:** the City story works without the 311 stretch feature.

### Step 7 — Integration and Freeze

- Test from a clean environment.
- Verify both pages, data paths, attribution, caveats, and demo defaults.
- Freeze features at noon on Day 3.
- Use the remaining time for bug fixes and rehearsal.

## 14. Definition of Done

The MVP is complete when:

- the deployed app opens reliably;
- the fixed Driver demo returns reproducible results;
- unsupported parking rules never produce a positive legal verdict;
- the City map shows rate and ticket concentration without describing tickets as demand;
- ticket geocoding quality and unmatched counts are disclosed;
- all sources, snapshot dates, and limitations are visible;
- the team can complete the two-minute demo without using a stretch feature.

## 15. Instructions for an LLM Coding Agent

- Implement only the must-have scope until it is deployed and tested.
- Do not infer parking-law semantics beyond the decisions in Section 3.3.
- Do not treat missing data as zero, free, no restriction, or no time limit.
- Do not silently discard unmatched or unparseable records; count and report them.
- Keep preprocessing separate from Streamlit page rendering.
- Prefer small pure functions and deterministic tests for rule evaluation.
- Preserve raw source columns when generating parsed columns.
- Do not add frameworks, databases, routing services, LLM APIs, or background services unless the product owner explicitly approves them.
- If a requested feature conflicts with the MVP scope, report the conflict before changing the implementation.
