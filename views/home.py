"""CurbCheck home page: what the product does and where to start."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from curbcheck.ranking import SEARCH_RADIUS_M

DATA = Path(__file__).resolve().parent.parent / "data"
VIDEO_URL = "https://youtu.be/AlxIEvF085s"

HERO = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700&display=swap');
.cc-hero {background: #2E343B; border-radius: 12px; overflow: hidden;}
.cc-hero-text {padding: clamp(1.25rem, 4vw, 2.75rem) clamp(1rem, 5vw, 3rem) 0;}
.cc-title {color: #F3F5F7; font-family: 'Barlow Condensed', 'Arial Narrow', sans-serif;
           font-size: clamp(2.8rem, 8vw, 5rem); font-weight: 700; line-height: 0.95; margin: 0;}
.cc-slogan {color: #AEB6BE; font-size: clamp(1.1rem, 2.6vw, 1.6rem); line-height: 1.3;
            margin: 0.4rem 0 0;}
.cc-lede {color: #C9CED3; font-size: clamp(0.95rem, 1.7vw, 1.05rem); line-height: 1.6;
          margin: 0.9rem 0 0; text-wrap: pretty;}
.cc-lane {height: 6px; margin: clamp(1.25rem, 3vw, 2rem) 0 clamp(1rem, 2.5vw, 1.75rem);
          background: repeating-linear-gradient(90deg, #454C54 0 56px, transparent 56px 112px);}
.cc-curb {background: #C9CED3; padding: 10px clamp(1rem, 5vw, 3rem) 0;}
.cc-strip {display: flex; height: clamp(26px, 3.5vw, 36px);}
.cc-strip div {color: #FFFFFF; font-family: 'Barlow Condensed', 'Arial Narrow', sans-serif;
               font-size: clamp(0.85rem, 1.8vw, 1.2rem); font-weight: 700; padding-left: 8px;
               display: flex; align-items: center; white-space: nowrap; overflow: hidden;}
.cc-rush {flex: 4; background: #cf222e;}
.cc-open {flex: 3; background: #1a7f37;}
.cc-walk {background: #E6E8EA; padding: 0 clamp(1rem, 5vw, 3rem) 12px;}
.cc-hours {position: relative; height: 34px; margin-top: -1px;}
.cc-hours span {position: absolute; top: 0; transform: translateX(-50%); padding-top: 6px;
                border-left: 2px solid #2E343B; height: 8px;}
.cc-hours em {position: absolute; top: 12px; transform: translateX(-50%); font-style: normal;
              font-family: 'Barlow Condensed', 'Arial Narrow', sans-serif; font-weight: 700;
              font-size: clamp(0.8rem, 1.5vw, 1rem); color: #2E343B; white-space: nowrap;}
@media (max-width: 520px) {.cc-hours .cc-minor {display: none;}}
</style>
<div class="cc-hero">
  <div class="cc-hero-text">
    <p class="cc-title">CurbCheck</p>
    <p class="cc-slogan">Clearer parking decisions, for drivers and the City.</p>
    <p class="cc-lede">Vancouver's parking rules change by the hour. CurbCheck checks rates,
    time limits, and rush-hour rules for your whole stay before you park, and shows the City
    where tickets concentrate.</p>
    <div class="cc-lane"></div>
  </div>
  <div class="cc-curb">
    <div class="cc-strip">
      <div class="cc-rush">Rush hour</div>
      <div class="cc-open">Open to park</div>
    </div>
  </div>
  <div class="cc-walk"><div class="cc-hours">HOURS</div></div>
</div>
"""
_HOURS = ["3 pm", "4", "5", "6", "7", "8", "9", "10 pm"]
HERO = HERO.replace("HOURS", "".join(
    f'<span style="left:{i / 7 * 100:.2f}%"></span>'
    f'<em class="{"" if i in (0, 2, 4, 7) else "cc-minor"}" style="left:{i / 7 * 100:.2f}%">{h}</em>'
    for i, h in enumerate(_HOURS)))


