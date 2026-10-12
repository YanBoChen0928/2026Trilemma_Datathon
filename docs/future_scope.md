# CurbCheck Future Scope

## 1. Purpose

This document records post-MVP product and architecture ideas. None of these items are required for the current demo. The existing Python preprocessing, rule engine, ranking logic, and tests remain the source of truth.

The main future goal is to make CurbCheck easier to use on a phone and easier to evolve into a production web application without rewriting verified parking rules.

## 2. What the Current MVP Already Does Well

- The full driver flow works: choose a destination and stay, evaluate nearby meters, and explain the result.
- The map and result explanations make the recommendation auditable.
- The UI communicates the supported scope and keeps the posted-sign disclaimer visible.
- Parking rules and ranking already live outside the Streamlit page, which makes a future frontend replacement practical.

## 3. UI/UX Improvements

### 3.1 Immediate improvements that can remain in Streamlit

These are lower-risk improvements and do not require a React rewrite:

- Add map filters for `Recommended`, `Conflicts`, and `Unsupported` meters.
- Cluster dense markers or hide most rejected meters by default. The current red markers dominate the map when many nearby meters conflict.
- Replace long repeated rejection paragraphs with a compact summary, for example:
  - `47` exceed the time limit
  - `12` overlap a rush-hour restriction
  - Expand to view exact time windows and details.
- Make the no-result state actionable. Suggested actions may include shortening the stay, changing the arrival time, or moving the destination pin. Only show an alternative when it can be computed deterministically.
- Give the selected or recommended meter a stronger visual treatment than other markers.
- Keep advanced coordinates and the full candidate table collapsed by default.
- Show the parking-data snapshot date near the results.
- Use icons and text in addition to colour so red/green is never the only status signal.

### 3.2 Mobile and responsive design (RWD)

The desktop two-column layout should become a single task flow on narrow screens:

1. Choose destination.
2. Enter arrival and duration.
3. Review the best result.
4. Open the map or full explanation when needed.

Recommended mobile behaviour:

- Use a `Map / List` segmented control instead of showing a large map and a long result list at the same time.
- Use a map height based on the viewport, approximately `40–50vh`, instead of a fixed desktop height.
- Show the best recommendation, or the no-result message, in a bottom sheet above the map.
- Put filters and advanced inputs in a drawer or expandable section.
- Keep primary buttons and controls large enough for touch and usable with one hand.
- Respect mobile safe areas and avoid controls underneath browser or device chrome.
- Keep the most important result visible without requiring the user to scroll through every input again.
- Test at minimum at 360 px, 390 px, and 430 px widths, plus tablet and landscape layouts.

### 3.3 UX states that need explicit designs

- Initial state: explain that the user can tap the map or use their location.
- Loading state: show that nearby meters are being evaluated.
- Recommendation state: show meter ID, estimated cost, approximate distance, allowed stay, and key caveats.
- No-result state: summarize why candidates failed and provide a safe next action.
- Uncertain state: distinguish `legal = None` from a confirmed conflict and explain why CurbCheck cannot recommend it.
- Data or network error: preserve the user's input and provide a retry action.

Accessibility should include keyboard navigation, visible focus states, adequate contrast, screen-reader labels, scalable text, and status indicators that do not depend only on colour.

### 3.4 Destination search

The Driver View already has a **block search**: drivers can type part of a street name and pick one of the 10,450 Vancouver 100-blocks in `data/block_coords.csv`. It works offline and needs no external service.

Searching for **any full street address** (for example, a house number that is not a block centre) would need geocoding:

- An external geocoding service, which adds a network dependency, usage limits, and possibly cost.
- Address matching and ambiguity handling, such as misspellings, unit numbers, and addresses outside Vancouver.
- Privacy review, because typed addresses would be sent to a third party.

Estimated effort: about 4–6 hours on top of the block search. Treat it as a post-datathon improvement, after the responsive design work, and keep the block search as the offline fallback.

## 4. Is a Formal React Application Possible?

Yes. A formal React frontend is feasible, but it should be a progressive migration rather than a rewrite of the parking logic.

### Recommended target architecture

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

### Suggested frontend choices

- **Next.js + React + TypeScript** for a maintainable responsive web application.
- **MapLibre GL JS** for a production map with clustering, layers, and smoother handling of dense spatial data. React-Leaflet is also a reasonable lower-migration option if the team wants to stay closer to the current Leaflet map.
- Responsive CSS can use CSS Modules, plain CSS, or a utility framework; the exact styling library is less important than defining the mobile layout and component states first.

