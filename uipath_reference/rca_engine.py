# rca_engine.py
def calculate_rca(clean_hub, rca_base, s_oos, site_alarms, global_diag_pwr):
    """
    Determines the Root Cause based on hub alarms and group alarm density.
    """
    # 1. Get alarms specifically for the Lead Hub
    hub_alarms = site_alarms.get(clean_hub, [])

    # 2. CRITICAL OVERRIDE: Check for specific high-priority power alarms
    has_critical_pwr_alarm = any(
        "device_powered_off" in str(a.get("Alarm", "")).lower() or 
        "power supply failed" in str(a.get("Summary", "")).lower() or 
        "rectifier system failed" in str(a.get("Summary", "")).lower() 
        for a in hub_alarms
    )

    if has_critical_pwr_alarm:
        return f"{rca_base} - Power"

    # 3. DENSITY CHECK: Check if the group as a whole is reporting power issues
    pwr_sites_in_group = s_oos.intersection(global_diag_pwr)
    
    # Calculate what % of OOS sites have power alarms
    pwr_ratio = len(pwr_sites_in_group) / len(s_oos) if s_oos else 0

    # If Hub has a generic power alarm OR more than 40% of sites have power alarms
    if (clean_hub in global_diag_pwr) or (pwr_ratio > 0.4):
        return f"{rca_base} - Power"
    
    # 4. DEFAULT: If no power indicators found, assume Transmission
    return f"{rca_base} - Transmission"