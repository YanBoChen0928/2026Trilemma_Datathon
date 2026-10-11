# Meter Data Decisions — For Team Review

> Status: Proposed, pending team confirmation
> Owner: Yan-Bo (Driver View)
> Source snapshot: `parking-meters`, downloaded 2026-10-11T19:11:12Z, 3,642 records
> Related: `mvp_implementation_handoff_en.md` §6.2, §7.2

During the Step 2 inventory of the raw meter snapshot, three questions came up that the handoff does not yet answer. Each item below lists what the data shows, the options, and the recommendation. Once confirmed, the decisions will be written into the handoff. Counts cover all 3,642 records unless stated otherwise.

---

## 1. Prohibition time formats not covered by the handoff

**Finding.** Besides the regular format (e.g., `7:00am to 6:00pm`), `prohibition_1_time` and `prohibition_2_time` contain:

- `Noon` and `Midnight` as endpoints (e.g., `7:00am to Noon`, `5:00pm to Midnight`);
- `Anytime` (3 records);
- intervals that cross midnight (37 records in total), e.g., `6:00pm to 2:00am`, `9:00pm to 4:00am`, `3:00pm to 9:30am`.

**Options.**

- **A.** Parse `Noon` as 12:00 pm, `Midnight` as the end of the day, and `Anytime` as all day. For an interval that crosses midnight, check only the part that falls inside the supported 9:00 am–10:00 pm window. For example, `6:00pm to 2:00am` becomes 6:00–10:00 pm, and `3:00pm to 9:30am` becomes two parts: 9:00–9:30 am and 3:00–10:00 pm.
- **B.** Same as A for `Noon`, `Midnight`, and `Anytime`, but mark every record with a cross-midnight prohibition as unsupported.

**Recommendation: A.** The MVP only evaluates same-day stays between 9:00 am and 10:00 pm, so clipping a cross-midnight interval to that window involves no guessing. Option B would exclude records that the MVP can evaluate safely.

## 2. Rush-hour fields do not state which days they apply

**Finding.** `am_rush_hours` and `pm_rush_hours` contain only a time range (e.g., `7:00am to 10:00am`, `3:00pm to 7:00pm`) with no days of the week. Posted rush-hour restrictions are usually weekday-only, but the dataset does not say so, and handoff §7.2 step 6 does not address weekends.

**Options.**

- **A.** Apply rush-hour restrictions every day, including weekends.
- **B.** Apply them on weekdays only.

**Recommendation: A.** Applying them every day can only make results more conservative (more stays marked not recommended); it never produces a positive legal verdict that the data does not support. Option B would assume a rule the data does not state. The UI should note that rush-hour restrictions are applied every day because the data does not specify days. The demo (Tuesday) is not affected either way.

## 3. `meter_id` is not unique

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
