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

    return {
        "total_oos": total_oos,
        "total_incidents": total_hubs, 
        "total_alarms": total_alarms,
        "priorities": dict(priorities),
        "top_rcas": rca_dist.most_common(5)
    }