HOW_IT_WORKS = """
<style>
.cc-how {background: #EEF0F2; border-radius: 12px; padding: clamp(1rem, 3vw, 1.75rem);
         margin-top: 1rem;}
.cc-how-title {font-size: 1.5rem; font-weight: 600; color: #2E343B; margin: 0 0 1rem;}
.cc-how-grid {display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));}
.cc-how-step {background: #FFFFFF; border: 1px solid #D0D7DE; border-radius: 10px;
              padding: 1rem 1.1rem; display: flex; gap: 0.9rem; align-items: flex-start;}
.cc-num {flex: 0 0 auto; width: 2.4rem; height: 2.4rem; border-radius: 50%; background: #1e4e8c;
         color: #FFFFFF; font-weight: 700; font-size: 1.2rem; display: flex; align-items: center;
         justify-content: center;}
.cc-how-h {font-weight: 600; color: #2E343B; margin: 0.1rem 0 0.2rem;}
.cc-how-t {color: #57606a; margin: 0; line-height: 1.5;}
</style>
<div class="cc-how">
  <p class="cc-how-title">How it works</p>
  <div class="cc-how-grid">
    <div class="cc-how-step"><span class="cc-num">1</span><div>
      <p class="cc-how-h">Pick your destination</p>
      <p class="cc-how-t">Tap the map, or enter coordinates.</p></div></div>
    <div class="cc-how-step"><span class="cc-num">2</span><div>
      <p class="cc-how-h">Set your stay</p>
      <p class="cc-how-t">When you arrive and how long you stay.</p></div></div>
    <div class="cc-how-step"><span class="cc-num">3</span><div>
      <p class="cc-how-h">Get your answer</p>
      <p class="cc-how-t">Ranked options, the reason, and directions.</p></div></div>
  </div>
</div>
"""

@st.cache_data
def key_numbers():
    report = json.loads((DATA / "meters_preprocessing_report.json").read_text())
    tickets = pd.read_csv(DATA / "tickets_block_agg.csv", usecols=["count"])
    return report["supported_records"], int(tickets["count"].sum())


st.html(HERO)
st.html(
    "<style>"
    ".st-key-cc_explore button {background: #E7EEF7; color: #1e4e8c; border: 1px solid #C9D7EA;}"
    ".st-key-cc_explore button:hover {background: #D6E2F1; color: #1e4e8c; border-color: #1e4e8c;}"
    ".st-key-cc_numbers [data-testid='stMetric'], .st-key-cc_numbers [data-testid='stCaptionContainer']"
    " {text-align: center;}"
    ".st-key-cc_numbers [data-testid='stMetricLabel'], .st-key-cc_numbers [data-testid='stMetricValue']"
    " {justify-content: center; justify-items: center;}"
    ".st-key-cc_numbers [data-testid='stMetricValue'] {font-size: clamp(2.2rem, 4vw, 2.9rem);}"
    ".st-key-cc_numbers [data-testid='stMetricLabel'] {display: flex;}"
    ".st-key-cc_numbers [data-testid='stMetricLabel'] p {font-size: 1.05rem; font-weight: 600;"
    " color: #2E343B;}"
    ".st-key-cc_numbers [data-testid='stCaptionContainer'] {margin-top: -0.9rem;}"
    "@media (min-width: 640px) {.st-key-cc_numbers [data-testid='stColumn'] + [data-testid='stColumn']"
    " {border-left: 1px solid #D0D7DE;}}"
    ".st-key-cc_numbers {margin-top: 1.5rem;}"
    ".st-key-cc_video {margin-top: 0.75rem;}"
    "[class*='st-key-cc_eyebrow_'] p {font-size: 0.875rem; color: #57606a;"
    " display: flex; align-items: center; gap: 0.35rem;}"
    "[class*='st-key-cc_eyebrow_'] span[role='img'] {color: #1e4e8c; font-size: 1.25rem;"
    " vertical-align: middle; line-height: 1;}"
    ".st-key-cc_card_driver > :last-child, .st-key-cc_card_city > :last-child {margin-top: auto;}"
    "</style>"
)

drivers, planners = st.columns(2, gap="medium")
with drivers, st.container(border=True, height="stretch", key="cc_card_driver"):
    st.container(key="cc_eyebrow_driver").markdown(":material/directions_car: For drivers")
    st.markdown("**Driver View**")
    st.write("Find metered parking that appears legal for your whole stay, "
             "ranked by cost, with directions.")
    st.caption("Posted signs take precedence over CurbCheck's results.")
    if st.button("Find parking", type="primary", icon=":material/arrow_forward:"):
        st.switch_page("views/driver.py")
with planners, st.container(border=True, height="stretch", key="cc_card_city"):
    st.container(key="cc_eyebrow_city").markdown(":material/location_city: For planners")
    st.markdown("**City View**")
    st.write("See meter rates and where Downtown tickets concentrate, "
             "by street and infraction.")
    if st.button("Explore tickets", key="cc_explore", icon=":material/arrow_forward:"):
        st.switch_page("views/city.py")

meters_checked, downtown_tickets = key_numbers()
with st.container(key="cc_numbers"):
    m1, m2, m3 = st.columns(3)
    m1.metric("Parking meters checked", f"{meters_checked:,}")
    m2.metric("Downtown parking tickets", f"{downtown_tickets:,}")
    m3.metric("Search radius", f"{SEARCH_RADIUS_M} m")
    m3.caption("around your destination")

st.html(HOW_IT_WORKS)

st.subheader("See it in 60 seconds")
_, video, _ = st.container(key="cc_video").columns([1, 3, 1])
video.video(VIDEO_URL)
