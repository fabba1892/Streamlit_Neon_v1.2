from collections import Counter

def extract_sidebar_metrics(payload):
    """Hybrid Aggregation: Trusts JSON metadata for top metrics, counts RCAs manually."""
    if not payload:
        return {}

    # 1. TRUST THE METADATA FOR EXACT COUNTS
    meta = payload.get("metadata", {})
    total_oos = meta.get("total_oos_sites", 0)
    total_hubs = meta.get("total_hub_impacts", 0) # Pulling exact hub impacts
    
    # Fallbacks in case metadata keys vary
    if not total_oos: total_oos = meta.get("total_oos", 0)
    if not total_hubs: total_hubs = meta.get("total_incidents_shown", 0) 

    regional_data = payload.get("regional_data", {})
    priorities = Counter()
    rca_dist = Counter()
    total_alarms = 0

    # 2. MANUALLY TALLY PRIORITIES & RCA
    for region, r_data in regional_data.items():
        incidents = r_data.get("Incidents", [])
        for inc in incidents:
            total_alarms += 1
            
            # Tally Priorities
            pri = str(inc.get("MSDP_Priority", "P4")).upper()
            if "P1" in pri: priorities["P1"] += 1
            elif "P2" in pri: priorities["P2"] += 1
            elif "P3" in pri: priorities["P3"] += 1
            else: priorities["P4"] += 1
            
            # Tally RCA 
            raw_rca = str(inc.get("RCA", "Unknown"))
            clean_rca = raw_rca.split(":")[0].split("-")[0].strip()
            rca_dist[clean_rca] += 1

    # ... (Keep the top part of the function the same)

    # NEW: Pull the last refresh timestamp from the JSON
    # ... (Keep priority and RCA tallying exactly the same)

    # NEW: Precisely targets the "last_refreshed" key from your JSON payload
    last_refresh = meta.get("last_refreshed", 
                   meta.get("last_refresh", 
                   payload.get("last_refreshed", "Data Offline")))

    return {
        "total_oos": total_oos,
        "total_incidents": total_hubs, 
        "total_alarms": total_alarms,
        "priorities": dict(priorities),
        "top_rcas": rca_dist.most_common(5),
        "last_refresh": last_refresh # Pushed to the UI
    }

def extract_regional_cards(payload):
    """Calculates Top Cards: Pulls pre-calculated Total_OOS_Count from the regional header."""
    if not payload:
        return 0, {}

    # 1. HARD-PULL GLOBAL OOS FROM METADATA
    meta = payload.get("metadata", {})
    total_all_oos = meta.get("total_oos_sites", meta.get("total_oos", 0))

    # 2. EXTRACT REGIONAL OOS
    regional_oos = {}
    regional_data = payload.get("regional_data", {})

    for region, r_data in regional_data.items():
        # PRIMARY: Look for the exact key you specified in the JSON header
        oos = r_data.get("Total_OOS_Count")
        
        # If the key exists, ensure it is an integer
        if oos is not None:
            try:
                oos = int(float(oos))
            except (ValueError, TypeError):
                oos = 0
                
        # FALLBACK: If the Total_OOS_Count key is missing, count it manually line-by-line
        else:
            oos = 0
            for inc in r_data.get("Incidents", []):
                val = inc.get("OOS_Sites", 0)
                try:
                    if val and str(val).strip() != "":
                        oos += int(float(val))
                except (ValueError, TypeError):
                    pass
        
        # Assign to the dictionary
        regional_oos[region] = oos

    return total_all_oos, regional_oos