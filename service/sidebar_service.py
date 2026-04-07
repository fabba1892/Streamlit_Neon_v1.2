import streamlit as st
from service.styling import inject_sidebar_css

def render_sidebar(metrics):
    """Renders the styled Neon Command Sidebar."""
    # 1. Fire the CSS Engine
    inject_sidebar_css()

    st.sidebar.markdown("### 🔍 Filters")
    
    # 2. Native Inputs (Styled automatically by config.toml)
    if 'search_query' not in st.session_state: st.session_state.search_query = ""
    if 'min_sites' not in st.session_state: st.session_state.min_sites = 0
    if 'region_filter' not in st.session_state: st.session_state.region_filter = "All"

    st.session_state.search_query = st.sidebar.text_input("Search (Hub/County/RCA)", value=st.session_state.search_query)
    st.session_state.min_sites = st.sidebar.slider("Min Sites OOS", 0, 50, st.session_state.min_sites)
    
    # Emulating the dual dropdown from the screenshot
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.session_state.region_filter = st.selectbox("Region", ["All", "EAS", "SGS", "WES", "CEN", "KZN"], index=0)
    with col2:
        st.selectbox("County", ["All"], index=0) # Placeholder for dynamic county linking later

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # 3. HTML Injected Metrics (Matching the Screenshot perfectly)
    st.sidebar.markdown("### 📊 Network State")
    
    oos = metrics.get("total_oos", 0)
    incidents = metrics.get("total_incidents", 0)
    
    st.sidebar.markdown(f"""
        <div class="neon-metric-row"><span class="neon-metric-label">OOS Sites</span><span class="val-red">{oos}</span></div>
        <div class="neon-metric-row"><span class="neon-metric-label">Hub Impacts</span><span class="val-yellow">{incidents}</span></div>
        <div class="neon-metric-row"><span class="neon-metric-label">PWR Alarms</span><span class="val-orange">0</span></div>
        <div class="neon-metric-row"><span class="neon-metric-label">Newest Alarm</span><span class="val-white">N/A</span></div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # 4. Priority Breakdown
    st.sidebar.markdown("### 🚨 Priority Levels")
    pri_data = metrics.get("priorities", {})
    p1 = pri_data.get("P1", 0)
    p2 = pri_data.get("P2", 0)
    p3 = pri_data.get("P3", 0)
    p4 = pri_data.get("P4", 0)

    st.sidebar.markdown(f"""
        <div class="neon-pri-row"><span class="pri-p1">P1 - Critical</span><span class="pri-val">{p1}</span></div>
        <div class="neon-pri-row"><span class="pri-p2">P2 - High</span><span class="pri-val">{p2}</span></div>
        <div class="neon-pri-row"><span class="pri-p3">P3 - Medium</span><span class="pri-val">{p3}</span></div>
        <div class="neon-pri-row"><span class="pri-p4">P4 - Low / Weather</span><span class="pri-val">{p4}</span></div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # 5. RCA Distribution
    st.sidebar.markdown("### 🔍 RCA Distribution")
    rca_data = metrics.get("top_rcas", [])
    
    rca_html = ""
    for rca, count in rca_data:
        rca_html += f'<div class="neon-rca-row"><span>{rca}</span><span class="neon-rca-badge">{count}</span></div>'
    
    if not rca_html:
        rca_html = '<div class="neon-rca-row"><span>No Data</span></div>'
        
    st.sidebar.markdown(rca_html, unsafe_allow_html=True)