import json
import csv
import os
import sys
from datetime import datetime

# Threshold: Only show a "Spike" incident if reports are above this number
REPORTS_THRESHOLD = 20 

def build_incident_block(title, rca, total_reports=0, priority="P3"):
    """Helper to create a standardized incident block for the dashboard."""
    return {
        "start_ts": int(datetime.now().timestamp()),
        "Region": "DOWNDETECTOR",
        "Hub_Name": title,
        "County_List": ["National"],
        "OOS_Count": total_reports,
        "Impact_15min_Count": total_reports,
        "MSDP_Priority": priority,
        "Average_Rank": 0,
        "RCA": rca,
        "Failure_Probability": "100.0%",
        "OOS_Location_List": [],
        "OOS_Location_Details": {}
    }

def create_dd_incident(phase1_file_path, csv_path, api_result_string):
    """
    Main method called by UiPath.
    Inputs: Phase1 Path (Str), CSV History Path (Str), Combined Indicator Data (JSON Str)
    """
    incidents_to_add = []
    log_rows = []
    
    # 1. Load the existing Phase1 Result file
    try:
        if not os.path.exists(phase1_file_path):
            return f"Error: {phase1_file_path} not found."
            
        with open(phase1_file_path, 'r', encoding='utf-8') as f:
            phase1_data = json.load(f)
    except Exception as e:
        return f"Error reading Phase1 file: {str(e)}"

    # 2. Process Combined API Result String from UiPath
    try:
        if not api_result_string or len(str(api_result_string).strip()) < 5:
            raise ValueError("Empty or invalid API response received.")
            
        combined_data = json.loads(api_result_string)
        
        # Loop through each provider in the JSON (e.g., "vodacom", "mtn")
        for provider_name, indicators in combined_data.items():
            total_reports = sum(item.get('amount', 0) for item in indicators)
            
            if total_reports > 0:
                # Identify top complaint category for this provider
                sorted_inds = sorted(indicators, key=lambda x: x.get('amount', 0), reverse=True)
                top_issue = sorted_inds[0]['indicator']['slug'].replace('-', ' ').title()
                top_pct = sorted_inds[0]['percentage']
                
                # Determine if volume warrants an incident
                if total_reports >= REPORTS_THRESHOLD:
                    incidents_to_add.append(build_incident_block(
                        title=f"{provider_name.upper()}: {total_reports} Reports",
                        rca=f"Crowdsourced Spike: {top_issue} ({top_pct}%)",
                        total_reports=total_reports,
                        priority="P1" if total_reports > 100 else "P2"
                    ))
                
                # Data for CSV Logging
                log_rows.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    int(datetime.now().timestamp()), 
                    provider_name.upper(), 
                    total_reports, 
                    top_issue, 
                    top_pct
                ])
            else:
                # Log zero reports for this provider to keep history consistent
                log_rows.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    int(datetime.now().timestamp()), 
                    provider_name.upper(), 
                    0, 
                    "None", 
                    0
                ])

    except Exception as e:
        # If the API string is broken, create a system warning incident
        incidents_to_add.append(build_incident_block(
            title="⚠️ DOWNDETECTOR DATA ERROR",
            rca=f"UiPath passed invalid data: {str(e)[:50]}",
            total_reports=0,
            priority="P3"
        ))

    # 3. Append to CSV History
    try:
        if log_rows:
            file_exists = os.path.isfile(csv_path)
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    # Added 'Provider' to the header
                    writer.writerow(['Datetime', 'Timestamp', 'Provider', 'Total_Reports', 'Top_Issue', 'Top_Issue_Pct'])
                writer.writerows(log_rows)
    except Exception as e:
        print(f"CSV Write Error: {e}")

    # 4. Update the JSON Structure
    if "regional_data" not in phase1_data:
        phase1_data["regional_data"] = {}
    
    # Inject the Downdetector region with ALL generated incidents
    phase1_data["regional_data"]["DOWNDETECTOR"] = {
        "Total_OOS_Count": sum(inc["OOS_Count"] for inc in incidents_to_add),
        "Incidents": incidents_to_add
    }
    
    # Update Metadata incident count
    phase1_data["metadata"]["total_incidents_shown"] = len(phase1_data["regional_data"])

    # 5. Save and Return success string to UiPath 'prettyText' variable
    try:
        with open(phase1_file_path, 'w', encoding='utf-8') as f:
            json.dump(phase1_data, f, indent=2)
        provider_count = len(combined_data.keys()) if 'combined_data' in locals() else 0
        return f"Success: Processed {provider_count} providers."
    except Exception as e:
        return f"Error saving JSON: {str(e)}"