import streamlit as st
from data_engine import load_and_prepare_neon_data, apply_tactical_filters, get_sidebar_aggregates
from ui_components import inject_neon_theme, render_regional_kpis, render_enhanced_accordion, render_sidebar_stats

st.set_page_config(page_title="Neon Ops", layout="wide", initial_sidebar_state="expanded")
inject_neon_theme()

with st.sidebar:
    st.title("🛡️ MSDP MONITOR")
    uploaded_file = st.file_uploader("Ingest Phase 1 JSON", type=['json', 'txt'])
    
    if uploaded_file:
        raw = uploaded_file.getvalue().decode("utf-8")
        meta, stats, df = load_and_prepare_neon_data(raw)
        global_min = meta.get("min_avg_rank", 0)
        aggs = get_sidebar_aggregates(df, stats)
        render_sidebar_stats(aggs)

    st.markdown("---")
    selected_regions = st.multiselect("Regions", ["KZN", "WES", "CEN", "EAS", "LIM", "MPU", "NGA", "SGS", "SGC"], default=["KZN", "EAS", "LIM"])
    min_priority = st.select_slider("Max Priority", options=["P1", "P2", "P3", "P4", "P5"], value="P4")

st.title("🖥️ Ops Command Center")
if uploaded_file:
    render_regional_kpis(stats)
    st.markdown("---")
    filtered_df = apply_tactical_filters(df, selected_regions, min_priority)
    for _, row in filtered_df.iterrows():
        render_enhanced_accordion(row, global_min)
else:
    st.info("System Standby. Upload data in Sidebar.")