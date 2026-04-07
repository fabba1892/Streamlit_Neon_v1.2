from collections import Counter

def extract_sidebar_metrics(payload):
    """Hard-aggregates metrics directly from the raw JSON to guarantee accuracy."""
    if not payload or "regional_data" not in payload:
        return {}

    regional_data = payload.get("regional_data", {})

    total_oos = 0
    total_incidents = 0
    total_hubs = 0
    priorities = Counter()
    rca_dist = Counter()

    # Deep dive into the raw data
    for region, r_data in regional_data.items():
        incidents = r_data.get("Incidents", [])
        for inc in incidents:
            total_incidents += 1
            
            # 1. Sum OOS Sites manually
            oos_count = inc.get("OOS_Sites", 0)
            if isinstance(oos_count, (int, float)):
                total_oos += oos_count
            elif isinstance(oos_count, str) and oos_count.isdigit():
                total_oos += int(oos_count)

            # 2. Count Hub Impacts (Checking if Hub_Failure is True or "Yes")
            is_hub = inc.get("Hub_Failure", False)
            if is_hub in [True, "Yes", "true"]:
                total_hubs += 1

            # 3. Tally Priorities
            pri = str(inc.get("MSDP_Priority", "P4")).upper()
            if "P1" in pri: priorities["P1"] += 1
            elif "P2" in pri: priorities["P2"] += 1
            elif "P3" in pri: priorities["P3"] += 1
            else: priorities["P4"] += 1
            
            # 4. Tally RCA 
            raw_rca = str(inc.get("RCA", "Unknown"))
            clean_rca = raw_rca.split(":")[0].split("-")[0].strip()
            rca_dist[clean_rca] += 1

    return {
        "total_oos": total_oos,
        "total_incidents": total_hubs,  # Mapping "Hub Impacts" specifically to Hub Failures
        "total_alarms": total_incidents, # Total raw alarms
        "priorities": dict(priorities),
        "top_rcas": rca_dist.most_common(5)
    }