import streamlit as st
from service.styling import inject_sidebar_css

def render_sidebar(metrics):
    inject_sidebar_css()

    st.sidebar.markdown("## Network Ops AI")
    
    # 1. PULL RECALCULATED METRICS
    oos = metrics.get("total_oos", 0)
    hubs = metrics.get("total_incidents", 0)
    total = metrics.get("total_alarms", 0)
    p_data = metrics.get("priorities", {})

    # 2. RENDER TOP STATS (HTML injected to get exact layout and colors)
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

    # 3. RENDER RCA DISTRIBUTION (HTML injected)
    rca_html = '<div class="neon-box"><span class="filter-header">RCA Distribution</span>'
    for rca, count in metrics.get("top_rcas", []):
        rca_html += f'<div class="neon-rca-row"><span>{rca}</span><span class="neon-rca-badge">{count}</span></div>'
    rca_html += '</div>'
    st.sidebar.markdown(rca_html, unsafe_allow_html=True)

    # 4. STREAMLIT NATIVE FILTERS (Wrapped in a shaded container via CSS)
    st.sidebar.markdown('<span class="filter-header" style="margin-left: 5px;">Intelligent Filters</span>', unsafe_allow_html=True)
    
    # st.sidebar.container(border=True) creates the shaded background box!
    with st.sidebar.container(border=True):
        st.session_state.search_query = st.text_input("Search RCA, ID, Hub...", placeholder="Search...")
        
        st.session_state.focus_filter = st.selectbox(
            "Focus", 
            ["All Incidents", "Hub Failures Only", "Link/Trans Only"]
        )
        
        dynamic_rca = ["All"] + [rca[0] for rca in metrics.get("top_rcas", [])]
        st.session_state.rca_filter = st.selectbox("Root Cause", dynamic_rca)
        
        st.session_state.county_filter = st.selectbox("County", ["All"])
        
        st.session_state.min_sites = st.number_input("Min Sites Impacted", min_value=0, step=1)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Sort Rank", use_container_width=True)
        with col2:
            st.button("Sort Time", use_container_width=True)
            
        st.button("Clear All Filters", type="primary", use_container_width=True)

    st.sidebar.markdown('<div style="font-size:0.65rem; margin-top:20px; color:#64748b; text-align:center;">Last Sync: Live Engine</div>', unsafe_allow_html=True)