import json
import os

def Merge_Netcool_Files(json_input_args: str) -> str:
    try:
        args = json.loads(json_input_args)
        path_list = args.get("paths", [])
        save_path = args.get("save_path", "Netcool_Consolidated_Master.json")
        
        all_rows = []
        summary = [] # Track what happened to each file

        for path in path_list:
            clean_path = str(path).strip().replace('"', '')
            
            if not os.path.exists(clean_path):
                summary.append(f"FAILED: {clean_path} (File not found)")
                continue

            with open(clean_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
                
                # --- NEW ROBUST EXTRACTION LOGIC ---
                current_rows = []
                if isinstance(data, list):
                    current_rows = data
                elif isinstance(data, dict):
                    # Check for "rowset" wrapper (Source 1)
                    if "rowset" in data:
                        current_rows = data["rowset"].get("rows", [])
                    # Check for direct "rows" key (Source 2)
                    elif "rows" in data:
                        current_rows = data["rows"]
                    # If the dictionary is the row itself (rare but possible)
                    else:
                        current_rows = []
                
                if isinstance(current_rows, list):
                    all_rows.extend(current_rows)
                    summary.append(f"SUCCESS: {clean_path} ({len(current_rows)} rows)")
                else:
                    summary.append(f"SKIPPED: {clean_path} (Invalid data format)")

        if not all_rows:
            return json.dumps({"status": "failed", "error": "No data found in any file", "details": summary})

        # Save to disk
        with open(save_path, 'w', encoding='utf-8') as f_out:
            json.dump(all_rows, f_out)

        # Return status including the summary of which files worked
        return json.dumps({
            "status": "success", 
            "row_count": len(all_rows),
            "file_summary": summary,
            "merged_file": save_path
        })

    except Exception as e:
        return json.dumps({"status": "exception", "error": str(e)})