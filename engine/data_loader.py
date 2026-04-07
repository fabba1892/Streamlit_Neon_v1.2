import json
import os
import streamlit as st

@st.cache_data(ttl=300)  # Cache payload for 5 minutes to optimize performance
def load_phase1_data(filepath="data/Phase1result.txt"):
    """Safely loads the JSON payload with strict fault containment."""
    if not os.path.exists(filepath):
        st.error(f"🚨 CRITICAL FAULT: Payload missing at {filepath}. Halting render.")
        st.stop()
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        st.error("🚨 CRITICAL FAULT: Payload JSON is malformed or corrupted. Halting render.")
        st.stop()
    except Exception as e:
        st.error(f"🚨 UNKNOWN FAULT in Data Ingestion: {str(e)}")
        st.stop()