import streamlit as st

def inject_sidebar_css():
    st.markdown("""
    <style>
        /* 1. Base Sidebar Styling */
        [data-testid="stSidebar"] { background-color: #0f172a !important; }

        /* Custom HTML Blocks (Stats & RCA) - COMPACTED */
        .neon-box { 
            background-color: #1e293b !important; 
            padding: 12px !important; /* Shrunk from 18px */
            border-radius: 8px !important; 
            margin-bottom: 12px !important; /* Shrunk from 20px */
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important;
        }
        .blue-edge { border-left: 5px solid #3b82f6 !important; }
        
        /* Shrunk the margin between rows and slightly reduced font size */
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 3px; font-size: 0.85rem; color: #94a3b8; }
        .stat-val { font-weight: 700; color: #ffffff; }
        
        .neon-rca-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid #334155; font-size: 0.80rem; color: #cbd5e1; }
        .neon-rca-badge { background-color: #3b82f6; color: white; padding: 2px 6px; border-radius: 10px; font-weight: bold; font-size: 0.70rem; }
        .filter-header { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700; margin-bottom: 8px; display: block; }
        
        /* Tighter horizontal lines */
        hr { border-top: 1px solid #334155 !important; margin: 8px 0 !important; }

        /* --- 3. THE FORM BYPASS FIX --- */
        /* This targets Streamlit's native form wrapper, which works on ALL versions */
        [data-testid="stSidebar"] [data-testid="stForm"] {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
            padding: 15px !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important;
        }

        /* Forces input fields inside the form to be dark */
        [data-testid="stSidebar"] [data-testid="stForm"] input, 
        [data-testid="stSidebar"] [data-testid="stForm"] div[data-baseweb="select"] > div {
            background-color: #0f172a !important;
            border: 1px solid #334155 !important;
            color: #f1f5f9 !important;
            border-radius: 6px !important;
        }

        /* Submit Button Styling inside the form */
        [data-testid="stSidebar"] [data-testid="stForm"] button {
            background-color: #3b82f6 !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            border-radius: 6px !important;
        }

        [data-testid="stSidebar"] label p { color: #94a3b8 !important; font-size: 0.8rem !important; }
        hr { border-top: 1px solid #334155 !important; margin: 15px 0 !important; }
                
        /* =========================================
           MAIN CANVAS & INTERACTIVE CARDS CSS
           ========================================= */
           
        /* 1. Paint the Main Dashboard Background Off-White */
        [data-testid="stAppViewContainer"] {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        [data-testid="stHeader"] {
            background-color: #f8fafc !important;
        }

        /* 2. Transform Streamlit Buttons into Compact Floating Cards */
        [data-testid="stAppViewContainer"] [data-testid="stButton"] button {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 8px 5px !important; /* TIGHTER PADDING */
            height: auto !important;
            min-height: 0 !important; /* REMOVES NATIVE HEIGHT RESTRICTIONS */
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
            transition: transform 0.2s, border-color 0.2s !important;
            width: 100% !important;
        }

        /* 3. Hover Effect */
        [data-testid="stAppViewContainer"] [data-testid="stButton"] button:hover {
            transform: translateY(-3px) !important;
            border-color: #3b82f6 !important;
            box-shadow: 0 8px 12px -3px rgba(0,0,0,0.1) !important;
        }

        /* 4. Formatting the Text inside the Button */
        [data-testid="stAppViewContainer"] [data-testid="stButton"] button p {
            font-size: 0.95rem !important;  /* SMALLER FONT */
            font-weight: 800 !important;
            margin: 0 !important;
            white-space: pre-wrap !important; 
            line-height: 1.2 !important; /* FORCES THE SECOND LINE TO SHOW */
            text-align: center !important;
        }

        /* 5. ACTIVE STATE (Primary Button = Light Red Indicator) */
        /* Targets the button type="primary" set by our main_view.py logic */
        [data-testid="stAppViewContainer"] [data-testid="stButton"] button[kind="primary"] {
             border: 2px solid #ef4444 !important; /* Solid Red Border */
             background-color: #fef2f2 !important; /* Light Red Background */
             color: #991b1b !important; /* Dark Red Text for high contrast */
        }
        [data-testid="stAppViewContainer"] [data-testid="stButton"] button[kind="primary"] p {
             color: #991b1b !important;
        }

        /* Sidebar Form Compact Fix */
        [data-testid="stSidebar"] [data-testid="stForm"] .stSelectbox { margin-bottom: -10px !important; }
    </style>
    """, unsafe_allow_html=True)