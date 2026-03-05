import pandas as pd
import json

def load_and_prepare_neon_data(json_input):
    try:
        data = json.loads(json_input)
        metadata = data.get("metadata", {})
        regional_raw = data.get("regional_data", {})
        
        regional_stats = {
            reg: info.get("Total_OOS_Count", 0) 
            for reg, info in regional_raw.items()
        }

        all_incidents = []
        for region_code, content in regional_raw.items():
            for inc in content.get("Incidents", []):
                inc["Region_Key"] = region_code
                inc["County_String"] = ", ".join(inc.get("County_List", ["Unknown"]))
                
                tech = inc.get("Tech_Counts", {})
                inc["2G_Count"] = tech.get("2G", 0)
                inc["3G_Count"] = tech.get("3G", 0)
                inc["4G_Count"] = tech.get("4G", 0)
                inc["5G_Count"] = tech.get("5G", 0)
                
                inc["Power_Count"] = len(inc.get("Power_Location_List", [])) if isinstance(inc.get("Power_Location_List"), list) else 0
                inc["Hub_Impact_Count"] = len(inc.get("Hub_Site_List", [])) if isinstance(inc.get("Hub_Site_List"), list) else 0
                
                all_incidents.append(inc)

        df = pd.DataFrame(all_incidents)
        if not df.empty:
            df = df.sort_values(by="Average_Rank", ascending=True)
            priority_map = {"P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5}
            df["Priority_Num"] = df["MSDP_Priority"].map(priority_map)
            
        return metadata, regional_stats, df
    except Exception as e:
        print(f"Engine Error: {e}")
        return {}, {}, pd.DataFrame()

def apply_tactical_filters(df, selected_regions, min_priority):
    if df.empty: return df
    filtered_df = df.copy()
    if selected_regions:
        filtered_df = filtered_df[filtered_df["Region_Key"].isin(selected_regions)]
    priority_limit = {"P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5}.get(min_priority, 5)
    filtered_df = filtered_df[filtered_df["Priority_Num"] <= priority_limit]
    return filtered_df

def get_sidebar_aggregates(df, regional_stats):
    if df.empty:
        return {"total_oos": sum(regional_stats.values()), "total_pwr": 0, "total_hubs": 0, "prio_counts": {}}
    
    return {
        "total_oos": sum(regional_stats.values()),
        "total_pwr": int(df['Power_Count'].sum()),
        "total_hubs": int(len(df[df['RCA'] == 'Hubsite Failure'])),
        "prio_counts": df['MSDP_Priority'].value_counts().to_dict()
    }