import json
import time

REGION_MAP = {
    1013: "LIM", 1014: "MPU", 1015: "NGA", 1018: "SGC",
    1017: "SGS", 1008: "CEN", 1007: "EAS", 1005: "KZN", 1006: "WES"
}

def process_phase_1_dynamic(json_input):
    try:
        if isinstance(json_input, str):
            raw_data = json.loads(json_input)
        else:
            raw_data = json_input
            
        rows = raw_data.get("rowset", {}).get("rows", [])
        rows = [r for r in rows if isinstance(r, dict)]
        rows.sort(key=lambda x: x.get("LastOccurrence", 0))

        processed_windows = []
        current_oos, current_power, current_temp = set(), set(), set()
        window_start_ts = rows[0].get("LastOccurrence", 0) if rows else 0
        current_region_id = rows[0].get("RegionID") if rows else None
        
        OOS_THRESHOLD = 20
        MIN_WINDOW = 900 # 15 mins

        for row in rows:
            rid = row.get("RegionID")
            if rid not in REGION_MAP: continue
            
            ts = row.get("LastOccurrence", 0)
            loc = str(row.get("LocationName", "")).casefold()
            alert = str(row.get("AlertKey", "")).upper()
            elapsed = ts - window_start_ts
            
            # Check for window completion
            if (len(current_oos) >= OOS_THRESHOLD and elapsed >= MIN_WINDOW) or (elapsed >= 3600):
                if current_oos:
                    processed_windows.append({
                        "Window_Start": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(window_start_ts)),
                        "Region": REGION_MAP.get(current_region_id, "Unknown"),
                        "Duration_Mins": round(elapsed / 60, 2),
                        "OOS_Count": len(current_oos),
                        "Power_Count": len(current_power),
                        "Temp_Count": len(current_temp),
                        "Insight": "High Density Trigger" if len(current_oos) >= OOS_THRESHOLD else "Standard Window"
                    })
                current_oos, current_power, current_temp = set(), set(), set()
                window_start_ts = ts
                current_region_id = rid

            # Track unique locations per alert type
            if any(k in alert for k in ["UNAVAILABLE", "OUT_OF_SERVICE"]): current_oos.add(loc)
            if any(k in alert for k in ["MAINS", "RECTIFIER", "POWER"]): current_power.add(loc)
            if "TEMPERATURE" in alert: current_temp.add(loc)

        return json.dumps({
            "metadata": {"total_events": len(rows), "dynamic_windows": len(processed_windows)}, 
            "time_series_data": processed_windows
        })
    except Exception as e:
        return json.dumps({"error": f"Process Error: {str(e)}"})