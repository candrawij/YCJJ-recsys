import streamlit as st
import sys
import os

# Set global page configuration
st.set_page_config(
    page_title="YuruCamp Data Science — Smart Camping Hub",
    page_icon="🏕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tambahkan direktori modul ke sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
mod1_dir = os.path.join(root_dir, "01_camp_area_recommender")
mod2_dir = os.path.join(root_dir, "02_gear_recommender")
mod3_dir = os.path.join(root_dir, "03_integrated_approach")

for d in [root_dir, mod1_dir, mod2_dir, mod3_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from app_camp import render_camp_app
from app_gear import render_gear_app
from app_integrated import render_integrated_app

def main():
    # Sidebar Navigation
    st.sidebar.title("🏕️ YuruCamp DS Hub")
    st.sidebar.markdown("**Pilih Pendekatan Interaktif:**")

    menu = st.sidebar.radio(
        "Menu Navigasi:",
        [
            "🏕️ 1. Rekomendasi Tempat Kemah",
            "🎒 2. Rekomendasi Pembelian Gear",
            "🔗 3. Smart Camping Planner Terpadu"
        ],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Info Proyek Data Science:**\n"
        "• Data Spot Camp: 57 Destinasi (Jogja-Jateng)\n"
        "• Data Gear: 49 Item Katalog Outdoor\n"
        "• Model: K-Means Clustering + Knapsack Optimizer + Content-Based Heuristic"
    )

    if menu == "🏕️ 1. Rekomendasi Tempat Kemah":
        render_camp_app()
    elif menu == "🎒 2. Rekomendasi Pembelian Gear":
        render_gear_app()
    elif menu == "🔗 3. Smart Camping Planner Terpadu":
        render_integrated_app()

if __name__ == "__main__":
    main()
