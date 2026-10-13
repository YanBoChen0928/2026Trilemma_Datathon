"""CurbCheck About page: the problem, who it is for, the team, and the project's data."""

import base64
from html import escape
from pathlib import Path

import streamlit as st

from views.icons import GITHUB_SVG, ICON_CSS, LINKEDIN_SVG

st.set_page_config(page_title="CurbCheck — About", page_icon="ℹ️", layout="wide")

ASSETS = Path(__file__).resolve().parent.parent / "assets"
REPO_URL = "https://github.com/YanBoChen0928/2026Trilemma_Datathon"
VIDEO_URL = "https://youtu.be/AlxIEvF085s"
TRILEMMA_URL = "https://www.trilemma.foundation/"
DATATHON_URL = "https://github.com/TrilemmaFoundation/Datathon-Season-2026"
NEU_VANCOUVER_URL = "https://www.northeastern.edu/vancouver/"
LICENCE_URL = "https://opendata.vancouver.ca/pages/licence/"

TEAM = [
    {
        "name": "Anahid Raisrohani",
        "role": "Ticket data and insights",
        "photo": "team_anahid.jpg",
        "qr": "qr_anahid.png",
        "linkedin": "https://www.linkedin.com/in/anahid-raisrohani-8aa62182/",
        "bio": "Built a preprocessing pipeline to clean and combine City parking-ticket and "
               "property-address datasets, match tickets to 100-block coordinates, and "
               "categorize infractions. Created the data-quality report and scripts for "
               "generating City View insights.",
    },
    {
        "name": "Juwon Park",
        "role": "City View",
        "photo": "team_juwon.jpg",
        "qr": "qr_juwon.png",
        "linkedin": "https://www.linkedin.com/in/juwon-park-ai-data/",
        "bio": "Built the City View: the rate and ticket map, block details, insight cards, and "
               "category filter, with a layout and colours matched to the Driver View.",
    },
    {
        "name": "Yan-Bo Chen",
        "role": "Driver View and product",
        "photo": "team_yanbo.jpg",
        "qr": "qr_yanbo.png",
        "linkedin": "https://www.linkedin.com/in/yanbochenmd",
        "bio": "Built the Driver View: data preprocessing for the City's parking-meter dataset, "
               "the whole-stay rules engine, ranking, and directions. Led the UI and UX design, "
               "integrated both views, reviewed the insights, and deployed the app.",
    },
]

STYLE = """
<style>
""" + ICON_CSS + """
.cc-about-head {background: #2E343B; border-radius: 12px; padding: clamp(1.25rem, 4vw, 2rem);
                display: flex; align-items: center; justify-content: space-between; gap: 1.5rem;}
.cc-about-head p {margin: 0;}
.cc-app-qr {flex: none; background: #FFFFFF; border-radius: 10px; padding: 0.6rem 0.6rem 0.5rem;
            text-align: center; color: #57606a; font-size: 0.75rem; line-height: 1.4;}
.cc-app-qr img {width: 160px; height: 160px; display: block; image-rendering: pixelated;}
.cc-app-qr strong {color: #2E343B;}
@media (max-width: 640px) {.cc-app-qr {display: none;}}
.cc-about-title {color: #F3F5F7; font-size: clamp(1.8rem, 4vw, 2.4rem); font-weight: 700;}
.cc-about-lede {color: #C9CED3; font-size: 1.05rem; line-height: 1.6; margin-top: 0.5rem !important;
                text-wrap: pretty;}
.cc-about-grid {display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));}
.cc-about-h {font-weight: 600; color: #2E343B; font-size: 1.1rem; margin: 0 0 0.35rem;}
.cc-about-t {color: #57606a; line-height: 1.6; margin: 0;}
.cc-about-list {color: #57606a; line-height: 1.6; margin: 0; padding-left: 1.2rem;}
.cc-problem {background: #FBF4F4; border-radius: 12px;
             padding: 1rem 1.25rem;}
.cc-problem-label {color: #cf222e; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.04em;
                   margin: 0 0 0.35rem;}
.cc-who {background: #F6F7F8; border-radius: 12px;
         padding: 1rem 1.25rem;}
.cc-who-label {color: #57606a; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.04em;
               margin: 0 0 0.6rem;}
.cc-problem-h {color: #2E343B; font-size: 1.15rem; font-weight: 700; margin: 0 0 0.4rem;}
.cc-about-list strong {color: #2E343B;}
.cc-team {display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));}
.cc-member {border: 1px solid #D0D7DE; border-radius: 12px; padding: 1.25rem;
            display: flex; flex-direction: column;}
.cc-photo {width: 96px; height: 96px; border-radius: 50%; object-fit: cover;}
.cc-name {font-weight: 600; font-size: 1.1rem; color: #2E343B; margin: 0.75rem 0 0;}
.cc-role {align-self: flex-start; background: #E7EEF7; color: #1e4e8c; font-size: 0.8rem;
          font-weight: 600; padding: 0.15rem 0.6rem; border-radius: 0.5rem; margin-top: 0.35rem;}
.cc-bio {color: #57606a; line-height: 1.55; margin: 0.75rem 0 1rem; flex: 1;}
.cc-member-foot {display: flex; align-items: flex-end; justify-content: space-between; gap: 12px;}
.cc-link {color: #1e4e8c; font-weight: 600; text-decoration: none;}
.cc-link:hover {text-decoration: underline;}
.cc-qr {text-align: center; color: #57606a; font-size: 0.75rem;}
.cc-qr img {width: 88px; height: 88px; display: block; image-rendering: pixelated;}
@media (max-width: 640px) {.cc-qr {display: none;}}
.cc-mark {background: rgba(191, 135, 0, 0.18); color: inherit; padding: 0 0.2rem;
          border-radius: 0.25rem;}
.cc-orgs {display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));}
.cc-org {border: 1px solid #D0D7DE; border-radius: 12px; padding: 1.1rem 1.25rem;
         display: flex; flex-direction: column;}
.cc-org .cc-about-t {flex: 1; margin-bottom: 0.75rem;}
.cc-org-links {display: flex; flex-wrap: wrap; gap: 0.4rem 1.25rem;}
.cc-project {background: #EEF0F2; border-radius: 12px; padding: 1.25rem 1.5rem;}
.cc-project p {margin: 0;}
.cc-btns {display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.9rem;}
.cc-btn {border: 1px solid #C9D7EA; background: #FFFFFF; color: #1e4e8c; border-radius: 0.5rem;
         padding: 0.4rem 0.9rem; font-weight: 600; text-decoration: none;}
.cc-btn:hover {background: #E7EEF7;}
</style>
"""


