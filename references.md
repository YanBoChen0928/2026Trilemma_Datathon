# CurbCheck References

Last verified: 2026-10-11  
Primary jurisdiction: City of Vancouver, British Columbia

This file records the external sources used for CurbCheck's data, parking-rule interpretations, UI caveats, and demo claims. The current City by-laws and posted street signs take precedence over this prototype.

## 1. Driver View — Data Source

### City of Vancouver Open Data — Parking Meters

- Dataset page: https://opendata.vancouver.ca/explore/dataset/parking-meters/
- Dataset ID: `parking-meters`
- CSV export used: https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/parking-meters/exports/csv?delimiter=%2C
- Count verification: https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/parking-meters/records?limit=0
- Metadata: https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/parking-meters
- Local snapshot: `data/raw/parking-meters_2026-10-11.csv`
- Downloaded: `2026-10-11T19:11:12Z` (`2026-10-11 12:11:12 PDT`)
- Snapshot records: 3,642

Used for meter locations, daytime and evening rates, weekday and weekend time limits, rush-hour intervals, prohibition intervals, vehicle eligibility, service status, and override flags.

Important limitation: the open-data record does not replace the current information displayed on the meter or posted street signs.

### Data freshness and future weekly refresh — Q2 follow-up

The City states that the parking-meter extract is updated weekly, but changes in the street may not appear immediately in the dataset. The demo therefore uses the dated snapshot above for reproducibility and describes a clear result only as a restriction found, or not found, in that snapshot.

After the MVP, a weekly refresh workflow may:

1. download a new full CSV export, API `total_count`, and metadata snapshot;
2. verify that the CSV row count matches `total_count`;
3. compare the new schema with the expected raw fields and stop if required fields were added, removed, or renamed;
4. run the existing deterministic preprocessing code and parser tests;
5. compare supported counts, unsupported reasons, parse failures, and duplicate identifiers with the previous snapshot; and
6. produce a candidate `meters_clean.csv` and preprocessing report for human review before replacing the deployed files.

An AI or Codex skill may orchestrate these steps and summarize differences. It must not silently change parking-rule interpretations, rewrite the preprocessing rules, or replace committed/deployed data when schema checks, tests, or count comparisons fail. Weekly refreshes normally replace the input snapshot and regenerate outputs; code changes require a separately reviewed handoff decision.

## 2. Current Parking Guidance

### City of Vancouver — How to Pay for Parking

- URL: https://vancouver.ca/streets-transportation/pay-for-parking.aspx
- Relevant guidance:
  - Pay parking is generally in effect from 9:00 am to 10:00 pm, seven days a week, unless otherwise specified.
  - Daytime and evening rates may differ.
  - Drivers must check for restrictions such as rush hours, special events, and construction.
  - The City's payment apps provide a `Park until` feature and allow drivers to pay ahead for the next morning.

Used for the Driver View's payment-window explanation and overnight-parking context.

## 3. Current By-laws

### Parking Meter By-law No. 2952

- URL: https://bylaws.vancouver.ca/2952c.pdf
- Relevant provisions:
  - Section 5(3): drivers must comply with the indicated meter time limit and rate.
  - Section 6(3): metered spaces may generally be used without charge from 10:00 pm to 9:00 am, subject to other parking time limits and prohibitions in the Street and Traffic By-law. Electric Vehicle Charging Stations are an exception where applicable rates may continue.
  - Section 7: temporary signs may discontinue a metered space and prohibit parking or stopping.

Used to support the overnight zero-meter-fee rule and the requirement to continue checking other restrictions.

### Street and Traffic By-law No. 2849

- URL: https://bylaws.vancouver.ca/2849c.pdf
- Relevant provisions:
  - Section 17.6: drivers must follow posted parking prohibitions, restrictions, and time limits. It also contains the general three-hour rule between 8:00 am and 6:00 pm and its exceptions.
  - Sections 21.1–21.5: passenger, loading, commercial-loading, and related zones have separate stopping and eligibility rules.

