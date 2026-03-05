import streamlit as st
import pandas as pd
from datetime import datetime

def inject_neon_theme():
    st.markdown("""
    <style>
        .neon-card {
            background: #1e1e2d; padding: 15px; border-radius: 8px;
            text-align: center; color: #ffffff; border-bottom: 4px solid #334155; margin-bottom: 15px;
        }
        .pulse-cyan { border-bottom-color: #00c8ff; }
        .pulse-orange { border-bottom-color: #f97316; animation: flash-orange 2s infinite; }
        .pulse-red { border-bottom-color: #ef4444; animation: flash-red 1.5s infinite; }
        
        @keyframes flash-red { 0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.6); } 70% { box-shadow: 0 0 0 10px rgba(239,68,68,0); } }
        @keyframes flash-orange { 0% { box-shadow: 0 0 0 0 rgba(249,115,22,0.5); } 70% { box-shadow: 0 0 0 8px rgba(249,115,22,0); } }

        .neon-title { color: #94a3b8; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px; }
        .neon-value { font-size: 2em; font-weight: bold; color: #ffffff; }

        [data-testid="stExpander"] { border: 1px solid #334155; border-radius: 4px; margin-bottom: 4px; background: #1e1e2d; }
        .stMarkdown p { font-size: 0.85rem; margin-bottom: 0px; }
        
        .diag-table { width: 100%; border-collapse: collapse; font-size: 0.75rem; margin-top: 8px; color: #e2e8f0; }
        .diag-table th { background: #334155; padding: 6px; border: 1px solid #475569; text-align: center; }
        .diag-table td { padding: 4px; border: 1px solid #475569; text-align: center; }
        
        .stats-container { background: #1e293b; padding: 15px; border-radius: 8px; margin-bottom: 20px; color: white; }
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9em; }
        .stat-val { font-weight: bold; color: #38bdf8; }
        .p-stat { color: #94a3b8; font-size: 0.8em; margin-top: 10px; border-top: 1px solid #334155; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar_stats(aggs):
    p1 = aggs.get('prio_counts', {}).get('P1', 0)
    p2 = aggs.get('prio_counts', {}).get('P2', 0)
    p3 = aggs.get('prio_counts', {}).get('P3', 0)
    p4 = aggs.get('prio_counts', {}).get('P4', 0)
    
    html = f"""
    <div class="stats-container">
        <div class="stat-row"><span>Total OOS Sites</span><span class="stat-val">{aggs.get('total_oos', 0)}</span></div>
        <div class="stat-row"><span>Power Failures</span><span class="stat-val">{aggs.get('total_pwr', 0)}</span></div>
        <div class="stat-row"><span>Hub Impacts</span><span class="stat-val">{aggs.get('total_hubs', 0)}</span></div>
        <div class="p-stat">
            <div class="stat-row"><span>P1 Priority</span><span style="color:#ef4444; font-weight:bold;">{p1}</span></div>
            <div class="stat-row"><span>P2 Priority</span><span style="color:#f97316; font-weight:bold;">{p2}</span></div>
            <div class="stat-row"><span>P3 Priority</span><span style="color:#eab308; font-weight:bold;">{p3}</span></div>
            <div class="stat-row"><span>P4 Priority</span><span style="color:#94a3b8; font-weight:bold;">{p4}</span></div>
        </div>
    </div>
    """
    st.sidebar.markdown(html, unsafe_allow_html=True)

def render_regional_kpis(regional_stats: dict):
    cols = st.columns(len(regional_stats))
    for idx, (reg, count) in enumerate(regional_stats.items()):
        p_class = "pulse-cyan" if count < 20 else "pulse-orange" if count < 50 else "pulse-red"
        cols[idx].markdown(f'''
            <div class="neon-card {p_class}">
                <div class="neon-title">{reg}</div>
                <div class="neon-value">{count}</div>
            </div>''', unsafe_allow_html=True)

def render_enhanced_accordion(inc, global_min):
    p_level = inc.get("MSDP_Priority", "P4")
    avg_rank = inc.get("Average_Rank", 0)
    try:
        time_str = datetime.fromtimestamp(inc.get("start_ts", 0)).strftime('%H:%M:%S')
    except:
        time_str = "00:00:00"

    header = f"🔴 {p_level} | {time_str} | {inc.get('Region', 'UNK')} | {inc.get('RCA', 'Unknown')} | {inc.get('Failure_Window', '')} (15m: {inc.get('Impact_15min_Count', 0)}) | [{inc.get('Hub_Name', 'None')}] | {inc.get('Failure_Probability', 'N/A')} Prob | RANK: {avg_rank}"
    
    with st.expander(header):
        st.markdown(f"**Counties:** `{inc.get('County_String', 'Unknown')}`")
        pwr = set(inc.get("Power_Location_List", [])) if isinstance(inc.get("Power_Location_List", []), list) else set()
        hubs = set(inc.get("Hub_Site_List", [])) if isinstance(inc.get("Hub_Site_List", []), list) else set()
        table_rows = "".join([f"<tr><td style='text-align:left;'>{s}</td><td>{'✔' if s in pwr else '-'}</td><td>-</td><td>-</td><td>{'✔' if s in hubs else '-'}</td></tr>" 
                             for s in inc.get("OOS_Location_List", [])])
        st.markdown(f'''<table class="diag-table"><thead><tr><th style="text-align:left;">Site</th><th>PWR</th><th>TX</th><th>RF</th><th>Hub</th></tr></thead>
                    <tbody>{table_rows}</tbody></table>''', unsafe_allow_html=True)
        tech = inc.get("Tech_Counts", {})
        if isinstance(tech, dict):
            tech_str = " | ".join([f"{k}: {v}" for k, v in tech.items() if v > 0])
            if tech_str: st.markdown(f"**Tech:** {tech_str}")