The map must retain OpenStreetMap attribution, and a production deployment should use an appropriate tile provider rather than assuming public community tiles are an unlimited production service.

### Minimal API surface

The first React version only needs a small backend contract:

- `POST /api/v1/parking/search`
  - Input: destination coordinates, Vancouver-local arrival datetime, duration, and search radius.
  - Output: recommendations, closest rejected option, rejection summary, disclaimers, and data version.
- `GET /api/v1/metadata`
  - Output: dataset snapshot dates, supported scope, and rule-engine version.
- `GET /api/v1/health`
  - Output: service readiness for deployment monitoring.

FastAPI can publish an OpenAPI schema, which can later be used to generate or validate TypeScript API types.

## 5. Data and Backend Growth

### Near term

- Continue loading the versioned cleaned CSV into memory for the demo and early deployments.
- Return structured reason codes as well as human-readable messages.
- Keep golden test cases that compare API output with the existing Python rule-engine output.
- Expose the data snapshot date and rule version in every search response.

### Only when usage or data size justifies it

- Move spatial queries to PostgreSQL/PostGIS.
- Add a scheduled data-refresh job with validation before a new snapshot becomes active.
- Keep the previous valid snapshot available for rollback.
- Add basic monitoring for API errors, data freshness, and response time.

A database, accounts, microservices, or real-time infrastructure are not prerequisites for the first React version.

## 6. Recommended Migration Sequence

### Phase 0 — Finish and protect the MVP

- Complete the current Streamlit flow and manual testing.
- Freeze the API-independent Python rule and ranking behaviour with tests.

### Phase 1 — Improve the current UI

- Add responsive Streamlit styling where practical.
- Reduce map clutter.
- Improve the no-result summary and mobile reading order.
- Perform human tests on phone-sized browsers.

### Phase 2 — Add a Python API boundary

- Wrap the existing rule and ranking functions with FastAPI.
- Define versioned request and response models.
- Verify API results against the current unit and golden tests.

### Phase 3 — Build the React driver experience

- Implement the Driver View first because it has the strongest mobile use case.
- Reuse the Python API rather than porting rules to TypeScript.
- Run mobile, accessibility, and end-to-end tests before replacing the Streamlit page.

### Phase 4 — Expand the City View

- Add city rate and ticket layers through separate read-only endpoints.
- Add filters, legends, and downloadable summaries only after the core map remains readable on desktop and tablet.

### Phase 5 — Operational improvements

- Automate data refresh and validation.
- Add a spatial database and caching only if performance measurements show a need.
- Add monitoring and rollback procedures for production deployment.

## 7. Suggested Priority

| Priority | Work |
| --- | --- |
| P1 after the demo | Mobile reading order, map/list toggle, marker filtering or clustering, compact conflict summary, accessibility pass |
| P2 | FastAPI wrapper and stable API contract around the existing Python logic; full-address search through geocoding (Section 3.4) |
| P3 | React/Next.js Driver View proof of concept |
| P4 | React City View, scheduled data refresh, and production monitoring |
| Later only if justified | PostGIS, user accounts, saved trips, notifications, or native mobile apps |

## 8. What Not to Add Yet

To avoid turning a strong MVP into an unfinished platform, postpone:

- Rewriting parking rules in TypeScript.
- User accounts and saved profiles.
- Payment integration.
- Real-time occupancy claims without an authoritative live data source.
- LLM-generated legal or parking decisions.
- Microservices or a database migration before performance requires them.
- Separate native iOS and Android applications before the responsive web experience is validated.

## 9. Future Acceptance Checks

A future responsive or React version should meet these checks:

- No horizontal overflow at 360 px width.
- Destination, stay details, and the primary result can be completed and understood with one mobile task flow.
- Map and list views remain usable with touch, keyboard, and screen readers.
- The same input produces the same legal state, cost, ranking, and reason codes as the Python reference tests.
- `True`, `False`, and `None` legal states are visually and textually distinct.
- Posted-sign disclaimers, approximate-distance wording, data dates, and map attribution remain visible.
- The user can recover from no-result and error states without re-entering all inputs.

## 10. Technical References

- [React documentation](https://react.dev/)
- [Next.js App Router documentation](https://nextjs.org/docs/app)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [MapLibre GL JS documentation](https://maplibre.org/maplibre-gl-js/docs/)

