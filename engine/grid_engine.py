def filter_incidents(payload, session_state):
    """Filters raw JSON incidents based on all active UI parameters."""
    if not payload or "regional_data" not in payload:
        return []

    reg_data = payload.get("regional_data", {})
    raw_incidents = []

    # 1. REGION FILTERING (Triggered by clicking the Top Cards)
    active_region = session_state.get("active_region", "ALL")
    if active_region == "ALL":
        for r_info in reg_data.values():
            raw_incidents.extend(r_info.get("Incidents", []))
    else:
        raw_incidents.extend(reg_data.get(active_region, {}).get("Incidents", []))

    # 2. EXTRACT SIDEBAR STATE
    search_q = session_state.get("search_query", "").lower()
    focus = session_state.get("focus_filter", "All Incidents")
    rca_f = session_state.get("rca_filter", "All")
    county_f = session_state.get("county_filter", "All")
    min_s = session_state.get("min_sites", 0)
    sort_t = session_state.get("sort_type", "Rank (Highest Impact)")

    filtered_incidents = []

    # 3. THE GAUNTLET (Apply Sidebar Filters)
    for inc in raw_incidents:
        # A. Search (Checks Hub Name, RCA, and Counties)
        if search_q:
            target = f"{inc.get('Hub_Name','')} {inc.get('RCA','')} {' '.join(inc.get('County_List',[]))}".lower()
            if search_q not in target:
                continue
                
        # B. Focus Filter
        rca_lower = str(inc.get("RCA", "")).lower()
        if focus == "Hub Failures Only" and "hubsite" not in rca_lower:
            continue
        if focus == "Link/Trans Only" and "transmission" not in rca_lower and "link" not in rca_lower:
            continue
            
        # C. RCA Dropdown
        if rca_f not in ["All", "Root Cause"]:
            clean_rca = str(inc.get("RCA", "")).split(":")[0].split("-")[0].strip()
            if clean_rca != rca_f:
                continue
                
        # D. County Dropdown
        if county_f not in ["All", "County"]:
            if county_f not in inc.get("County_List", []):
                continue
                
        # E. Min Sites Impacted
        if int(inc.get("OOS_Count", 0)) < min_s:
            continue
            
        filtered_incidents.append(inc)

    # 4. GAMIFICATION & 5-TIER PINNING ALGORITHM
    def strict_sort_key(inc):
        hub = str(inc.get("Hub_Name", "")).upper()
        rca = str(inc.get("RCA", "")).upper()
        
        # --- TIER EVALUATION ---
        pin_score = 4 # Default tier for standard incidents
        
        if "WEATHER" in rca and "CURRENT" in rca:
            pin_score = 0
        elif "WEATHER" in rca and "FORECAST" in rca:
            pin_score = 1
        elif "VODACOM" in hub:
            pin_score = 2
        elif "MTN" in hub:
            pin_score = 3
            
        # --- SECONDARY EVALUATION (User Selected Sort) ---
        if "Time" in sort_t:
            # Sort by newest first (highest timestamp) -> negative makes Python sort descending
            secondary_score = -float(inc.get("start_ts", 0))
        else:
            # Sort by Rank (Lowest rank number = highest priority)
            r = inc.get("Average_Rank", 0)
            secondary_score = float(r) if float(r) > 0 else 9999999
            
        # Return a tuple. Python will sort by pin_score first, then by secondary_score.
        return (pin_score, secondary_score)

    # Apply the sort
    filtered_incidents.sort(key=strict_sort_key)

    return filtered_incidents