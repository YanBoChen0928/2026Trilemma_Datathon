"""CurbCheck entry point.

Run locally with:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="CurbCheck", page_icon="🅿️", layout="wide")

st.title("CurbCheck")
st.write(
    "Vancouver's street parking rules switch by time of day. "
    "CurbCheck helps drivers check whether a whole stay is legal and what it "
    "will cost, and shows the City where its rules trip people up."
)

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/driver.py", label="Driver View", icon="🚗")
    st.caption("Find street parking that is legal for your whole stay.")
with col2:
    st.page_link("pages/city.py", label="City View", icon="🏙️")
    st.caption("See meter rates and where tickets concentrate Downtown.")

st.info("Posted signs take precedence over CurbCheck's results.")
