# Demo Video Plan — 60 Seconds

> Status: Draft for team review
> Guidelines: [Trilemma 60-Second Demo Video Guidelines](https://github.com/TrilemmaFoundation/Datathon-Season-2026/blob/main/demo-video-guidelines.md)
> Demo scenario: README, "Demo scenario"

## 1. What the guidelines ask for

- Every team submits a 60-second demo video.
- The video should sell the problem, show the actual product as the end user would use it, and make the value obvious.
- A product walkthrough or screen recording is preferred over slides.
- A natural, scripted narration in our own voice is recommended over AI voiceovers or AI-generated video. A human voice is not strictly required, but we will use one.
- Keep technical details to a minimum; focus on the value, not the tech stack.
- The video must stand on its own, without extra explanation.
- Refine the story with the Build Session 3 feedback before recording the final version.

## 2. Division of work

| Task | Owner |
| --- | --- |
| Script, storyboard, on-screen captions | Assistant drafts; team reviews |
| Screen recording (macOS: Cmd+Shift+5) | Yan-Bo or a teammate |
| Voice narration | Yan-Bo or a teammate |
| Editing: trim, merge narration, add captions (ffmpeg, if installed) | Assistant helps after recording |
| Final cut and submission | Team |

## 3. Story

The Driver View and the City View tell one story: the same open data helps drivers avoid parking traps and helps the City see where those traps are.

- **WHY:** Vancouver's street parking rules change by the hour. A spot that looks legal at 6 pm can still be in a rush-hour zone.
- **WHAT:** CurbCheck checks the whole stay, explains why the closest meter is not recommended, and ranks legal options by cost with directions.
- **HOW:** City of Vancouver open data on meters and tickets. For the City, rush-hour tickets cluster on a few Downtown streets (City View, Insight 1).

## 4. Script and storyboard

About 150 words of narration, which takes roughly 55–60 seconds at a natural pace.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00–0:10 (WHY) | Home page, then open Driver View. | In Vancouver, a parking spot that's legal at noon can be a tow-away zone at 5 pm. Rates, time limits, and rush-hour rules all change by the hour. |
| 0:10–0:20 (WHAT) | Click the 400 block of West Hastings on the map, set the arrival time to 6:00 pm, and choose 2 hr. Do not use Load demo example in the video; a real action is more convincing. | CurbCheck checks your whole stay. Say I'm arriving on West Hastings at 6 pm for two hours. |
| 0:20–0:30 | Pause on the Closest meter card; hover over the closest red marker on the map. | The closest meter is only 17 meters away, but it's still in a rush-hour zone until 7 pm. CurbCheck flags it before I get a ticket. |
| 0:30–0:38 | Move to the three recommendation cards; click marker 1 on the map to open its popup and point to Directions. | Instead of reading every sign on the block, I get one answer and the reason: three legal options ranked by cost, four dollars each, with directions one tap away. |
| 0:38–0:45 | Change the arrival time to 5:00 pm; more red markers appear. | Arrive an hour earlier, and conflicts jump from 12 to 32 meters. Time changes everything. |
| 0:45–0:55 (HOW) | Click Home, open City View, and select Insight 1 so the map highlights those streets. Make sure the ticket total and the insight figures are visible on screen. | The same open data helps the City. 183,000 Downtown tickets show that rush-hour tickets cluster on a few streets, like Seymour, Howe, and West Pender, which may be worth reviewing for signage. |
| 0:55–1:00 | Return to the Driver View recommendations, or hold on the City View map. | CurbCheck: City of Vancouver open data, turned into a clear answer before you park. |

### Notes on the HOW section

- Say only that we use the City's open data and what it achieves. Do not describe the rules engine, the timeline, or the code.
- Keep the City View wording non-causal ("may be worth reviewing"), matching the insight text. Do not say the signs are unclear or badly designed.

## 5. Proof-of-value checks

From the Datathon build guidance shared by the team (source page not yet confirmed; likely the Build Session 3 checklist):

| Check | How the demo meets it |
| --- | --- |
| One real situation where we would use the app | Arriving on West Hastings at 6 pm for two hours |
| Problem → action in the app → visible useful result | Rules change by the hour → choose place and time → closest meter flagged, three legal options shown |
| The interface makes the purpose and result understandable | Summary line, closest-meter card, recommendation cards |
| The demo shows an action and a result it actually produces | Real map click and time selection, not the demo button |
| We can explain how the result solves the problem | "CurbCheck flags it before I get a ticket" |
| Claims are supported by visible behavior and data | Rush-hour reason on hover, $4.00 costs, 12 → 32 conflicts, ticket figures on the City View screen |
| No reliance on hypothetical features or future users | The script mentions only features that exist today |
| Simple before/after comparison | Before: read every sign on the block. After: one answer and the reason. |

## 6. Before recording

1. **Record with real actions.** Set the destination by clicking the map and choose the time and duration by hand. Keep Load demo example as a backup for live demos only.
2. **City View insights are still a draft.** `data/city_insights.md` says they need review by a second team member before the demo. Confirm that the Insight 1 figures have been checked before using them in the video.
3. **Timing is tight.** If the narration runs over 60 seconds, shorten the first WHY sentence first. Keep the 5:00 pm change; it shows best how time changes the answer.
4. **Use the deployed app if possible**, and open it a few minutes beforehand so it is awake.
5. The figures in the script come from the 2026-10-11 meter snapshot and the ticket aggregate. Re-check them if the data is refreshed.

## 7. Submission

- Submit the video and the GitHub repository through the [final submission form](https://airtable.com/appZZI7zTz3xYJE0r/pagSrc0WDreG1SxeI/form).
- The guidelines do not say whether the video is uploaded to the form or submitted as a link. Open the form to check the fields.
- If a link is required, upload to YouTube as "Unlisted" or to Google Drive with "Anyone with the link can view". Test the link in a signed-out browser.
- Make sure the GitHub repository is public, or that the judges have access.
