import streamlit as st

# 1. PAGE CONFIG
st.set_page_config(page_title="Neon Ops Command", page_icon="🖥️", layout="wide", initial_sidebar_state="expanded")

# 2. INTERNAL IMPORTS
from engine.data_loader import load_phase1_data
from engine.aggregations import extract_sidebar_metrics, extract_regional_cards
from service.sidebar_service import render_sidebar
from service.main_view import render_top_cards

# NEW IMPORTS
from engine.grid_engine import filter_incidents
from service.grid_view import render_incident_grid

def main():
    # 3. INGESTION
    payload = load_phase1_data()

    # 4. METRIC EXTRACTION
    sidebar_metrics = extract_sidebar_metrics(payload)
    total_all, regional_cards = extract_regional_cards(payload)

    # 5. RENDER CONTROL PLANE
    render_sidebar(sidebar_metrics)
    render_top_cards(total_all, regional_cards)

    # 6. RUN THE FILTERING ENGINE
    # We pass the entire st.session_state dictionary to the engine
    filtered_incidents = filter_incidents(payload, st.session_state)

    # 7. RENDER EXECUTION PLANE
    render_incident_grid(filtered_incidents)

if __name__ == "__main__":
    main()