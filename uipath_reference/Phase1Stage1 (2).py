import json
import time
import re
import os
from collections import defaultdict, Counter
import rca_engine  # <--- Essential: This imports your separate RCA logic script

# =============================================================================
# MAJOR SECTION 1: GLOBAL CONFIGURATION & TUNING
# =============================================================================
CONFIG = {
    "MIN_OOS_DURATION_SECONDS": 300,
    "PROBABILITY_THRESHOLD": 70.0,
    "WINDOW_15M_SECONDS": 900,
    "P1_LIMIT": 15,
    "P2_LIMIT": 10,
    "P3_LIMIT": 5,
    "ALARM_HISTORY_WINDOW_HOURS": 12,
    "MIN_SITES_PER_INCIDENT": 3 
}

def norm_name(name):
    if not name: return ""
    return str(name).strip().upper().replace(" ", "_")

def extract_rank(rank_str):
    if not rank_str or "No Rank Data" in str(rank_str): return 0
    try:
        match = re.search(r'site_rank=(\d+)', str(rank_str))
        if match: return int(match.group(1))
        match = re.search(r'(\d+)', str(rank_str))
        return int(match.group(1)) if match else 0
    except: return 0

def get_oos_density(group_rows, oos_sites_set, OOS_KEYS, window_seconds):
    site_to_first_ts = {}
    for r in group_rows:
        loc = norm_name(r.get("LocationName", r.get("Node", "")))
        if loc in oos_sites_set and r.get("AlertKey") in OOS_KEYS:
            ts = int(r.get("LastOccurrence", 0))
            if loc not in site_to_first_ts or ts < site_to_first_ts[loc]:
                site_to_first_ts[loc] = ts
    if not site_to_first_ts: return 0, 0, 0.0, 0
    all_start_times = sorted(site_to_first_ts.values())
    max_burst_count, best_window_start = 0, 0
    for start_ts in all_start_times:
        count_in_window = sum(1 for ts in site_to_first_ts.values() if start_ts <= ts <= start_ts + window_seconds)
        if count_in_window > max_burst_count:
            max_burst_count, best_window_start = count_in_window, start_ts
    total_oos_sites_in_group = len(site_to_first_ts)
    probability = (max_burst_count / total_oos_sites_in_group) * 100
    return best_window_start, max_burst_count, probability, total_oos_sites_in_group

