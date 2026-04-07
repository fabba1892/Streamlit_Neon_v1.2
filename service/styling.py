import streamlit as st

def inject_sidebar_css():
    st.markdown("""
    <style>
        /* 1. Base Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
        }

        /* 2. Custom HTML Blocks (Stats & RCA) */
        .neon-box { 
            background: #1e293b; padding: 18px; border-radius: 10px; 
            margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }
        .neon-box.blue-edge { border-left: 5px solid #3b82f6; }
        
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9rem; color: #94a3b8; }
        .stat-val { font-weight: 700; color: #ffffff; }
        
        .neon-rca-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #334155; font-size: 0.85rem; color: #cbd5e1; }
        .neon-rca-badge { background: #3b82f6; color: white; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 0.75rem; }
        .filter-header { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; display: block; }

        /* 3. FORCING STREAMLIT NATIVE INPUTS TO MATCH TEMPLATE */
        /* Target the st.container(border=True) background */
        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }
        
        /* Make input boxes dark blue (#0f172a) like the template */
        [data-testid="stSidebar"] input, 
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #0f172a !important;
            border: 1px solid #334155 !important;
            color: #f1f5f9 !important;
            border-radius: 8px !important;
        }

        /* Adjust labels above inputs */
        [data-testid="stSidebar"] label p {
            color: #94a3b8 !important;
            font-size: 0.8rem !important;
        }
        
        hr { border-top: 1px solid #334155 !important; margin: 15px 0 !important; }
    </style>
    """, unsafe_allow_html=True)