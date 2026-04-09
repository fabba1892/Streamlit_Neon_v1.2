import streamlit as st
from service.styling import inject_sidebar_css

def render_sidebar(metrics):
    inject_sidebar_css()

    st.sidebar.markdown("## 🛜Network Ops AI")
    
    # 1. PULL METRICS
    oos = metrics.get("total_oos", 0)
    hubs = metrics.get("total_incidents", 0)
    total = metrics.get("total_alarms", 0)
    p_data = metrics.get("priorities", {})

    # 2. TOP STATS
    st.sidebar.markdown(f"""
        <div class="neon-box blue-edge">
            <div class="stat-row"><span>Sites OOS</span> <span class="stat-val">{oos}</span></div>
            <div class="stat-row"><span>Hub Impacts</span> <span class="stat-val" style="color:#ef4444;">{hubs}</span></div>
            <div class="stat-row"><span>Power Alarms</span> <span class="stat-val" style="color:#eab308;">0</span></div>
            <hr>
            <div class="stat-row"><span>P1 Critical</span> <span class="stat-val" style="color:#ef4444;">{p_data.get('P1', 0)}</span></div>
            <div class="stat-row"><span>P2 High</span> <span class="stat-val" style="color:#f97316;">{p_data.get('P2', 0)}</span></div>
            <div class="stat-row"><span>P3 Moderate</span> <span class="stat-val" style="color:#eab308;">{p_data.get('P3', 0)}</span></div>
            <div class="stat-row"><span>P4 Low</span> <span class="stat-val" style="color:#94a3b8;">{p_data.get('P4', 0)}</span></div>
            <div class="stat-row"><span>Total Alarms</span> <span class="stat-val">{total}</span></div>
        </div>
    """, unsafe_allow_html=True)

    # 3. RCA DISTRIBUTION
    rca_html = '<div class="neon-box blue-edge"><span class="filter-header">RCA Distribution</span>'
    for rca, count in metrics.get("top_rcas", []):
        rca_html += f'<div class="neon-rca-row"><span>{rca}</span><span class="neon-rca-badge">{count}</span></div>'
    rca_html += '</div>'
    st.sidebar.markdown(rca_html, unsafe_allow_html=True)

    # ... (Keep the Top Stats and RCA sections the same)

    # 4. INTELLIGENT FILTERS (Compact & Formatted)
    with st.sidebar.form("filter_panel"):
        st.markdown('<span class="filter-header">Intelligent Filters</span>', unsafe_allow_html=True)
        
        # Search Box
        st.session_state.search_query = st.text_input("Search", placeholder="Search RCA, ID, Hub...", label_visibility="collapsed")
        
        # Dropdowns acting as Placeholders (first item is the label)
        st.session_state.focus_filter = st.selectbox("Focus", ["All Incidents", "Hub Failures Only", "Link/Trans Only"], label_visibility="collapsed")
        
        dynamic_rca = ["Root Cause", "All"] + [rca[0] for rca in metrics.get("top_rcas", [])]
        st.session_state.rca_filter = st.selectbox("Root Cause", dynamic_rca, label_visibility="collapsed")
        
        st.session_state.county_filter = st.selectbox("County", ["County", "All"], label_visibility="collapsed")
        
        # Min Sites
        st.session_state.min_sites = st.number_input("Min Sites Impacted", min_value=0, step=1)
        
        # Side-by-Side Sort Buttons inside the form
        col1, col2 = st.columns(2)
        with col1:
            sort_rank_clicked = st.form_submit_button("Sort Rank", use_container_width=True)
        with col2:
            sort_time_clicked = st.form_submit_button("Sort Time", use_container_width=True)

        # Logic to catch which sort button was pressed
        if sort_rank_clicked: st.session_state.sort_type = 'rank'
        if sort_time_clicked: st.session_state.sort_type = 'time'

    # External Action Buttons (Outside form to clear easily)
    st.sidebar.button("Clear All Filters", type="primary", use_container_width=True)
    st.sidebar.button("Export CSV", use_container_width=True)

    # 5. DYNAMIC LAST SYNC TIMESTAMP
    sync_time = metrics.get("last_refresh", "Data Offline")
    st.sidebar.markdown(f'<div style="font-size:0.70rem; margin-top:20px; color:#94a3b8; text-align:center; font-weight: bold;">Last Sync: {sync_time}</div>', unsafe_allow_html=True)