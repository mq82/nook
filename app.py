import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

import streamlit as st

from utils.styles import apply_global_styles, apply_mobile_styles

from pages_dashboard.dashboard import render_dashboard

from pages_home.chores import render_chores
from pages_home.meals import render_meals
from pages_home.fridge_inventory import render_fridge_inventory

from pages_personal.vera_supplements import render_vera_supplements
from pages_personal.pingping_plan import render_pingping_plan
from pages_personal.pingping_checkin import render_pingping_checkin

from pages_fermentation.kombucha import render_kombucha
from pages_fermentation.pickles import render_pickles
from pages_fermentation.yogurt import render_yogurt

from pages_ballet.ballet_tracker import render_ballet_tracker

from PIL import Image

app_icon = Image.open("static/nook-icon-512.png")

st.set_page_config(
    page_title="Nook",
    page_icon=app_icon,
    layout="wide"
)

apply_global_styles()
apply_mobile_styles()

st.title("🌿 Nook")
st.markdown(
    """
    <link rel="manifest" href="/app/static/manifest.json?v=3">
    <link rel="apple-touch-icon" href="/app/static/apple-touch-icon.png">
    <meta name="theme-color" content="#7a8f68">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="Nook">
    """,
    unsafe_allow_html=True
)

st.caption("A small personal system for home, health, fermentation, and ballet.")
st.image("static/apple-touch-icon.png", width=120)

# -------- 1st level tabs --------
main_tab = st.tabs([
    "📊 Dashboard",
    "🏠 Home",
    "💊 Personal Daily",
    "🫙 Fermentation",
    "🩰 Ballet"
])


# -------- DASHBOARD --------
with main_tab[0]:
    render_dashboard()

with main_tab[1]:
    home_page = st.segmented_control(
        "Choose Section",
        ["Chores", "Meals", "Fridge Inventory"],
        default = "Chores"
    )

    if home_page == "Chores":
        render_chores()
    elif home_page == "Meals":
        render_meals()
    elif home_page == "Fridge Inventory":
        render_fridge_inventory()

# -------- PERSONAL DAILY --------
with main_tab[2]:
    personal_page = st.segmented_control(
        "Choose Section",
        [
            "Vera Supplements",
            "Pingping Supplements",
            "Pingping Daily Check"
        ],
        default = "Vera Supplements"
    )

    if personal_page == "Vera Supplements":
        render_vera_supplements()
    elif personal_page == "Pingping Supplements":
        render_pingping_plan()
    elif personal_page == "Pingping Daily Check":
        render_pingping_checkin()

# -------- FERMENTATION --------
with main_tab[3]:
    fermentation_page = st.segmented_control(
        "Choose Section",
        [
            "Kombucha",
            "Pickles",
            "Yogurt"
        ],
        default = "Kombucha"
    )

    if fermentation_page == "Kombucha":
        render_kombucha()
    elif fermentation_page == "Pickles":
        render_pickles()
    elif fermentation_page == "Yogurt":
        render_yogurt()

# -------- BALLET --------
with main_tab[4]:
    render_ballet_tracker()
