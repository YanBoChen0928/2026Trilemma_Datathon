# CurbCheck Manual Test Checklist

Use this checklist for behavior that unit tests and LLM-generated tests cannot verify reliably: map interaction, UI wording, data plausibility, cross-page behavior, and the deployed environment.

Do not use the rules engine itself as the only source of the expected result. For data and cost checks, compare directly with `data/meters_clean.csv` or the dated raw snapshot and calculate the expected value independently.

## Test Record

- Tester:
- Date and time:
- Git commit:
- Environment: local / deployed
- Browser:
- Current supported-window configuration:

## Must Pass Before the Demo

| ID | Scenario | Input / Steps | Expected result and human observations | Actual observation | Pass / Fail |
| --- | --- | --- | --- | --- | --- |
| H01 | Golden path | Load the demo example or choose the demo destination on the map. Enter the demo date, arrival time, and duration. | The destination updates correctly; no more than three recommendations appear; markers and cards refer to the same meter IDs; locations, approximate distances, and costs look plausible. |  |  |
| H02 | Independent source-data check | Select at least three recommended meters. Compare each result directly with `meters_clean.csv` or the raw snapshot. | `meter_id`, coordinates, daytime/evening rates, time limits, rush hours, and prohibition fields agree with the source rows. Record the checked IDs below. |  |  |
| H03 | Independent cost calculation | Hand-calculate one stay inside a single paid window. Then hand-calculate one stay crossing 6:00 pm by pricing the daytime and evening minutes separately. | UI cost equals the independent calculation, apart from documented currency rounding. There are no negative, missing, or `NaN` costs. A cross-6:00 pm legal verdict also follows the handoff's tri-state rule. |  |  |
| H04 | Closest meter rejected | Choose a destination/time for which the geographically closest meter cannot be recommended. | The app still returns other legal options when available and clearly explains why the closest meter was rejected: rush hour, prohibition, meter time limit, unsupported data, or `legal=None`. |  |  |
| H05 | Uncertain verdict wording | Exercise a case that returns `legal=None`, such as the three-hour guard or an unresolved 6:00 pm reset. | The result is not recommended. The UI explains the uncertainty and does not call the stay definitely legal or definitely illegal. `Posted signs take precedence.` remains visible. |  |  |
| H06 | No-result and invalid-input states | Test an area with no eligible nearby result, a non-positive duration, a stay outside the currently enabled window, and a simulated missing/unreadable data file if practical. | Each case shows a useful user-facing explanation rather than an empty panel or traceback. A configuration-gated stay states the current supported scope. |  |  |
| H07 | Map and page behavior | Click a second destination, change the date/time, and switch between Driver and City pages. Also try the advanced latitude/longitude inputs if present. | Results recompute rather than showing stale recommendations; map markers match cards; Driver and City map states do not overwrite each other; OSM attribution and `Posted signs take precedence.` are visible. |  |  |
| H08 | Clean deployed-session smoke test | Open the deployed app in a new private/incognito browser session and complete the demo flow once. | Driver and City pages open; committed data files load through repository-relative paths; the map renders; the demo example succeeds without local-machine paths, cached state, or uncaught errors. |  |  |

## Required After the 9:00 am–10:00 pm Gate Is Removed

Do not remove the configuration gate until the automated timeline tests pass and these behaviors have been checked manually.

| ID | Scenario | Input / Steps | Expected result and human observations | Actual observation | Pass / Fail |
| --- | --- | --- | --- | --- | --- |
| H09 | Free overnight segment | Test 11:00 pm–6:00 am at a meter with no overlapping known restriction. | Estimated cost is `$0`; the UI still warns that posted restrictions and signs take precedence. |  |  |
| H10 | Cross-midnight prohibition | Test 7:00 pm–1:00 am at a meter with a `6:00pm to 2:00am` prohibition. | The stay is not recommended, and the explanation identifies the prohibition rather than the meter price. |  |  |
| H11 | Actual calendar day after midnight | Test an early-Saturday stay against a `Mon-Fri` prohibition that covers the same clock time. | The Friday restriction does not incorrectly apply to the Saturday segment, except when it is the carried-over portion of a cross-midnight restriction anchored on Friday. |  |  |
| H12 | 9:00 am meter-limit restart | Test a stay that continues from the free overnight period into the next paid period. | Cost begins at 9:00 am, and the applicable weekday/weekend meter limit restarts at 9:00 am. |  |  |
| H13 | Overnight three-hour guard | At a `3 Hr` meter, compare an overnight stay ending at 11:00 am with one ending at 12:00 pm. | The 8:00–11:00 am overlap is exactly 180 minutes and does not trigger the guard; the stay ending at noon returns `legal=None` unless another definite violation already makes it `False`. |  |  |
| H14 | Maximum supported stay | Try a stay of exactly 24 hours, a stay longer than 24 hours, and a stay crossing more than one midnight boundary. | The valid boundary case follows the documented rule; longer stays or stays crossing more than one midnight are unsupported with a clear scope message. |  |  |

## Source-Data Spot Checks

Record the three meters used for H02 so another person can repeat the comparison.

| Meter | `object_id` | `meter_id` | Fields checked | Source row matches? | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 |  |  | coordinates, rates, limits, rush, prohibitions |  |  |
| 2 |  |  | coordinates, rates, limits, rush, prohibitions |  |  |
| 3 |  |  | coordinates, rates, limits, rush, prohibitions |  |  |

## Sign-off

- Automated tests passed at commit:
- Manual must-pass failures remaining:
- Timeline gate removed: yes / no
- Demo-ready decision and owner:
- Follow-up issues:
