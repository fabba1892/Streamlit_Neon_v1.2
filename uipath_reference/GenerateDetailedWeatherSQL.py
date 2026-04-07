import json
import os

def generate_all_incidents_sql(phase1_path):
    # 1. Load the Phase 1 Results
    if not os.path.exists(phase1_path):
        return "-- Error: Phase1result.txt not found."
        
    try:
        with open(phase1_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return f"-- Error parsing JSON: {str(e)}"

    # 2. Extract ALL unique Site Names
    all_failed_sites = set()
    regional_data = data.get("regional_data", {})

    def clean_site_name(name):
        if not name or not isinstance(name, str):
            return None
            
        # Strip out emojis and forecast alert strings
        if any(char in name for char in ["💨", "🚨", "⚠️", "🚩"]):
            return None
        if "WEATHER ALERT" in name.upper():
            return None
            
        # Handle names like "VODACOM: 148 Reports"
        clean_name = name.split(":")[0].upper().strip()
        
        # Filter generic non-sites
        if clean_name in ["UNKNOWN", "NATIONAL", "NONE", "INCIDENTS", "VODACOM", "MTN"]:
            return None
            
        return clean_name

    for region_name, region_info in regional_data.items():
        if region_name.upper() == "DOWNDETECTOR":
            continue
            
        incidents = region_info.get("Incidents", [])
        for inc in incidents:
            hub = clean_site_name(inc.get("Hub_Name"))
            if hub: all_failed_sites.add(hub)
            
            loc_list = inc.get("OOS_Location_List", [])
            for site in loc_list:
                cleaned = clean_site_name(site)
                if cleaned: all_failed_sites.add(cleaned)
                
            loc_details = inc.get("OOS_Location_Details", {})
            for site_key in loc_details.keys():
                cleaned = clean_site_name(site_key)
                if cleaned: all_failed_sites.add(cleaned)

    if not all_failed_sites:
        return "-- No valid incident sites found to query."

    # 3. Format the site list for the SQL IN clause
    formatted_sites = ",\n        ".join([f"'{s}'" for s in sorted(list(all_failed_sites))])

    # 4. Final SQL Construction 
    # STRICT RULE FOR UIPATH: NO SEMICOLON AT THE VERY END
    sql_query = f"""SELECT 
    TO_CHAR(w.DATETIME, 'YYYY-MM-DD HH24:MI:SS') AS DATETIME_FULL,
    g.REGION,
    g.REGION || '_' || g.COUNTY AS COUNTY_ID, 
    g.ATOLL_SITE_NAME, 
    g.LATITUDE, 
    g.LONGITUDE,
    w.MAX_WIND_GUSTS_10M,   
    w.SUM_RAIN,             
    w.MAX_TEMPERATURE_2M,   
    w.WEATHER_CODE
FROM npm_rpt.GEN_ATOLL_LAST_STATUS g
INNER JOIN sonar_usr.weather_data_site_hr w
    ON ROUND(g.LATITUDE, 1) = w.LATITUDE 
    AND ROUND(g.LONGITUDE, 1) = w.LONGITUDE
WHERE 
    UPPER(g.ATOLL_SITE_NAME) IN (
        {formatted_sites}
    )
    AND w.DATETIME >= TRUNC(SYSDATE, 'HH24') - INTERVAL '4' HOUR
    AND w.DATETIME <= SYSDATE
ORDER BY 
    w.DATETIME DESC, 
    g.ATOLL_SITE_NAME ASC"""

    return sql_query