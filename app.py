"""CurbCheck entry point: page setup, top navigation, and the shared footer.

Run locally with:  streamlit run app.py
"""

import streamlit as st

REPO_URL = "https://github.com/YanBoChen0928/2026Trilemma_Datathon"
LICENCE_URL = "https://opendata.vancouver.ca/pages/licence/"

st.set_page_config(page_title="CurbCheck", page_icon="assets/favicon.png", layout="wide")
st.logo("assets/logo.png", size="large")

# Pages live in views/, not pages/: a pages/ folder would also trigger
# Streamlit's automatic sidebar navigation on a cold start.
page = st.navigation(
    [
        st.Page("views/home.py", title="Home", default=True),
        st.Page("views/driver.py", title="Driver View", icon="🚗"),
        st.Page("views/city.py", title="City View", icon="🏙️"),
    ],
    position="top",
)
page.run()

# Shared footer, shown under every page.
st.divider()
st.caption(
    "Data: City of Vancouver Open Data, via the Trilemma Foundation data catalog. "
    f"Contains information licensed under the [Open Government Licence – Vancouver]({LICENCE_URL}). "
    "Map data © OpenStreetMap contributors."
)
st.caption(
    "Built by Anahid, Juwon, and Yan-Bo for the Trilemma × Northeastern Datathon, "
    f"Vancouver 2026 · [GitHub]({REPO_URL})"
)