Used to explain why a space can remain restricted even when the parking meter does not charge a fee.

## 4. Park Until — Historical Council Record

### Vancouver City Council Minutes — January 29, 2019

- URL: https://council.vancouver.ca/20190129/documents/regu20190129min.pdf
- Relevant discussion: printed page 34, numbered items 8–10.
- The minutes state that Vancouver introduced the PayByPhone `Park Until` feature in 2018 so drivers could leave a vehicle overnight and pay ahead for the next morning.
- They also explain that the next-morning maximum stay is based on the meter's time limit after paid parking begins. Their example says that a three-hour meter could be used until noon the next day.
- The discussion explicitly mentions nightlife users and people finishing late night shifts.

This is a historical Council record that explains the feature; it is not a substitute for the current by-laws or posted signs.

## 5. Rule Interpretations

This section records where each parking rule used by CurbCheck comes from, what the official sources leave unstated, and the rule the MVP adopts. The rules themselves are specified in `mvp_implementation_handoff_en.md`, which remains the engineering source of truth; this section explains their basis and points to the relevant handoff section.

Status labels:

- **Official rule** — stated directly in a current by-law or City page.
- **Interpretation supported by official materials** — not stated in one sentence, but several official sources point to the same reading.
- **MVP assumption** — the sources are silent; the MVP chooses a conservative rule and discloses it.
- **Team decision** — an MVP assumption or scope choice that the team has confirmed.
- **Pending** — proposed, not yet confirmed by the team.
- **Open question** — raised during development; sources reviewed, but no team decision yet.
- **Superseded** — replaced by a later item; kept for history.

New questions are added to this section as they arise. Where an official source supports a specific statement, a footnote marker (for example, `[^stb-17-6f]`) is attached to the exact words it supports, and the footnote gives the document, section, and link.

### 5.1 Meter operating hours and overnight fees

