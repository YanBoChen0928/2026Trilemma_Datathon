# Meter Data Decisions — For Team Review

> Status: All items resolved (2026-10-11)
> Owner: Yan-Bo (Driver View)
> Source snapshot: `parking-meters`, downloaded 2026-10-11T19:11:12Z, 3,642 records
> Related: `mvp_implementation_handoff_en.md` §3.2, §3.3, §4.3, §6.2, §7.2, §12; `references.md` §5

During the Step 2 inventory of the raw meter snapshot, three questions came up that the handoff did not yet answer (items 1–3). Item 4 records the scope change that followed from the inventory. Each item below lists what the data shows, the options, and the recommendation. Once confirmed, the decisions will be written into the handoff. Counts cover all 3,642 records unless stated otherwise.

---

## 1. Prohibition time formats not covered by the handoff

**Status: Adopted, revised (2026-10-11).** `Noon`, `Midnight`, and `Anytime` are parsed explicitly, and intervals are kept in full instead of being clipped, because the rules engine now uses a full timeline (`references.md` §5.5, §5.11).

**Finding.** Besides the regular format (e.g., `7:00am to 6:00pm`), `prohibition_1_time` and `prohibition_2_time` contain:

- `Noon` and `Midnight` as endpoints (e.g., `7:00am to Noon`, `5:00pm to Midnight`);
- `Anytime` (3 records);
- intervals that cross midnight (37 records in total), e.g., `6:00pm to 2:00am`, `9:00pm to 4:00am`, `3:00pm to 9:30am`.

**Adopted rule.** Parse `Noon` as 12:00 pm, an ending `Midnight` as the end of the day, and `Anytime` as all day. Preserve every interval over the full 24-hour timeline instead of clipping it to a UI window. Store parsed start and end minutes plus `crosses_midnight` and `all_day` flags for each prohibition group. A cross-midnight prohibition is anchored to its listed start day, and its after-midnight portion continues into the following calendar day.

## 2. Rush-hour fields do not state which days they apply

**Status: Adopted — Option A (team decision, 2026-10-11).** Recorded in `references.md` §5.4; handoff §7.2 step 6 still to be updated.

**Finding.** `am_rush_hours` and `pm_rush_hours` contain only a time range (e.g., `7:00am to 10:00am`, `3:00pm to 7:00pm`) with no days of the week. Posted rush-hour restrictions are usually weekday-only, but the dataset does not say so, and handoff §7.2 step 6 does not address weekends.

**Options.**

- **A.** Apply rush-hour restrictions every day, including weekends.
- **B.** Apply them on weekdays only.

**Recommendation: A.** Applying them every day can only make results more conservative (more stays marked not recommended); it never produces a positive legal verdict that the data does not support. Option B would assume a rule the data does not state. The UI should note that rush-hour restrictions are applied every day because the data does not specify days. The demo (Tuesday) is not affected either way.

## 3. `meter_id` is not unique

**Status: Resolved as recommended (2026-10-11).** `object_id` is the unique record key; `meter_id` is shown to drivers; duplicates are counted in the preprocessing report.

**Finding.** `meter_id` has 3,641 unique values across 3,642 records. `B71509` appears twice in Fairview: one record is `Out of Service` and the other `In Service`, at nearly the same coordinates. `object_id` is unique.

**Impact.** Only the `In Service` record can pass preprocessing, so recommendations are not affected. However, `meter_id` cannot be used as a unique key for joins or lookups.

**Recommendation.**

- Keep the source `object_id` in `meters_clean.csv` as the unique record key.
- Keep `meter_id` as the identifier shown to drivers.
- Report the number of duplicate `meter_id` values in `data/meters_preprocessing_report.json`.

---

## For Information — Effect of Handoff §6.2 Rule 14

This is not a decision item, but it changes the Step 2 checkpoint.

One record, `291103` (Downtown, In Service), has a prohibition time and zone (`7:00am to 11:00am`, `CVLZ`) but no days. Under rule 14, a partially filled prohibition group makes the record unsupported, because the days on which the restriction applies are unknown.

| Scope | Handoff §6.3 (2026-10-10) | After rule 14 (2026-10-11 snapshot) |
| --- | --- | --- |
| Citywide | 2,761 | 2,760 |
| Downtown | 637 | 636 |

Rule 15 (coordinates) does not remove any record in this snapshot.

## 4. Scope change: lift the same-day 9:00 am–10:00 pm limit

**Status: Adopted (team decision, 2026-10-11).** This is a change to the confirmed MVP scope; handoff §3.2, §3.3, §4.3, §7.2, and §12 have been updated accordingly.

**Previous rule.** The MVP evaluated only same-day stays between 9:00 am and 10:00 pm. The limit was set before the data was inspected, to avoid three open questions: whether the meter time limit keeps counting after 10:00 pm, which day's rules apply after midnight, and how the next morning's paid period works.

**Decision.**

- Support stays of up to 24 hours that cross at most one midnight.
- Evaluate every stay with one timeline engine, split at 9:00 am, 6:00 pm, 10:00 pm, and midnight. There are no separate daytime and overnight code paths.
- The overnight segment (10:00 pm–9:00 am) costs $0 and does not consume the meter time limit; the limit restarts at 9:00 am.
- The Day 2 deployment may keep the old 9:00 am–10:00 pm limit through a configuration value. The limit is removed once the timeline tests in handoff §12 pass.

**Reasons.**

1. **The data turned out to be simpler than expected.** After downloading the snapshot, the rule fields proved to use a small, regular set of formats: two AM and two PM rush-hour intervals, a short list of time-limit values, and prohibition times that can all be parsed, including `Noon`, `Midnight`, `Anytime`, and intervals that cross midnight (item 1). Supporting overnight stays needs no new data and no change to preprocessing.
2. **The open questions behind the old limit now have answers.** Parking Meter By-law §6(3) makes 10:00 pm–9:00 am free of meter charges, and the City's Park Until record describes the next-morning time limit as counted from 9:00 am (`references.md` §5.2, §5.11). Restrictions after midnight are checked on each segment's actual calendar day (`references.md` §5.5, §5.10).
3. **Evening and late-night drivers are a real use case.** Drivers going to dinner, events, or night shifts often arrive before 10:00 pm and leave after it, or park overnight. The old limit returned "unsupported" for all of these.
4. **One timeline engine is simpler than two modes.** An earlier proposal added a separate overnight mode, which created boundary cases between modes. A single timeline removes those cases, and the supported window becomes a configuration value.
5. **Risk stays controlled.** Uncertain rules still never produce a positive verdict: the 6:00 pm tri-state rule (handoff §7.4) and the general three-hour guard (`references.md` §5.9) return `legal=None`. The first deployment can keep the old limit, so the demo does not depend on the new tests.

**Still out of scope.** Stays longer than 24 hours or crossing more than one midnight.
