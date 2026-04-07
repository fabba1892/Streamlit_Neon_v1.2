import streamlit as st

# 1. PAGE CONFIG (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Neon Ops Command", 
    page_icon="🖥️", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. INTERNAL IMPORTS (Decoupled Architecture)
from engine.data_loader import load_phase1_data
from engine.aggregations import extract_sidebar_metrics
from service.sidebar_service import render_sidebar

def main():
    # 3. INTELLIGENT INGESTION
    payload = load_phase1_data()

    # 4. DATA PROCESSING
    sidebar_metrics = extract_sidebar_metrics(payload)

    # 5. RENDER UI
    render_sidebar(sidebar_metrics)

    # --- TEMPORARY MAIN CANVAS ---
    st.title("NEON OPS COMMAND CENTER")
    st.markdown("### 📡 Main Network View")
    st.success("✅ Architecture Validated: Sidebar successfully decoupled and rendered.")
    st.info("Awaiting command to construct Top Cards and Region Grids...")

if __name__ == "__main__":
    main()