- **Status:** Official rule
- **Sources:** Parking Meter By-law No. 2952 §6(3) (consolidated to December 9, 2025, including By-law No. 14528 effective April 1, 2026); City page "Time-limited and metered parking" (https://vancouver.ca/streets-transportation/time-limited-metered-parking.aspx), checked 2026-10-11.
- **What the sources say:** Meters operate from 9:00 am to 10:00 pm every day, including statutory holidays. From 10:00 pm to 9:00 am, metered spaces may be used without charge, subject to the time limits and prohibitions of the Street and Traffic By-law. Electric Vehicle Charging Stations may still charge overnight.
- **What they do not say:** Which Street and Traffic By-law restrictions apply to a given block overnight; these are not fully represented in the meter dataset (see 5.6).
- **MVP rule:** Meter fees are estimated only for 9:00 am–10:00 pm; the 10:00 pm–9:00 am segment costs $0. Electric-vehicle records are already unsupported (`vehicle_type != "Any Vehicle"`).
- **Implemented in:** handoff §7.2; timeline engine (5.11).

### 5.2 Meter time limit across 10:00 pm

- **Status:** Interpretation supported by official materials
- **Sources:** Parking Meter By-law §5(3)(a) and §6(3); City driving and parking guide (https://vancouver.ca/streets-transportation/driving.aspx); City parking payment guide (Section 2 above); 2019 Council minutes (Section 4 above), page 34, Motion B4 "Expanding Parking Options at EasyPark Lots and Parkades", whereas-clauses 8–10 (carried unanimously); City FOI release 2019-093, part 4 (https://vancouver.ca/files/cov/2019-093-release4.pdf), Parking Enforcement Officer training material, page 778 of 883.
- **What the sources say:** §5(3)(a) prohibits leaving a vehicle in a metered space continuously beyond the indicated time limit. §6(3) makes the overnight period subject to Street and Traffic By-law limits rather than to the meter's own limit. The City allows overnight parking at metered spots with no other restrictions and offers Park Until for the next morning. The 2019 minutes describe the next-morning time limit as counted from when paid parking resumes, and the FOI material describes overparking as exceeding the time limit while the meter is in effect.
- **What they do not say:** No by-law sentence states directly that the meter time limit stops counting at 10:00 pm.
- **MVP rule:** Meter time limits apply only within the meter's operating windows. The 10:00 pm–9:00 am segment does not consume the meter time limit. Example: with a 4-hour evening limit, a 7:00 pm–1:00 am stay uses 3 hours of the evening limit (7:00–10:00 pm) and is within the limit. Prohibitions, rush hours, and other known restrictions are still checked for the whole stay.
- **Implemented in:** Timeline engine (5.11); handoff update pending.
- **Verification (2026-10-11):** Both documents were read in the original. The Council minutes record the Park Until example in the preamble of a councillor's motion, not in a by-law. The FOI document is internal training material from about 2017–2018 and contains some outdated details (for example, page 763 says meters operate until 8:00 pm), so it is supporting context only. The controlling text remains Parking Meter By-law §5(3)(a) and §6(3).

### 5.3 Meter time limit across 6:00 pm

- **Status:** MVP assumption
- **Sources:** Parking Meter By-law §5(3)(a).
- **What the sources say:** A vehicle must not remain continuously beyond the indicated time limit.
- **What they do not say:** Whether the limit resets at 6:00 pm, when the daytime window ends and the evening window begins. Unlike 5.2, both windows are paid operating windows, so the reasoning in 5.2 does not apply.
- **MVP rule:** Tri-state rule. If the "reset at 6:00 pm" and "continuous" readings disagree, `legal=None` and the record is not recommended.
- **Implemented in:** handoff §7.4; test case 3 in handoff §12.

### 5.4 Days on which rush-hour restrictions apply

- **Status:** Team decision (adopted 2026-10-11; see `meter_data_decisions_en.md`, item 2)
- **Sources:** Open data fields `am_rush_hours` and `pm_rush_hours`; 2023 Council report on Street and Traffic By-law amendments (https://council.vancouver.ca/20231115/documents/cfsc2.pdf), which defines a Priority Congestion Management Roadway as a street where stopping is prohibited at specified times between 7:00 am and 7:00 pm.
- **What the sources say:** Rush-hour restrictions prohibit stopping during peak hours. The dataset records only a time range (e.g., `7:00am to 10:00am`).
- **What they do not say:** Which days of the week the restriction applies.
- **MVP rule:** Apply rush-hour restrictions every day. This can only make results more conservative. The UI notes that days are not specified in the data.
- **Implemented in:** handoff §7.2 step 6 (to be updated).

### 5.5 Prohibition time formats and cross-midnight intervals

- **Status:** Team decision (2026-10-11); start-day attribution resolved as an implementation note
- **Sources:** Open data fields `prohibition_1_*` and `prohibition_2_*` (2026-10-11 snapshot).
- **What the sources say:** Times include regular ranges, `Noon`, `Midnight`, `Anytime`, and ranges that cross midnight (e.g., `6:00pm to 2:00am`, `3:00pm to 9:30am`). Days include ranges such as `Mon-Fri` and single days such as `Tuesdays`.
- **Related official guidance:** City enforcement material (FOI release 2019-093, part 4, pages 763 and 782) states that signs without specific times are in effect 24 hours a day, which supports parsing `Anytime` as all day.
- **What they do not say:** For a day-specific prohibition that crosses midnight (e.g., `Tuesdays`, `6:00pm to 2:00am`), whether the early-morning part belongs to the listed day or the following day.
- **MVP rule:** Preprocessing keeps the full 24-hour interval and flags intervals that cross midnight; the rules engine checks them against the stay's actual timeline (5.11). A cross-midnight interval is attributed to the day on which it starts (Tuesday 6:00 pm to Wednesday 2:00 am).
- **Implemented in:** handoff §6.2 (to be updated).

### 5.6 Overnight restrictions outside the meter dataset

- **Status:** Official rule, partially represented in the data
- **Sources:** Parking Meter By-law §6(3); Street and Traffic By-law No. 2849 §17.6 (Section 3 above); 2023 Council report (5.4); parking-meters dataset description.
- **What the sources say:** Overnight parking remains subject to Street and Traffic By-law time limits and prohibitions. §17.6(f) contains a general three-hour rule between 8:00 am and 6:00 pm for streets abutting residential or commercial premises, with exceptions (as quoted in FOI release 2019-093, part 4, page 757). The dataset is updated weekly, and changes on the street may take time to reach the database.
- **What they do not say:** Which of these restrictions apply to each metered block, and whether the three-hour rule applies within metered spaces (see 5.9).
- **MVP rule:** The UI says only that no known restriction was found in the meter dataset, never that parking is legal. The three-hour rule is handled by the runtime guard in 5.9, which applies to every stay, including overnight and cross-day stays (5.11, Question 2).
- **Implemented in:** UI copy (Section 8); required caveats (Section 9).

### 5.7 Overnight Lite scope

- **Status:** Superseded by 5.11 (2026-10-11). The night-window design below is kept for history; the single timeline engine in 5.11 replaces it.
- **Sources:** 5.1, 5.2, and 5.6.
- **Rule summary:**
  - Night window: 6:00 pm to 9:00 am the following day.
  - Evening arrival: 6:00 pm–11:59 pm, departing by 9:00 am the next day.
  - Early-morning arrival: 12:00 am–8:59 am, departing by 9:00 am the same day.
  - The stay must fall entirely within one night window; at most one midnight is crossed.
  - 6:00–10:00 pm: evening rate and evening time limit. 10:00 pm–9:00 am: $0 and no meter time limit (5.2).
  - Prohibitions (including cross-midnight intervals and `Anytime`) and rush hours are checked for the whole stay.
  - Departure after 9:00 am: unsupported.
- **Open dependencies:** Early-morning arrivals conflict with handoff §7.2 step 3 (arrivals before 9:00 am are unsupported), which must be revised. Morning rush-hour checks depend on 5.4.
- **Implemented in:** To be added to handoff §4.2 (stretch).

### 5.8 Missing, incomplete, or unverified data

- **Status:** MVP assumption
- **Sources:** parking-meters dataset (2026-10-11 snapshot) and its metadata.
- **What the sources say:** The dataset distinguishes `No Time Limit` from blank fields, and includes flat-rate options and override flags.
- **What they do not say:** What a blank time limit means, how flat-rate options interact with hourly rates, and what the override flags change.
- **MVP rule:** `No Time Limit` is stored as `-1`; blank values are missing data, never zero or no limit. Records with missing required limits or rates, partially filled restriction groups, unparseable values, flat-rate options, override flags, or invalid coordinates are unsupported.
- **Implemented in:** handoff §6.1 and §6.2.

### 5.9 Three-hour rule within metered spaces during the day

- **Status:** Team decision (adopted 2026-10-11)
- **Question:** Can CurbCheck recommend a daytime stay longer than 3 hours at a meter whose posted daytime limit is longer than 3 hours (`4 Hr` or `No Time Limit`)?
- **What the sources say:**
  - The Street and Traffic By-law prohibits parking on a street abutting residential or commercial premises for more than 3 hours between 8:00 am and 6:00 pm[^stb-17-6f]. Downtown streets almost always abut such premises.
  - None of the listed exceptions refers to metered spaces; they cover same-block residents, employees of the premises, resident-only streets, and a few vehicle classes[^stb-17-6f].
  - Where an area is subject to two or more parking limitations, the more restrictive one applies[^stb-24-1].
  - A paid metered space may be occupied for the time paid, subject to the Street and Traffic By-law as well as the Parking Meter By-law[^pmb-5-2], and a vehicle must not stay beyond the meter's indicated time limit[^pmb-5-3a].
  - The Parking Meter By-law itself contemplates daytime meter limits of 9 hours[^pmb-5-6], and the raw meter dataset includes `13 Hr` limits (13 records, none of which pass preprocessing)[^data-limits].
  - City enforcement training material describes the three-hour rule as a measure against non-resident parking pressure and does not mention metered spaces[^foi-3hr].
- **What they do not say:** Whether a meter's posted time limit replaces the three-hour rule for that space, or whether both apply and the shorter one governs. Read together, the by-law text points toward "both apply" (the more restrictive rule governs), while the existence of 4-hour and 9-hour meter limits points toward "the meter limit governs".
- **Impact:** 35 supported records citywide, 23 of them Downtown, have a daytime limit longer than 3 hours (22 `4 Hr`, 13 `No Time Limit`)[^data-limits]. For same-day stays starting at 9:00 am or later, meters with daytime limits of 3 hours or less are unaffected, because the meter limit is already at least as strict. Overnight and cross-day stays can trigger the guard at any meter (5.11, Question 2). The demo (6:00 pm arrival) is unaffected, because the rule ends at 6:00 pm.
- **Options:**
  - **A.** The meter's posted limit governs within metered spaces; recommend stays up to that limit.
  - **B.** Both apply. If more than 3 hours of the stay fall between 8:00 am and 6:00 pm at a meter with a longer daytime limit, return `legal=None` with the reason "This stay may exceed the City's general three-hour rule for daytime parking." CurbCheck cannot know whether the driver qualifies for an exception, such as living on the block.
- **MVP decision:** Adopt Option B as a narrow runtime guard. Calculate how many minutes of the requested stay overlap the 8:00 am–6:00 pm window. Apply all definite checks first; if any returns `legal=False` (for example, the meter limit is exceeded), the result is `False`. Otherwise, if the overlap on any calendar day is **more than 180 minutes**, return `legal=None` regardless of the meter's daytime limit, do not recommend the meter, and use the reason: "This stay may exceed Vancouver's general three-hour daytime parking rule. Exceptions may apply." Exactly 180 minutes does not trigger the guard. Shorter stays continue through the normal rule engine. (Updated 2026-10-11: the guard originally applied only to meters with limits longer than 3 hours; it was generalized because the general rule starts at 8:00 am while the meter's next-day period starts at 9:00 am — see 5.11, Question 2.)
- **Preprocessing effect:** None. Do not mark the 35 records as unsupported and do not change the preprocessing checkpoints. Those meters remain usable for requests of 3 hours or less; the guard applies to each requested stay at runtime.
- **UI wording:** "Not recommended: This stay may exceed Vancouver's general three-hour daytime parking rule. Exceptions may apply; check posted signs." Do not describe the stay as definitely illegal because CurbCheck cannot determine whether the driver qualifies for an exception.
- **Minimum tests:**
  1. `4 Hr`, 9:00 am–1:00 pm: return `legal=None` and do not recommend.
  2. `No Time Limit`, 9:00 am–11:00 am: do not trigger the three-hour guard.
  3. `4 Hr`, 9:00 am–12:00 pm: do not trigger the guard because the overlap is exactly 180 minutes.
- **Implementation notes (no team decision needed):**
  1. The "applicable daytime limit" is the one for the stay's actual day: `limit_day_min` on weekdays, `limit_weekend_day_min` on weekends.
  2. If the supported window is later widened (5.11), the overlap is calculated per calendar day. For overnight or cross-day stays, 5.11 Question 2 generalizes the guard to meters with any daytime limit because the general rule begins at 8:00 am while the next meter period begins at 9:00 am.
  3. Results combine conservatively across all checks: any `False` gives `False`; otherwise any `None` gives `None`; otherwise `True`. All reasons are kept.
  4. Extra tests to add with the rules engine: `No Time Limit`, 9:00 am–1:00 pm → `None`; `3 Hr`, 9:00 am–1:00 pm → `False` (meter limit); `4 Hr` daytime and evening, 2:30 pm–6:30 pm → `None` (guard only).
- **Implemented in:** Decision recorded here; the handoff, rule engine, and tests still need to adopt it.

[^stb-17-6f]: Street and Traffic By-law No. 2849 (consolidated to May 19, 2026), §17.6(f), including exceptions (i)–(vi). https://bylaws.vancouver.ca/2849c.pdf
[^stb-24-1]: Street and Traffic By-law No. 2849, §24.1 ("the more restrictive regulation shall apply"). https://bylaws.vancouver.ca/2849c.pdf
[^pmb-5-2]: Parking Meter By-law No. 2952 (consolidated to December 9, 2025), §5(2), which makes occupancy of a paid metered space subject to "all other restrictions" of that by-law and of the Street and Traffic By-law. https://bylaws.vancouver.ca/2952c.pdf
[^pmb-5-3a]: Parking Meter By-law No. 2952, §5(3)(a). https://bylaws.vancouver.ca/2952c.pdf
[^pmb-5-6]: Parking Meter By-law No. 2952, §5(6) (daily rate where the daytime limit is 9 hours). https://bylaws.vancouver.ca/2952c.pdf
[^foi-3hr]: City of Vancouver FOI release 2019-093, part 4, Parking Enforcement Officer training material, pages 757 and 773. https://vancouver.ca/files/cov/2019-093-release4.pdf
[^data-limits]: City of Vancouver Open Data, `parking-meters`, snapshot `data/raw/parking-meters_2026-10-11.csv` (Section 1), field `time_limit_9am_6pm` among records that pass handoff §6.2; the weekend daytime field gives the same counts. https://opendata.vancouver.ca/explore/dataset/parking-meters/

### 5.10 Overnight Lite: mode selection and weekday attribution

- **Status:** Superseded by 5.11 (2026-10-11). With a single timeline engine there are no modes, so Questions 1 and 3 no longer arise (the 5:00 pm–11:00 pm stay in Question 1 is supported). The day-attribution rule in Question 2 still applies: each part of a stay is checked on its actual calendar day.
- **Background:** The team proposes two modes: daytime mode (same-day stay between 9:00 am and 10:00 pm) and Overnight Lite (a night window from 6:00 pm to 9:00 am the following day, crossing at most one midnight). An arrival after midnight is treated as part of the night window that started the previous evening.
- **Question 1 — Stays that start before 6:00 pm and end after 10:00 pm.** Example: Friday 5:00 pm to 11:00 pm. The stay fits neither mode: it is not within 9:00 am–10:00 pm, and it does not start inside the night window. As proposed, it is unsupported, although it is a common dinner-or-event pattern.
  - **What the sources say:** The meter time limit applies to continuous parking[^pmb-5-3a], and the 10:00 pm–9:00 am period is free of meter charges[^pmb-6-3]. Section 5.2 already treats the 10:00 pm boundary, and Section 5.3 the 6:00 pm boundary.
  - **What they do not say:** Nothing new; the difficulty is combining the two boundaries in one stay.
  - **Options:** **A.** Keep it unsupported in the first version of Overnight Lite. **B.** Support it by applying the tri-state rule (5.3) at 6:00 pm and the 5.2 rule at 10:00 pm.
  - **Proposed rule:** A for the first version, with an explicit unsupported reason, because B combines two boundary rules and needs its own tests.
- **Question 2 — Which calendar day is used for prohibitions after midnight.** Treating a 1:00 am Saturday arrival as part of Friday's night window must not change the day used to evaluate restrictions.
  - **What the sources say:** The dataset states prohibition days such as `Mon-Fri` or `Tuesdays`; it does not define how a night window relates to them.
  - **Proposed rule:** The night window is used only to decide which mode applies and which evening rate and limit apply. Each part of the stay is checked against prohibitions using its actual calendar day (Saturday 1:00–8:00 am is checked as Saturday). Prohibitions that themselves cross midnight follow 5.5 (attributed to their start day).
- **Question 3 — Overlap between the two modes.** A stay such as 8:00–9:30 pm on the same day fits both modes.
  - **Proposed rule:** If the stay ends by 10:00 pm on the arrival date, daytime mode applies; otherwise Overnight Lite applies if the stay fits the night window; otherwise unsupported. Both modes give the same result for the 6:00–10:00 pm segment, so this only fixes which code path runs.
- **Implemented in:** Not yet in the handoff; would revise handoff §3.2, §3.3, §4.3, and §7.2 steps 2–3 if Overnight Lite is adopted.

[^pmb-6-3]: Parking Meter By-law No. 2952, §6(3). https://bylaws.vancouver.ca/2952c.pdf

### 5.11 Removing the 9:00 am–10:00 pm supported window

- **Status:** Team decision (2026-10-11)
- **Decision:**
  1. The rules engine uses a single timeline from the start; there are no separate daytime and overnight code paths.
  2. Fees and meter time limits are split at 9:00 am, 6:00 pm, 10:00 pm, and midnight.
  3. Rush hours and prohibitions are checked against each meter's own intervals on each segment's actual calendar day.
  4. Stays are supported for up to 24 hours, crossing at most one midnight.
  5. The Day 2 deployment may restrict the supported window to 9:00 am–10:00 pm through a configuration value.
  6. Once the overnight and cross-day tests pass, the restriction is removed.
- **Background:** The MVP limits stays to the same day between 9:00 am and 10:00 pm (handoff §3.2, §7.2 steps 2–3). The window was set to avoid three unresolved issues: whether the meter time limit keeps counting after 10:00 pm, which day's rules apply after midnight, and how the next morning's paid period works. The first is now addressed by 5.2 and the second by 5.5 and 5.10. This item evaluates removing the window and evaluating any stay with one timeline engine.
- **Proposed engine:** Split every stay into segments at 9:00 am, 6:00 pm, 10:00 pm, and midnight. Paid segments use their own rate and time limit; free segments (10:00 pm–9:00 am) cost $0 and do not consume the meter time limit (5.2). The 6:00 pm boundary keeps the tri-state rule (5.3). Rush hours and prohibitions are checked on each segment's actual calendar day (5.4, 5.10). This replaces the two-mode design in 5.10.
- **Question 1 — Time limit after 9:00 am the next morning.**
  - **What the sources say:** The meter time limit applies to continuous parking[^pmb-5-3a], and the overnight period is free of meter charges[^pmb-6-3]. The 2019 Council record describes the next-morning maximum as counted from when paid parking resumes, with a 3-hour meter usable until noon[^coun-park-until].
  - **What they do not say:** Whether time parked during the previous evening's paid period (6:00–10:00 pm) carries into the next morning's limit. The Council example implies it does not, but it is a motion preamble, not by-law text.
  - **Rule:** The meter time limit restarts at 9:00 am, consistent with 5.2 (interpretation supported by official materials).
- **Question 2 — Three-hour rule for stays continuing into the morning.** The Street and Traffic By-law's general three-hour rule runs from 8:00 am to 6:00 pm[^stb-17-6f]. For an overnight or cross-day stay, this can affect a meter with any daytime limit, not only `4 Hr` or `No Time Limit`, because the general-rule window starts at 8:00 am while the next meter period starts at 9:00 am. For example, at a `3 Hr` meter, staying until noon uses exactly 3 hours of the restarted meter period (9:00 am–12:00 pm), but occupies 4 hours of the general-rule window (8:00 am–12:00 pm). The Council's Park Until example supports the meter calculation but does not resolve whether the general three-hour rule also applies.
  - **Rule:** For each actual calendar day, calculate the stay's overlap with 8:00 am–6:00 pm. Apply all definite meter-limit, rush-hour, and prohibition checks first and combine results using the precedence in 5.9: any definite violation returns `legal=False`. Otherwise, if the overlap is more than 180 minutes, return `legal=None` and do not recommend, regardless of the meter's daytime limit, because CurbCheck cannot determine whether a driver exception applies. Exactly 180 minutes does not trigger this guard.
  - **Minimum cross-day tests:** At a `3 Hr` meter, an overnight stay ending at 12:00 pm returns `legal=None`; the same stay ending at 11:00 am does not trigger this guard because the 8:00–11:00 am overlap is exactly 180 minutes.
- **Question 3 — Maximum stay length.** Without the window, stays could cover several days. The by-law treats a vehicle parked continuously for more than 14 days as abandoned[^stb-72a], but multi-day stays would also multiply the uncertain rules above.
  - **Rule:** Cap stays at 24 hours and at most one midnight.
- **Advantages:**
  - Supports evening and late-night drivers, including arrivals before 6:00 pm that end after 10:00 pm (5.10, Question 1) and stays continuing past 9:00 am.
  - One segment-based engine is simpler to test than two modes with a boundary between them, and the window becomes a configuration value rather than branching logic.
  - Prohibition parsing already keeps full 24-hour intervals (5.5), so no preprocessing change is needed.
- **Disadvantages and risks:**
  - More of the verdict depends on interpretations rather than by-law text (5.2, Question 1 above, 5.9).
  - More test cases: the 9:00 am restart, the 8:00 am three-hour window, morning rush overlap, cross-midnight prohibitions with day attribution, and the 24-hour cap.
  - It changes confirmed handoff rules (§3.2, §3.3, §4.3, §7.2 steps 2–3, §12) during a three-day build.
- **Feasibility:** The engine itself is moderate work if built segment-based from the start. The main cost is tests and handoff changes, not new data processing.
- **Implemented in:** Not yet in the handoff; requires revising handoff §3.2, §3.3, §4.3, §7.2 steps 2–3, and §12.

[^coun-park-until]: Vancouver City Council, Regular Council Meeting Minutes, January 29, 2019, page 34, Motion B4, whereas-clause 9. https://council.vancouver.ca/20190129/documents/regu20190129min.pdf
[^stb-72a]: Street and Traffic By-law No. 2849, §72A(2)(vi). https://bylaws.vancouver.ca/2849c.pdf

## 6. City View — Open Data Sources

### Parking Tickets

- 2026 dataset: https://opendata.vancouver.ca/explore/dataset/parking-tickets/
- 2020–2025 dataset: https://opendata.vancouver.ca/explore/dataset/parking-tickets-2020-2025/

Used for ticket concentration and infraction-category analysis. Ticket volume represents enforcement activity, not parking demand or the probability of receiving a ticket.

### Property Addresses

- URL: https://opendata.vancouver.ca/explore/dataset/property-addresses/

Used to assign approximate coordinates to normalized ticket blocks.

### 3-1-1 Service Requests — Stretch Feature Only

- URL: https://opendata.vancouver.ca/explore/dataset/3-1-1-service-requests/

If implemented, this dataset represents resident requests, not tickets or confirmed violations.

## 7. API Documentation

### Opendatasoft Explore API v2.1

- URL: https://help.opendatasoft.com/apis/ods-explore-v2/

Used to verify that the records endpoint is paginated while the export endpoint can return the complete dataset, and that `total_count` can be used to check snapshot completeness.

## 8. Suggested Demo UI Copy

### Short overnight note

> Metered parking is generally free from 10:00 pm to 9:00 am, but posted restrictions and other parking rules still apply. Vancouver's Park Until feature allows drivers to pay ahead for the next morning. Posted signs take precedence.

### When no known overnight restriction is found

> No known overnight restriction was found in the meter dataset. This is data-based guidance, not a guarantee that parking is legal. Check the posted signs before leaving your vehicle.

### When a known restriction overlaps the stay

> Not recommended: this stay overlaps a {zone} restriction listed in the meter dataset ({days}, {time}).

### Scope disclosure

While the supported window is restricted (5.11, decision 5):

> CurbCheck currently evaluates same-day stays between 9:00 am and 10:00 pm.

After the restriction is removed:

> CurbCheck evaluates stays of up to 24 hours that cross at most one midnight.

## 9. Required Caveats

- Posted signs and current meter information take precedence.
- CurbCheck does not show real-time space availability.
- Open-data records may not reflect temporary construction, special-event, or emergency restrictions.
- A zero meter fee does not mean unrestricted parking.
- Results should be described as data-based guidance, not a legal guarantee.
- The current by-laws are the controlling reference. The 2019 Council minutes and the FOI training material are used only as supporting evidence for interpretations in Section 5 (see 5.2).
