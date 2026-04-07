import json
import os
import time
from datetime import datetime

def get_weather_icon(code, wind, rain):
    try:
        w, r = float(wind), float(rain)
        c = int(code) if code else 0
        if c in [95, 96, 99, 65, 82]: return "⛈️"
        if r > 10.0 or c in [61, 63, 80, 81]: return "🌧️"
        if w > 60.0: return "🌪️"
        if w > 40.0: return "💨"
        return "☀️"
    except: return "☀️"

def get_impact_description(wind, rain):
    impacts = []
    w, r = float(wind), float(rain)
    if w > 65: impacts.append("High risk of antenna misalignment/structural damage")
    elif w > 45: impacts.append("Potential for wind-blown debris/intermittent link fades")
    if r > 15: impacts.append("Heavy rain: Potential for microwave rain-fade/flooding")
    return " | ".join(impacts) if impacts else "Monitor for site stability"

def process_weather_and_enrich(phase1_filepath, raw_weather_db_json):
    try:
        if not os.path.exists(phase1_filepath):
            return json.dumps({"error": f"File not found: {phase1_filepath}"})
        with open(phase1_filepath, 'r', encoding='utf-8') as f:
            phase1_data = json.load(f)
            
        db_rows = json.loads(raw_weather_db_json)
        weather_map = {} 

        for row in db_rows:
            reg = str(row.get("REGION", "UNK")).upper()
            raw_c_id = str(row.get("COUNTY_ID", "UNK"))
            dtype = str(row.get("DATA_TYPE", "CURRENT")).upper()
            dt_str = row.get("DATETIME_FULL") 
            
            clean_county = raw_c_id.split('_', 1)[-1] if '_' in raw_c_id else raw_c_id
            
            if clean_county.lower() == "winelands" and reg != "WES":
                continue

            if reg not in weather_map: weather_map[reg] = {}
            if clean_county not in weather_map[reg]: weather_map[reg][clean_county] = {}

            w_val, r_val = row.get('MAX_WIND_GUSTS_10M', 0) or 0, row.get('SUM_RAIN', 0) or 0
            threat = "High" if (float(w_val) > 65 or float(r_val) > 15) else "Medium" if (float(w_val) > 40 or float(r_val) > 5) else "Low"
            
            try:
                dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                unix_ts = int(time.mktime(dt_obj.timetuple()))
            except:
                unix_ts = int(time.time())

            metrics = {
                "icon": get_weather_icon(row.get('WEATHER_CODE'), w_val, r_val),
                "wind": f"{float(w_val):.1f}km/h",
                "rain": f"{float(r_val):.1f}mm",
                "temp": f"{float(row.get('MAX_TEMPERATURE_2M', 0) or 0):.1f}°C",
                "threat_level": threat,
                "impact": get_impact_description(w_val, r_val),
                "timestamp": unix_ts
            }
            key = "current" if "CURRENT" in dtype else "forecast_8h"
            weather_map[reg][clean_county][key] = metrics

        regional_data = phase1_data.get("regional_data", {})
        
        for reg_name, reg_obj in regional_data.items():
            reg_key = reg_name.upper()
            reg_weather = weather_map.get(reg_key, {})
            
            max_wind, top_icon = 0.0, "☀️"
            for c_info in reg_weather.values():
                curr_w = float(c_info.get("current", {}).get("wind", "0").replace("km/h", ""))
                if curr_w > max_wind:
                    max_wind, top_icon = curr_w, c_info.get("current", {}).get("icon", "☀️")
            
            reg_obj["Weather_Summary"] = {
                "current_icon": top_icon,
                "current_condition": f"Peak Wind: {max_wind:.1f}km/h",
                "warning_text": "⚠️ Severe Weather Active" if max_wind > 45 else ""
            }

            for inc in reg_obj.get("Incidents", []):
                for c_name in inc.get("County_List", []):
                    clean_c = c_name.split('_')[-1]
                    found = reg_weather.get(clean_c) or reg_weather.get(c_name)
                    if found:
                        inc["Weather"] = found
                        break

            for c_name, c_data in reg_weather.items():
                curr, fcst = c_data.get("current", {}), c_data.get("forecast_8h", {})
                
                target, label, alert_type = (None, "", "")
                if curr.get("threat_level") in ["High", "Medium"]:
                    target, label, alert_type = curr, "CURRENT", "CURRENT WEATHER ALERT"
                elif fcst.get("threat_level") in ["High", "Medium"]:
                    target, label, alert_type = fcst, "8H FORECAST", "FORECAST 8H WEATHER ALERT"

                if target:
                    priority_val = "P2" if target["threat_level"] == "High" else "P3"
                    # REPLACING P2/P3 with the dynamic icon for the dashboard display
                    display_icon = target.get("icon", "⚠️")
                    
                    reg_obj["Incidents"].append({
                        "start_ts": target.get("timestamp"),
                        "Region": reg_name,
                        "Hub_Name": f"{display_icon} {alert_type}: {c_name}", 
                        "County_List": [c_name],
                        "OOS_Count": 0,
                        "MSDP_Priority": display_icon, # Priority replaced by Icon
                        "Average_Rank": 1200 if priority_val == "P2" else 2600,
                        "RCA": f"Weather ({label}): {target['wind']}, {target['rain']}. {target['impact']}",
                        "Weather": c_data
                    })

        return json.dumps({"enriched_results": phase1_data, "weather_only": weather_map})

    except Exception as e:
        return json.dumps({"error": str(e)})