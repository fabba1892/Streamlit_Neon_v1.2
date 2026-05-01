import streamlit as st

import streamlit as st

# --- MODAL POPUP LOGIC ---
@st.dialog("🚨 Site Alarm Diagnostics", width="large")
def render_alarm_modal(site_name, site_data):
    """Renders the detailed alarm table when a specific site is clicked."""
    st.markdown(f"### **{site_name}**")
    
    meta = site_data.get("metadata", {})
    alarms = site_data.get("alarms", [])
    
    # Quick Stats Row
    cols = st.columns(4)
    cols[0].metric("Site Rank", meta.get("Site_Rank", "N/A"))
    cols[1].metric("RAN Risk", meta.get("RAN_Risk_Count", 0))
    cols[2].metric("RAN Failed", meta.get("RAN_Failed_Count", 0))
    cols[3].metric("Total Alarms", len(alarms))
    
    st.markdown("---")
    
    if not alarms:
        st.success("No active critical alarms detected for this specific location within the time window.")
        return

    # THE FIX: Absolute zero-indentation string building to prevent Markdown Code Blocks
    table_html = "<style>"
    table_html += ".modal-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; color: #f1f5f9; }"
    table_html += ".modal-table th { background-color: #1e293b; padding: 10px; text-align: left; border-bottom: 2px solid #334155; color: #94a3b8; }"
    table_html += ".modal-table td { padding: 10px; border-bottom: 1px solid #1e293b; }"
    table_html += ".sev-5 { color: #ef4444; font-weight: bold; }"
    table_html += ".sev-4 { color: #f97316; font-weight: bold; }"
    table_html += ".sev-3 { color: #eab308; font-weight: bold; }"
    table_html += "</style>"
    
    table_html += "<table class='modal-table'>"
    table_html += "<thead><tr><th>Severity</th><th>Alarm Type</th><th>Summary ID</th><th>Last Occurrence</th></tr></thead><tbody>"
    
    for a in alarms:
        sev = a.get("Severity", 0)
        sev_class = "sev-5" if sev == 5 else "sev-4" if sev == 4 else "sev-3" if sev == 3 else ""
        
        # Single-line HTML injection
        table_html += f"<tr><td class='{sev_class}'>Level {sev}</td><td>{a.get('Alarm', 'Unknown')}</td><td>{a.get('Summary', 'N/A')}</td><td>{a.get('LastOccurrence', 'N/A')}</td></tr>"
        
    table_html += "</tbody></table>"
    
    # Push to UI safely
    st.markdown(table_html, unsafe_allow_html=True)

# --- MAIN GRID RENDERER ---
# (Keep your existing render_incident_grid code below here)

# --- MAIN GRID RENDERER ---
def render_incident_grid(filtered_incidents):
    """Renders the tactical expandable grid for all filtered incidents."""
    
    # 1. SOFT DIVIDER
    st.markdown("""
        <div style="margin-top: 40px; margin-bottom: 25px;">
            <hr style="border: 0; height: 1px; background: linear-gradient(to right, rgba(15,23,42,0), rgba(148,163,184,0.6), rgba(15,23,42,0));">
            <div style="text-align: center; margin-top: -12px;">
                <span style="background: #f8fafc; padding: 0 15px; color: #64748b; font-size: 0.80rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;">
                    Tactical Incident Grid
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not filtered_incidents:
        st.info("✅ System Active: No incidents match your current filters.")
        return

    # 2. COLUMN HEADERS (Visual only)
    cols = st.columns([1, 3, 2, 4, 1, 1])
    headers = ["Priority", "Hub Impact", "County", "Root Cause", "OOS", "Avg Rank"]
    for i, h in enumerate(headers):
        cols[i].markdown(f"**<span style='color: #64748b; font-size: 0.8rem; text-transform: uppercase;'>{h}</span>**", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #e2e8f0; margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)

    # 3. RENDER THE EXPANDABLE ROWS
    for idx, inc in enumerate(filtered_incidents):
        pri = inc.get("MSDP_Priority", "P4")
        hub = inc.get("Hub_Name", "Unknown Hub")
        counties = ", ".join(inc.get("County_List", []))
        rca = inc.get("RCA", "Unknown RCA")
        oos_count = inc.get("OOS_Count", 0)
        
        # Formatting Rank for clean display
        raw_rank = inc.get("Average_Rank", 0)
        rank_str = f"{float(raw_rank):.1f}" if float(raw_rank) > 0 else "N/A"

        # Color-coding the Priority tag based on our design system
        pri_color = "#ef4444" if pri == "P1" else "#f97316" if pri == "P2" else "#eab308" if pri == "P3" else "#64748b"
        
        # Special catch for Weather icons (which come through as priority text sometimes)
        if pri not in ["P1", "P2", "P3", "P4"]:
            pri_tag = f"<span style='font-size: 1.2rem;'>{pri}</span>"
        else:
            pri_tag = f"<span style='background: {pri_color}; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 0.75rem;'>{pri}</span>"

        # Streamlit Expander acts as the "Row"
        with st.expander(f"{hub} | {oos_count} Sites OOS"):
            
            # Re-draw the row data neatly inside the top of the expander
            r_cols = st.columns([1, 3, 2, 4, 1, 1])
            r_cols[0].markdown(pri_tag, unsafe_allow_html=True)
            r_cols[1].markdown(f"**{hub}**")
            r_cols[2].markdown(f"<span style='color:#64748b; font-size:0.9rem;'>{counties}</span>", unsafe_allow_html=True)
            r_cols[3].markdown(f"**{rca}**")
            r_cols[4].markdown(f"<span style='color:#ef4444; font-weight:bold;'>{oos_count}</span>", unsafe_allow_html=True)
            r_cols[5].markdown(f"<span style='color:#64748b; font-size:0.9rem;'>{rank_str}</span>", unsafe_allow_html=True)
            
            st.markdown("---")

            # 4. THE NESTED SITES (Clickable Buttons that trigger the Modal)
            # 4. THE NESTED SITES (Compact Horizontal Grid)
            # 4. THE NESTED SITES (Compact Vertical Stack)
            loc_list = inc.get("OOS_Location_List", [])
            loc_details = inc.get("OOS_Location_Details", {})
            
            if not loc_list:
                st.info("No specific site locations detailed for this incident.")
                continue
                
            st.markdown("##### 📍 Impacted Sites (Click for Diagnostics)")
            
            # We use a 1-to-3 column ratio so the buttons only take up the left 25% of the screen
            # This keeps the vertical stack neat and readable.
            col_sites, _ = st.columns([1, 3]) 
            
            with col_sites:
                for s_idx, site in enumerate(loc_list):
                    btn_key = f"btn_{idx}_{site}"
                    if st.button(site, key=btn_key, use_container_width=True):
                        render_alarm_modal(site, loc_details.get(site, {}))