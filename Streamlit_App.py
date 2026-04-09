import streamlit as st

# 1. PAGE CONFIG
st.set_page_config(page_title="Neon Ops Command", page_icon="🖥️", layout="wide", initial_sidebar_state="expanded")

# 2. INTERNAL IMPORTS
from engine.data_loader import load_phase1_data
from engine.aggregations import extract_sidebar_metrics, extract_regional_cards
from service.sidebar_service import render_sidebar
from service.main_view import render_top_cards

def main():
    # 3. INTELLIGENT INGESTION
    payload = load_phase1_data()

    # 4. DATA PROCESSING
    sidebar_metrics = extract_sidebar_metrics(payload)
    
    # Unpacking the new tuple from our data engine
    total_all, regional_cards = extract_regional_cards(payload)

    # 5. RENDER UI
    render_sidebar(sidebar_metrics)
    render_top_cards(total_all, regional_cards)

    # 6. INCIDENT GRID PLACEHOLDER
    st.info(f"🔍 Current Region Filter Applied: **{st.session_state.get('active_region', 'ALL')}**")
    st.success("✅ Top Cards Synchronized and Ordered. Awaiting command to construct the Incident Grid...")

if __name__ == "__main__":
    main()