# =============================================================================
# MAJOR SECTION 2: MAIN PROCESSING ENGINE
# =============================================================================
def process_phase_1(netcool_file_path, hub_master_json, hub_report_json_str=None):
    OOS_KEYS = {'OML_FAULT', 'NODEB_UNAVAILABLE', 'CSL_FAULT', 'BTS_O&M_LINK_FAILURE', 
                'GNODEB_OUT_OF_SERVICE', 'NE3SWS_AGENT_NOT_RESPONDING_TO_REQUESTS', 
                'WCDMA_BASE_STATION_OUT_OF_USE', 'NE_IS_DISCONNECTED', "HUAWEI_SITE_OUT_OF_SERVICE", "NOKIA_SITE_OUT_OF_SERVICE"}
    PWR_KEYS = {"DEVICE_POWERED_OFF", "AC_MAINS_FAILED", "ESKOM_MAINS_FAILED", "GRID_SUPPLY_FAILURE", "BATTERY_LOW", "RECTIFIER_SYSTEM_FAILED", "FUEL_MISSING", "POWER_FAILURE"}
    TEMP_KEYS = {"HIGH_TEMPERATURE", "CABINET_TEMPERATURE_HIGH", "ROOM_TEMPERATURE_HIGH"}
    REGION_MAP = {1013: "LIM", 1014: "MPU", 1015: "NGA", 1018: "SGC", 1017: "SGS", 1008: "CEN", 1007: "EAS", 1005: "KZN", 1006: "WES"}
    COUNTY_LOOKUP = {3: 'Bandundu', 2: 'BDD', 4: 'CEN_BA', 7: 'CEN_NC', 9: 'CEN_WH', 10: 'CMZ_MAN', 11: 'CMZ_SOF', 12: 'CMZ_TET', 13: 'CMZ_ZAM', 17: 'EQT', 18: 'Equateur', 19: 'HKT', 20: 'HLU', 31: 'Kasai-Occidental', 32: 'Kasai-Oriental', 33: 'Katanga', 21: 'KGC', 1: 'Kie', 22: 'KIN', 23: 'KOC', 24: 'KOR', 27: 'KZN_NE', 28: 'KZN_NW', 34: 'LES_BB', 35: 'LES_BR', 36: 'LES_LR', 37: 'LES_LS', 38: 'LES_MA', 40: 'LES_MF', 39: 'LES_MH', 41: 'LES_MK', 42: 'LES_QA', 43: 'LES_QN', 44: 'LES_QT', 45: 'LES_TH', 49: 'LES_TT', 60: 'MAN', 55: 'Maniema', 53: 'MPU_NO', 54: 'MPU_SO', 59: 'NKV', 61: 'NMZ_CAB', 62: 'NMZ_NAM', 63: 'NMZ_NIA', 66: 'POR', 73: 'SKV', 74: 'SMZ_GAZ', 75: 'SMZ_INH', 76: 'SMZ_MPC', 77: 'SMZ_MPP', 78: 'Sud Kivu', 5: 'Diamond', 6: 'Goldfields', 8: 'Platinum', 14: 'Bay', 15: 'Eden', 16: 'Kei', 25: 'Berg', 26: 'eThekwini', 29: 'South', 30: 'Zululand', 79: 'Atlantic', 80: 'Whale', 81: 'Winelands', 46: 'Capricorn', 47: 'Vhembe', 48: 'Waterberg', 50: 'Ehlanzeni', 51: 'Gert Sibande', 52: 'Nkangala', 56: 'NGA Metro', 57: 'NGA North', 58: 'North West', 65: 'Aerotropolis', 68: 'Aerotropolis', 64: 'Central', 67: 'Central', 69: 'West Side', 71: 'Deep South', 70: 'Far East', 72: 'Jozi West', -1: 'Unknown', 0: 'Not Set'}

    try:
        with open(netcool_file_path, 'r', encoding='utf-8') as f: raw_data = json.load(f)
        rows = raw_data if isinstance(raw_data, list) else raw_data.get("rowset", {}).get("rows", [])
        topology_raw = json.loads(hub_master_json)
        topology_map = {norm_name(k): norm_name(v) for k, v in topology_raw.items()}

        hub_report_map = {} 
        if hub_report_json_str and hub_report_json_str.strip():
            hub_data = json.loads(hub_report_json_str)
            for h_name, h_info in hub_data.items():
                hub_report_map[norm_name(h_name)] = {"RAN_Risk_Count": int(h_info.get("num_RAN_RISK_LOCATIONS") or 0), "VBS_Count": int(h_info.get("numvbs") or 0), "RAN_Failed_Count": int(h_info.get("numranlocations") or 0), "Potential_Failure": int(h_info.get("num_RAN_RISK_LOCATIONS") or 0) + int(h_info.get("numranlocations") or 0)}

        global_diag = {"PWR": set(), "TEMP": set(), "HUBS": set()}
        site_ranks, site_all_alarms_map = {}, defaultdict(list)
        
        for r in rows:
            loc, ak = norm_name(r.get("LocationName", r.get("Node", ""))), r.get("AlertKey", "")
            if ak in PWR_KEYS: global_diag["PWR"].add(loc)
            if ak in TEMP_KEYS: global_diag["TEMP"].add(loc)
            if "txhub site" in str(r.get("AffectedServices", "")).lower(): global_diag["HUBS"].add(loc)
            site_all_alarms_map[loc].append({"Alarm": ak, "Summary": r.get("Summary", ""), "Severity": r.get("Severity"), "RawLastOccurrence": int(r.get("LastOccurrence", 0)), "LastOccurrence": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(r.get("LastOccurrence", 0)))), "Serial": r.get("Serial")})
            curr_rank = extract_rank(r.get("Rank", ""))
            if curr_rank > 0 and (loc not in site_ranks or curr_rank < site_ranks[loc]): site_ranks[loc] = curr_rank

        now_ts = int(time.time())
        active_oos_rows = [r for r in rows if r.get("AlertKey") in OOS_KEYS and (now_ts - int(r.get("LastOccurrence", 0))) >= CONFIG["MIN_OOS_DURATION_SECONDS"]]
        oos_sites_set = {norm_name(r.get("LocationName", r.get("Node", ""))) for r in active_oos_rows}
        
        region_buckets = defaultdict(list)
        for r in active_oos_rows: region_buckets[REGION_MAP.get(r.get("RegionID"), "Unknown")].append(r)

        regional_output, all_rank_values = {}, []
        for reg_name, reg_rows in region_buckets.items():
            total_regional_oos_count = len({norm_name(r.get("LocationName", r.get("Node", ""))) for r in reg_rows})
            final_incidents, processed_sites = [], set()
            temp_hub_map = defaultdict(list)
            for r in reg_rows:
                loc = norm_name(r.get("LocationName", r.get("Node", "")))
                parent = topology_map.get(loc, loc)
                if parent in global_diag["HUBS"] or loc in global_diag["HUBS"]: temp_hub_map[parent].append(r)

            hub_events_list = []
            for parent_hub, g_rows in temp_hub_map.items():
                d_start, _, d_pct, t_oos = get_oos_density(g_rows, oos_sites_set, OOS_KEYS, CONFIG["WINDOW_15M_SECONDS"])
                if d_pct >= CONFIG["PROBABILITY_THRESHOLD"]: hub_events_list.append({"name": parent_hub, "ts": d_start, "rows": g_rows, "total_base": t_oos})

            hub_events_list.sort(key=lambda x: x["ts"])
            while hub_events_list:
                base = hub_events_list.pop(0)
                cluster_rows, involved_hubs, total_base = list(base["rows"]), [base["name"]], base["total_base"]
                to_rem = [i for i, other in enumerate(hub_events_list) if other["ts"] <= base["ts"] + 180]
                for i in sorted(to_rem, reverse=True):
                    cluster_rows.extend(hub_events_list[i]["rows"])
                    involved_hubs.append(hub_events_list[i]["name"])
                    total_base += hub_events_list[i]["total_base"]
                    hub_events_list.pop(i)
                valid_lead_hubs = [h for h in involved_hubs if h in oos_sites_set]
                if not valid_lead_hubs: valid_lead_hubs = [norm_name(r.get("LocationName", r.get("Node", ""))) for r in cluster_rows if norm_name(r.get("LocationName", r.get("Node", ""))) in oos_sites_set]
                if valid_lead_hubs:
                    lead_hub = sorted(valid_lead_hubs, key=lambda h: site_ranks.get(h, 999999))[0]
                    inc = create_incident_block(cluster_rows, reg_name, lead_hub, "Hubsite Failure", site_all_alarms_map, global_diag, site_ranks, COUNTY_LOOKUP, hub_report_map, topology_map, oos_sites_set, OOS_KEYS, total_base)
                    for loc in inc.get("OOS_Location_List", []): processed_sites.add(loc)
                    if float(inc.get("Failure_Probability", "0%").strip('%')) >= CONFIG["PROBABILITY_THRESHOLD"] and len(inc.get("OOS_Location_List", [])) >= CONFIG["MIN_SITES_PER_INCIDENT"]:
                        final_incidents.append(inc)
                        if inc["Average_Rank"] > 0: all_rank_values.append(inc["Average_Rank"])

            remaining = [r for r in reg_rows if norm_name(r.get("LocationName", r.get("Node", ""))) not in processed_sites]
            county_groups = defaultdict(list)
            for r in remaining: county_groups[r.get("CountyID", -1)].append(r)
            for c_id, c_rows in county_groups.items():
                site_oos_ts = {}
                for r in c_rows:
                    loc = norm_name(r.get("LocationName", r.get("Node", "")))
                    if loc in oos_sites_set and r.get("AlertKey") in OOS_KEYS:
                        ts = int(r.get("LastOccurrence", 0))
                        if loc not in site_oos_ts or ts < site_oos_ts[loc]: site_oos_ts[loc] = ts
                total_county_oos, sorted_locs = len(site_oos_ts), sorted(site_oos_ts.keys(), key=lambda loc: site_oos_ts[loc])
                while sorted_locs:
                    base_ts = site_oos_ts[sorted_locs[0]]
                    cluster_locs = [loc for loc in sorted_locs if site_oos_ts[loc] <= base_ts + CONFIG["WINDOW_15M_SECONDS"]]
                    p_rows = [r for r in c_rows if norm_name(r.get("LocationName", r.get("Node", ""))) in cluster_locs]
                    inc = create_incident_block(p_rows, reg_name, "County Group", "Link Issue", site_all_alarms_map, global_diag, site_ranks, COUNTY_LOOKUP, hub_report_map, topology_map, oos_sites_set, OOS_KEYS, total_county_oos)
                    for loc in inc.get("OOS_Location_List", []): processed_sites.add(loc)
                    if float(inc.get("Failure_Probability", "0%").strip('%')) >= CONFIG["PROBABILITY_THRESHOLD"] and len(inc.get("OOS_Location_List", [])) >= CONFIG["MIN_SITES_PER_INCIDENT"]:
                        final_incidents.append(inc)
                        if inc["Average_Rank"] > 0: all_rank_values.append(inc["Average_Rank"])
                        sorted_locs = [loc for loc in sorted_locs if loc not in cluster_locs]
                    else: sorted_locs.pop(0)
            regional_output[reg_name] = {"Total_OOS_Count": total_regional_oos_count, "Incidents": final_incidents}
        return json.dumps({"metadata": {"last_refreshed": time.strftime('%Y-%m-%d %H:%M:%S'), "total_oos_sites": sum(v["Total_OOS_Count"] for v in regional_output.values()), "total_incidents_shown": sum(len(v["Incidents"]) for v in regional_output.values()), "min_avg_rank": min(all_rank_values) if all_rank_values else 0}, "regional_data": regional_output})
    except Exception as e: return json.dumps({"error": str(e)})

