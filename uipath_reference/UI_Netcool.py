import json

def get_html(inc):
    oos_count = inc.get("OOS_Count", 0)
    hub = inc.get("Hub_Name", "Regional")
    reg = inc.get("_reg_key", "UNK")
    rca = inc.get("RCA", "Unknown")
    p_level = inc.get("MSDP_Priority", "P3")
    
    # 1. Process Site Rows and Alarms
    loc_rows = ""
    details = inc.get("OOS_Location_Details", {})
    sites_list = inc.get("OOS_Location_List", [])
    
    for loc_name in sites_list:
        site_info = details.get(loc_name, {})
        site_meta = site_info.get("metadata", {})
        alarms = site_info.get("alarms", [])
        
        # Defaults
        f_occ, l_occ = "—", "—"
        pwr, tmp, sec = "✅", "✅", "✅"
        
        if alarms:
            # Sort by Raw timestamp to find first and last
            sorted_alarms = sorted(alarms, key=lambda x: x.get("RawLastOccurrence", 0))
            
            # FIXED: Populate First and Last Occurrence with date/time
            f_occ = sorted_alarms[0].get("FirstOccurrence", "—")
            l_occ = sorted_alarms[-1].get("LastOccurrence", "—")
            
            # FIXED: Improved Keyword Matching for Status Icons
            all_text = " ".join([str(a.get("Summary", "")) + " " + str(a.get("Alarm", "")) for a in alarms]).upper()
            
            if any(k in all_text for k in ["POWER", "BATTERY", "RECTIFIER", "MAINS", "VOLT", "DC", "AC FAIL"]): 
                pwr = "⚠️"
            if "TEMP" in all_text: 
                tmp = "⚠️"
            if any(k in all_text for k in ["DOOR", "INTRUSION", "SMOKE", "FAN"]): 
                sec = "⚠️"

        loc_rows += f'''
        <tr>
            <td style="font-weight:700;">{loc_name}</td>
            <td>{site_meta.get("Site_Rank", "—")}</td>
            <td style="font-size:0.7rem;">{f_occ}</td>
            <td style="font-size:0.7rem; color:#64748b;">{l_occ}</td>
            <td>{pwr}</td>
            <td>{tmp}</td>
            <td>{sec}</td>
            <td>{"⭐" if site_meta.get("is_primary_hub") else "—"}</td>
        </tr>'''

    # 2. Return the Full HTML Block (This fixes the 'NoneType' error)
    return f'''
    <div class="incident">
        <div class="header" onclick="this.parentElement.classList.toggle('open')">
             <div style="display:flex; align-items:center; gap:10px; flex-grow:1;">
                <span class="p-tag {p_level}">{p_level}</span>
                <span style="font-weight:800;">{oos_count} Sites working from {hub} ({reg})</span>
                <span style="color:#94a3b8;">|</span>
                <span>RCA: <b>{rca}</b></span>
             </div>
        </div>
        <div class="details">
            <table class="diag-table" style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:#f8fafc; text-align:left; font-size:0.75rem;">
                        <th>Site Name</th><th>Rank</th><th>First Alarm</th><th>Last Alarm</th><th>PWR</th><th>TMP</th><th>SEC</th><th>HUB</th>
                    </tr>
                </thead>
                <tbody>{loc_rows}</tbody>
            </table>
        </div>
    </div>
    '''