@st.cache_data
def data_uri(file_name):
    path = ASSETS / file_name
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def member_card(m):
    name = escape(m["name"])
    return f"""
<div class="cc-member">
  <img class="cc-photo" src="{data_uri(m['photo'])}" alt="Photo of {name}">
  <p class="cc-name">{name}</p>
  <span class="cc-role">{escape(m['role'])}</span>
  <p class="cc-bio">{escape(m['bio'])}</p>
  <div class="cc-member-foot">
    <a class="cc-link" href="{m['linkedin']}" target="_blank" rel="noopener">{LINKEDIN_SVG}LinkedIn ↗</a>
    <div class="cc-qr"><img src="{data_uri(m['qr'])}" alt="QR code for {name}'s LinkedIn">Scan</div>
  </div>
</div>"""


st.html(STYLE + f"""
<div class="cc-about-head">
  <div>
    <p class="cc-about-title">About CurbCheck</p>
    <p class="cc-about-lede">A microproduct built for the Trilemma × Northeastern Datathon,
    Vancouver 2026, turning City of Vancouver open data into clear parking decisions.</p>
  </div>
  <div class="cc-app-qr"><img src="{data_uri('qr_app.png')}" alt="QR code for curbcheck.streamlit.app">
    <strong>Scan to try it</strong><br>curbcheck.streamlit.app</div>
</div>
""")

st.html("""
<div class="cc-about-grid">
  <div class="cc-problem"><p class="cc-problem-label">The problem</p>
  <p class="cc-problem-h">A parking spot that works now may not <mark class="cc-mark">stay legal</mark> for your whole stay.</p>
  <p class="cc-about-t">Vancouver parking signs combine meter rates, time limits, and time-based
  restrictions. At our West Hastings demo location, the closest meter at 6:00 pm is still under
  a rush-hour no-stopping restriction until 7:00 pm.</p>
  <p class="cc-about-t" style="margin-top: 0.6rem;">This is not an isolated problem. Among
  196,909 Downtown tickets issued from January 2025 to June 2026, 59% were for expired meters,
  while 9,327—or 4.7%—were for rush-hour no stopping.</p></div>
  <div class="cc-who"><p class="cc-who-label">Who it's for</p>
  <ul class="cc-about-list">
    <li><strong>Drivers</strong> check a whole stay before they park.</li>
    <li><strong>City planners</strong> see where tickets concentrate, by street and infraction.</li>
  </ul></div>
</div>
""")

st.subheader("Team")
st.html('<div class="cc-team">' + "".join(member_card(m) for m in TEAM) + "</div>")

st.subheader("Organized by")
st.html(f"""
<div class="cc-orgs">
  <div class="cc-org"><p class="cc-name" style="margin-top:0;">Trilemma Foundation</p>
    <p class="cc-about-t">Datathon organizer and curator of the open data catalog we used.</p>
    <div class="cc-org-links">
      <a class="cc-link" href="{TRILEMMA_URL}" target="_blank" rel="noopener">trilemma.foundation ↗</a>
      <a class="cc-link" href="{DATATHON_URL}" target="_blank" rel="noopener">Datathon on GitHub ↗</a>
    </div></div>
  <div class="cc-org"><p class="cc-name" style="margin-top:0;">Northeastern University Vancouver</p>
    <p class="cc-about-t">Datathon partner in Vancouver.</p>
    <a class="cc-link" href="{NEU_VANCOUVER_URL}" target="_blank" rel="noopener">Northeastern Vancouver ↗</a></div>
</div>
""")

st.subheader("Project and data")
st.html(f"""
<div class="cc-project">
  <p class="cc-about-t">Data: City of Vancouver Open Data, via the Trilemma Foundation data
  catalog, licensed under the <a class="cc-link" href="{LICENCE_URL}" target="_blank"
  rel="noopener">Open Government Licence – Vancouver</a>. Map data © OpenStreetMap
  contributors.</p>
  <div class="cc-btns">
    <a class="cc-btn" href="{REPO_URL}" target="_blank" rel="noopener">{GITHUB_SVG}GitHub repository ↗</a>
    <a class="cc-btn" href="{VIDEO_URL}" target="_blank" rel="noopener">60-second demo ↗</a>
  </div>
</div>
""")
