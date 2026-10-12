"""CurbCheck entry point: page setup, top navigation, and the shared footer.

Run locally with:  streamlit run app.py
"""

import streamlit as st

from views.icons import GITHUB_SVG, ICON_CSS

REPO_URL = "https://github.com/YanBoChen0928/2026Trilemma_Datathon"
LICENCE_URL = "https://opendata.vancouver.ca/pages/licence/"
TRILEMMA_URL = "https://www.trilemma.foundation/"
NEU_VANCOUVER_URL = "https://www.northeastern.edu/vancouver/"

st.set_page_config(page_title="CurbCheck", page_icon="assets/favicon.png", layout="wide")
st.logo("assets/logo.png", size="large")

# Pages live in views/, not pages/: a pages/ folder would also trigger
# Streamlit's automatic sidebar navigation on a cold start.
page = st.navigation(
    [
        st.Page("views/home.py", title="Home", icon="🏠", default=True),
        st.Page("views/driver.py", title="Driver View", icon="🚗"),
        st.Page("views/city.py", title="City View", icon="🏙️"),
        st.Page("views/about.py", title="About", icon="ℹ️"),
    ],
    position="top",
)
page.run()

# Shared footer, shown under every page.
st.divider()
st.html(
    f"<style>{ICON_CSS} .cc-built {{font-size: 0.875rem; color: rgba(46, 52, 59, 0.6); margin: 0;}}"
    " .cc-built a {color: inherit;}</style>"
    '<p class="cc-built">Built by Anahid, Juwon, and Yan-Bo for the Trilemma × Northeastern '
    f'Datathon, Vancouver 2026 · <a href="{REPO_URL}" target="_blank" rel="noopener">'
    f"{GITHUB_SVG}GitHub</a></p>"
)
with st.container(horizontal=True, gap="small"):
    st.page_link("views/about.py", label="About the team", icon=":material/group:")
    st.page_link(TRILEMMA_URL, label="Trilemma Foundation", icon=":material/open_in_new:")
    st.page_link(NEU_VANCOUVER_URL, label="Northeastern University Vancouver",
                 icon=":material/open_in_new:")
st.caption(
    "Data: City of Vancouver Open Data, via the Trilemma Foundation data catalog. "
    f"Contains information licensed under the [Open Government Licence – Vancouver]({LICENCE_URL}). "
    "Map data © OpenStreetMap contributors."
)
