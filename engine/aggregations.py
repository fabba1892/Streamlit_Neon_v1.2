from collections import Counter

def extract_sidebar_metrics(payload):
    """Parses the payload to extract core network health metrics."""
    if not payload or "metadata" not in payload:
        return {}

    meta = payload.get("metadata", {})
    regional_data = payload.get("regional_data", {})

    # 1. Base Core Metrics
    total_oos = meta.get("total_oos_sites", 0)
    total_incidents = meta.get("total_incidents_shown", 0)

    # 2. Aggregation Counters
    priorities = Counter()
    rca_dist = Counter()

    # 3. Dynamic Loop through Regions
    for region, r_data in regional_data.items():
        incidents = r_data.get("Incidents", [])
        for inc in incidents:
            # Tally Priorities (This gracefully handles weather icons like 💨 as well)
            pri = inc.get("MSDP_Priority", "Unknown")
            priorities[pri] += 1
            
            # Tally RCA 
            # We split by ':' or '-' to group the high-level categories (e.g., "Hubsite Failure" vs "Weather")
            raw_rca = inc.get("RCA", "Unknown")
            clean_rca = raw_rca.split(":")[0].split("-")[0].strip()
            rca_dist[clean_rca] += 1

    return {
        "total_oos": total_oos,
        "total_incidents": total_incidents,
        "priorities": dict(priorities),
        "top_rcas": rca_dist.most_common(5) # Only grab Top 5 for sidebar real estate
    }