def create_incident_block(group_rows, reg_name, hub_display, rca_base, site_alarms, global_diag, site_ranks, COUNTY_LOOKUP, hub_report_map, topology_map, oos_sites_set, OOS_KEYS, total_base_oos=0):
    s_oos = {norm_name(r.get("LocationName", r.get("Node", ""))) for r in group_rows if norm_name(r.get("LocationName", r.get("Node", ""))) in oos_sites_set}
    if not s_oos: return {"Failure_Probability": "0%"} 
    clean_hub = norm_name(hub_display)
    hub_info = hub_report_map.get(clean_hub, {"RAN_Risk_Count": 0, "VBS_Count": 0, "RAN_Failed_Count": 0, "Potential_Failure": 0})
    start_ts, max_15m, _, _ = get_oos_density(group_rows, s_oos, OOS_KEYS, CONFIG["WINDOW_15M_SECONDS"])
    
    # 1. Probability Calculation Fix (ensures clustered incidents show real density)
    if total_base_oos == 0: total_base_oos = len(s_oos)
    real_probability = (max_15m / total_base_oos) * 100 if total_base_oos > 0 else 0
    
    # 2. CALL THE EXTERNAL RCA ENGINE (Separated logic)
    final_rca = rca_engine.calculate_rca(
        clean_hub=clean_hub, 
        rca_base=rca_base, 
        s_oos=s_oos, 
        site_alarms=site_alarms, 
        global_diag_pwr=global_diag["PWR"]
    )
    
    # 3. Data structure assembly
    oos_location_details = {}
    for loc in s_oos:
        parent_hub = topology_map.get(loc, loc)
        loc_hub = hub_report_map.get(loc) or hub_report_map.get(parent_hub, {"RAN_Risk_Count": 0, "VBS_Count": 0, "RAN_Failed_Count": 0, "Potential_Failure": 0})
        oos_location_details[loc] = {
            "metadata": {
                "is_primary_hub": (loc == clean_hub), 
                "Site_Rank": site_ranks.get(loc, 0), 
                "RAN_Risk_Count": loc_hub["RAN_Risk_Count"], 
                "VBS_Count": loc_hub["VBS_Count"], 
                "RAN_Failed_Count": loc_hub["RAN_Failed_Count"], 
                "Potential_Failure": loc_hub["Potential_Failure"]
            }, 
            "alarms": [a for a in site_alarms.get(loc, []) if a.get("RawLastOccurrence", 0) >= (start_ts - (CONFIG["ALARM_HISTORY_WINDOW_HOURS"] * 3600))]
        }
    
    ranks = [site_ranks.get(s, 0) for s in s_oos if s in site_ranks]
    return {
        "start_ts": start_ts, 
        "Region": reg_name, 
        "Hub_Name": hub_display, 
        "County_List": sorted(list({COUNTY_LOOKUP.get(r.get("CountyID"), "Unknown") for r in group_rows if norm_name(r.get("LocationName", r.get("Node", ""))) in s_oos})), 
        "RAN_Risk_Count": hub_info["RAN_Risk_Count"], 
        "VBS_Count": hub_info["VBS_Count"], 
        "RAN_Failed_Count": hub_info["RAN_Failed_Count"], 
        "Potential_Failure": hub_info["Potential_Failure"], 
        "OOS_Count": len(s_oos), 
        "Impact_15min_Count": max_15m, 
        "MSDP_Priority": "P1" if len(s_oos) >= CONFIG["P1_LIMIT"] else "P2" if len(s_oos) >= CONFIG["P2_LIMIT"] else "P3" if len(s_oos) >= CONFIG["P3_LIMIT"] else "P4", 
        "Average_Rank": round(sum(ranks)/len(ranks), 1) if ranks else 0, 
        "RCA": final_rca, 
        "OOS_Location_List": sorted(list(s_oos)), 
        "OOS_Location_Details": oos_location_details, 
        "Failure_Probability": f"{round(real_probability, 1)}%"
    }