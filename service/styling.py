import streamlit as st

def inject_sidebar_css():
    """Injects custom HTML classes to perfectly mimic the static HTML template."""
    st.markdown("""
    <style>
    /* 1. Global Sidebar Adjustments */
    [data-testid="stSidebar"] {
        border-right: 1px solid #1e293b;
    }
    
    /* 2. Metric Containers (OOS Sites, Hubs, etc) */
    .neon-metric-row {
        display: flex; justify-content: space-between; align-items: center;
        background: #1e293b; padding: 12px 15px; border-radius: 8px; margin-bottom: 8px;
    }
    .neon-metric-label { color: #94a3b8; font-weight: 600; font-size: 0.95rem; }
    .val-red { color: #ef4444; font-weight: 800; font-size: 1.2rem; }
    .val-yellow { color: #eab308; font-weight: 800; font-size: 1.2rem; }
    .val-orange { color: #f97316; font-weight: 800; font-size: 1.2rem; }
    .val-white { color: #ffffff; font-weight: 800; font-size: 1.2rem; }

    /* 3. Priority Breakdown List */
    .neon-pri-row {
        display: flex; justify-content: space-between;
        padding: 8px 0; border-bottom: 1px solid #334155;
        font-size: 0.95rem; font-weight: 600;
    }
    .pri-p1 { color: #ef4444; }
    .pri-p2 { color: #f97316; }
    .pri-p3 { color: #eab308; }
    .pri-p4 { color: #94a3b8; }
    .pri-val { color: #f8fafc; font-weight: 700; }

    /* 4. RCA Distribution List */
    .neon-rca-row {
        display: flex; justify-content: space-between; align-items: center;
        background: #1e293b; padding: 10px; border-radius: 6px; margin-bottom: 6px;
        font-size: 0.85rem; color: #cbd5e1; font-weight: 500;
    }
    .neon-rca-badge {
        background: #3b82f6; color: white; padding: 2px 8px; 
        border-radius: 12px; font-weight: bold; font-size: 0.75rem;
    }
    </style>
    """, unsafe_allow_html=True)