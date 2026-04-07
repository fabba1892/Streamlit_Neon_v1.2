import json
import html
from datetime import datetime
from collections import Counter
import UI_Netcool, UI_Downdetector, UI_Weather # Import the specialist modules

def get_key_case_insensitive(d, target_key, default_val=None):
    if not isinstance(d, dict): return default_val
    for k, v in d.items():
        if str(k).lower() == str(target_key).lower():
            return v
    return default_val

def generate_dashboard(phase1_json_output: str, template_content: str) -> str:
    try:
        raw_data = json.loads(phase1_json_output)
        data = raw_data.get("enriched_results", raw_data)
        reg_data = get_key_case_insensitive(data, "regional_data", {})
        
        all_incidents = []
        cards_html = ""
        total_oos, total_hubs, total_alarms, total_pwr_alarms = 0, 0, 0, 0
        newest_ts = 0
        p_stats = Counter({"P1": 0, "P2": 0, "P3": 0, "P4": 0})
        rca_stats = Counter()
        all_counties = set()

        for reg_key in sorted(reg_data.keys()):
            if reg_key.lower() in ["unknown", "metadata"]: continue
            info = reg_data[reg_key]
            reg_oos = get_key_case_insensitive(info, "Total_OOS_Count", 0)
            total_oos += reg_oos
            
            # Regional Weather Tiles (Static logic remains here)
            w_sum = get_key_case_insensitive(info, "Weather_Summary", {})
            reg_icon = get_key_case_insensitive(w_sum, "current_icon", "☀️")
            cards_html += f'''<div class="card" onclick="filterByRegion('{reg_key}')"><div style="font-size:1.2rem;">{reg_icon}</div><div style="font-size:0.75rem; font-weight:700;">{reg_key}</div><div class="val">{reg_oos}</div></div>'''

            incidents_list = get_key_case_insensitive(info, "Incidents", [])
            for inc in incidents_list:
                inc["_reg_key"] = reg_key
                all_incidents.append(inc)
                p_level = get_key_case_insensitive(inc, "MSDP_Priority", "P4")
                p_stats[p_level if p_level in p_stats else "P3"] += 1
                rca_stats[get_key_case_insensitive(inc, "RCA", "Unknown")] += 1
                for c in get_key_case_insensitive(inc, "County_List", []): all_counties.add(c)

        # --- INCIDENT FEED ROUTING ---
        list_html = '<h3 style="margin: 0 0 15px 5px; color:#1e293b;">Incident Intelligence Feed</h3>'
        all_incidents.sort(key=lambda x: get_key_case_insensitive(x, "Average_Rank", 99999))

        for inc in all_incidents:
            reg = inc.get("_reg_key", "UNK")
            hub_name = str(inc.get("Hub_Name", "")).upper()
            
            # ROUTER: Decide which module generates the HTML
            if reg == "DOWNDETECTOR":
                list_html += UI_Downdetector.get_html(inc)
            elif "FORECAST" in hub_name or "WEATHER ALERT" in hub_name:
                list_html += UI_Weather.get_html(inc)
            else:
                list_html += UI_Netcool.get_html(inc)

        # Final Assembly
        rca_list_html = "".join([f'<div class="stat-row"><span>{r}</span><span class="stat-val">{c}</span></div>' for r, c in rca_stats.most_common(5)])
        return (
            template_content.replace("##CARDS##", cards_html)
            .replace("##LIST##", list_html)
            .replace("##TOTAL_OOS##", str(total_oos))
            .replace("##P1_C##", str(p_stats['P1']))
            .replace("##P2_C##", str(p_stats['P2']))
            .replace("##RCA_LIST##", rca_list_html)
            .replace("##REFRESHED##", datetime.now().strftime('%H:%M:%S'))
        )
    except Exception as e:
        return f"Dashboard Error: {str(e)}"