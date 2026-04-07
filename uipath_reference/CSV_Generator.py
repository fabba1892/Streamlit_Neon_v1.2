import json
import csv
import os
import sys
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & THRESHOLDS
# ==========================================
# These defaults are used if no arguments are passed from UiPath
DEFAULT_INPUT = "Netcool_Consolidated_Master.json"
DEFAULT_OUTPUT = "SharePoint_Incident_History.csv"

# Core columns to ensure appear first in the CSV for readability
CORE_COLUMNS = [
    "Snapshot_Time", 
    "Region", 
    "Hub_Name", 
    "OOS_Count", 
    "MSDP_Priority", 
    "RCA", 
    "Failure_Probability"
]

# ==========================================
# 2. DATA PROCESSING MODULES
# ==========================================

def process_to_flat_list(input_data):
    """
    Main function called by UiPath.
    Accepts either a file path string OR a raw JSON string.
    """
    try:
        # Step 1: Ingest Data
        # Check if the input is a path to a file
        if isinstance(input_data, str) and os.path.exists(input_data):
            with open(input_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
        # Check if the input is a raw JSON string
        elif isinstance(input_data, str):
            data = json.loads(input_data)
        else:
            return json.dumps({"error": "Invalid input format. Expected file path or JSON string."})

        # Step 2: Flatten Logic
        flattened_rows = []
        metadata = data.get("metadata", {})
        snapshot_time = metadata.get("last_refreshed", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        regional_data = data.get("regional_data", {})
        
        for region_name, region_info in regional_data.items():
            incidents = region_info.get("Incidents", [])
            for inc in incidents:
                # Initialize row with core timing and location
                row = {
                    "Snapshot_Time": snapshot_time,
                    "Region": region_name
                }
                
                # DYNAMIC EXTRACTION:
                # Automatically captures all top-level keys in the incident object.
                # If you add 'Weather' or 'LS_Stage' to Phase1Stage1.py, they appear here automatically.
                for key, value in inc.items():
                    if isinstance(value, (list, dict)):
                        # Convert specific lists to readable strings for CSV/Excel
                        if key == "County_List":
                            row[key] = "|".join(value)
                        # Skip complex nested details (like full alarm logs) to save space
                        continue
                    row[key] = value
                    
                flattened_rows.append(row)
        
        # Step 3: Save to History CSV
        save_status = save_to_history_csv(flattened_rows, DEFAULT_OUTPUT)
        
        # Return the flattened data as a JSON string back to UiPath
        return json.dumps({"status": save_status, "rows_processed": len(flattened_rows)})

    except Exception as e:
        import traceback
        return json.dumps({"error": str(e), "trace": traceback.format_exc()})

def save_to_history_csv(rows, output_path):
    """
    Appends the processed rows to the master history file.
    Handles dynamic headers if new fields are added later.
    """
    if not rows:
        return "No incidents found to log."

    # Identify all unique keys across all incidents (Dynamic Headers)
    all_keys = set()
    for r in rows:
        all_keys.update(r.keys())
    
    # Organize headers: Core columns first, then others alphabetically
    headers = CORE_COLUMNS + sorted([h for h in all_keys if h not in CORE_COLUMNS])

    file_exists = os.path.isfile(output_path)
    
    try:
        # Open in 'a' (append) mode to build history for forecasting
        with open(output_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            # Write header only if the file is being created for the first time
            if not file_exists:
                writer.writeheader()
            writer.writerows(rows)
        return "Success"
    except Exception as e:
        return f"CSV Error: {str(e)}"

# ==========================================
# 3. CLI RUNNER (For Manual Testing)
# ==========================================
if __name__ == "__main__":
    # If run manually from CMD, use the first argument as the file path
    target_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    print(f"Running standalone sync for: {target_path}")
    result = process_to_flat_list(target_path)
    print(result)