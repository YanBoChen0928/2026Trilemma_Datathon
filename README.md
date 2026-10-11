# CurbCheck

Vancouver's street parking rules switch by time of day. CurbCheck helps drivers check whether a whole stay is legal and what it will cost, and shows the City where its rules trip people up.

Built for the Trilemma × Northeastern Datathon, Vancouver (2026).

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Posted signs take precedence over CurbCheck's results.

Team conventions are in `CONTRIBUTING.md`.
