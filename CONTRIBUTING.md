# Contributing — CurbCheck Team Setup

This file is for the three of us. The `README.md` is for judges and first-time visitors. Engineering rules and CSV schemas live in `mvp_implementation_handoff_en.md`, which is the single engineering source of truth.

---

## 1. Step 0 — Before Writing Code

1. **Confirm two team decisions**
   - Deployment platform (recommended: Streamlit Community Cloud; see Section 7).
   - Integration and deployment owner (the handoff suggests Juwon).
2. **Freeze shared contracts**
   - `meters_clean.csv` columns: handoff §6.1.
   - `tickets_block_agg.csv` columns: handoff §9.1.
   - File names and paths: Section 4 below.
3. **Agree on the environment**: one Python version and the initial `requirements.txt` (Section 5).
4. **Freeze the demo**: destination, date, 6:00 pm arrival, and duration.

**Done when:** all three of us are building against the same structure, schemas, and environment.

## 2. Project Structure

```
app.py                  # Streamlit entry point
pages/driver.py         # Driver View (Yan-Bo)
pages/city.py           # City View (Anahid, Juwon)
curbcheck/              # Shared Python modules (preprocessing, rules engine)
data/raw/               # Raw source snapshots — NOT committed
data/meters_clean.csv   # Produced by Driver View
data/tickets_block_agg.csv  # Produced by City View
tests/                  # pytest tests
requirements.txt
README.md
CONTRIBUTING.md
```

## 3. Shared Conventions

| Item | Agreement |
| --- | --- |
| App | One Streamlit multipage app; `app.py` is the entry point |
| Pages | Pages only read preprocessed CSVs; no raw-data processing inside pages |
| Coordinates | WGS84 `lat` / `lon` |
| Map | `folium` + `streamlit-folium` on OpenStreetMap tiles, with attribution |
| Paths | Relative paths inside the repo only; never hard-code a local machine path |
| File ownership | Each person edits only their own page and scripts; `app.py` and `requirements.txt` are maintained by the integration owner |

## 4. Data Files

| File | Committed? | Produced by | Used by |
| --- | --- | --- | --- |
| `data/meters_clean.csv` | Yes (small) | Driver View | Driver View; City View rate layer |
| `data/tickets_block_agg.csv` | Yes (small) | City View | City View; Driver View (stretch: block heads-up) |
| `data/raw/*` | **No** — add to `.gitignore` | Each owner's download script | Preprocessing only |

- Raw ticket data (about 2.5 million rows for 2020–2025) can exceed GitHub's 100 MB per-file limit, so raw data never goes into the repo.
- **Push a first version of `meters_clean.csv` on Day 1**, so the City View rate layer is not blocked.
- Record each data snapshot date in the README.

## 5. Environment and `requirements.txt`

- Everyone uses the same Python version as the deployment platform.
- Initial packages: `streamlit`, `folium`, `streamlit-folium`, `pandas`, `pytest`.
- Pin each version to the one installed locally; pinning the Streamlit version is the platform's recommended practice.
- To add a package, tell the integration owner first, then add it to `requirements.txt`.

## 6. Git Workflow

- Run `git pull` before every `git push`.
- Edit only the files you own (Section 3).
- Never use `git push --force`.

## 7. Deployment

### Recommended platform: Streamlit Community Cloud

- Deploys straight from the GitHub repo: pick the repo, branch, and `app.py`.
- Pushing to GitHub redeploys automatically; changes to `requirements.txt` trigger reinstallation.
- Apps with no traffic for 12 hours go to sleep — **open the app before the demo** so it is awake.
- Resources are limited, so pages read only small preprocessed CSVs.

### Architecture

```
[Our machines]                      [GitHub]          [Streamlit Community Cloud]
raw data (not committed)
   │
preprocessing ──► data/*.csv ──┐
app.py + pages/*.py ───────────┴──► main branch ──► auto deploy ──► public URL

Backup: run locally + recorded demo video
```

### Process

1. Build a runnable shared app shell locally (no deployment required).
2. Complete Driver View and City View locally.
3. Integrate both into the same app.
4. **Deploy the complete MVP on Day 2.**
5. After deploying, check: both pages open, data loads, the map renders, and errors show clear messages.
6. Use the platform's built-in logs only; no separate monitoring.
7. Feature freeze at noon on Day 3; final test from a clean environment.
