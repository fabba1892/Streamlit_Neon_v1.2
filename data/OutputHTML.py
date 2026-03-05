import json

def build_incident_dashboard(json_str):
    try:
        data = json.loads(json_str)
        time_series = data.get("time_series_data", [])
        
        # Sort by latest events first
        time_series.sort(key=lambda x: x.get("Window_Start", ""), reverse=True)
        
        # Aggregate Regional Overview
        region_stats = {}
        for win in time_series:
            r = win.get('Region', 'Global')
            region_stats[r] = region_stats.get(r, 0) + win.get('OOS_Count', 0)
        
        unique_regions = sorted(region_stats.keys())

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; display: flex; margin: 0; background: #f0f2f5; height: 100vh; overflow: hidden; }}
                .sidebar {{ width: 280px; background: #1e293b; color: white; padding: 25px; box-sizing: border-box; }}
                .filter-box {{ margin-bottom: 20px; }}
                select, input {{ width: 100%; padding: 10px; border-radius: 6px; border: none; margin-top: 5px; }}
                .main {{ flex: 1; padding: 30px; overflow-y: auto; }}
                .overview-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 12px; margin-bottom: 30px; }}
                .stat-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; border-top: 4px solid #38bdf8; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #333; }}
                .collapsible {{ width: 100%; padding: 15px; border: none; border-radius: 6px; color: white; cursor: pointer; text-align: left; display: flex; justify-content: space-between; margin-top: 8px; }}
                .d-bright {{ background: #ef4444; border: 2px solid #000; font-weight: bold; }}
                .d-red    {{ background: #b91c1c; }}
                .d-orange {{ background: #f97316; }}
                .d-yellow {{ background: #eab308; color: black !important; }}
                .d-normal {{ background: #10b981; }}
                .content {{ display: none; padding: 20px; background: white; border: 1px solid #ddd; border-top: none; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td, th {{ text-align: left; padding: 8px; border-bottom: 1px solid #eee; color: #444; }}
            </style>
        </head>
        <body>
            <div class="sidebar">
                <h2>Network Ops</h2>
                <div class="filter-box"><label>Search</label><input type="text" id="search" onkeyup="applyFilters()" placeholder="Search..."></div>
                <div class="filter-box"><label>Region</label><select id="regionSelect" onchange="applyFilters()"><option value="all">All Regions</option>
                {''.join([f'<option value="{r}">{r}</option>' for r in unique_regions])}</select></div>
            </div>
            <div class="main">
                <div class="overview-grid">
                {''.join([f'<div class="stat-card"><h4>{r}</h4><div>{count}</div></div>' for r, count in region_stats.items()])}
                </div>
                <div id="eventWrapper">
        """

        for win in time_series:
            oos, reg = win.get('OOS_Count', 0), win.get('Region', 'N/A')
            if oos > 20: cls, lbl = "d-bright", "CRITICAL (>20)"
            elif oos > 15: cls, lbl = "d-red", "RED (>15)"
            elif oos > 10: cls, lbl = "d-orange", "ORANGE (>10)"
            elif oos > 5: cls, lbl = "d-yellow", "YELLOW (>5)"
            else: cls, lbl = "d-normal", "STABLE"

            html += f"""
                <div class="event-item" data-region="{reg}">
                    <button class="collapsible {cls}">
                        <span><strong>[{reg}]</strong> {win['Window_Start']} — {oos} OOS Sites</span>
                        <span style="font-size: 11px; font-weight: bold;">{lbl}</span>
                    </button>
                    <div class="content">
                        <table>
                            <tr><th>Duration</th><td>{win.get('Duration_Mins')} Mins</td></tr>
                            <tr><th>Power Hits</th><td>{win.get('Power_Count')}</td></tr>
                            <tr><th>High Temp</th><td>{win.get('Temp_Count')}</td></tr>
                            <tr><th>Insight</th><td>{win.get('Insight')}</td></tr>
                        </table>
                    </div>
                </div>"""

        html += """
                </div>
            </div>
            <script>
                var btns = document.getElementsByClassName("collapsible");
                for (var i = 0; i < btns.length; i++) {
                    btns[i].addEventListener("click", function() {
                        var panel = this.nextElementSibling;
                        panel.style.display = (panel.style.display === "block") ? "none" : "block";
                    });
                }
                function applyFilters() {
                    var s = document.getElementById("search").value.toLowerCase();
                    var r = document.getElementById("regionSelect").value;
                    var items = document.getElementsByClassName("event-item");
                    for (var i = 0; i < items.length; i++) {
                        var txt = items[i].innerText.toLowerCase();
                        var reg = items[i].getAttribute("data-region");
                        items[i].style.display = (txt.includes(s) && (r === "all" || reg === r)) ? "block" : "none";
                    }
                }
            </script>
        </body></html>"""
        return html
    except Exception as e:
        return f"<h1>Error Generating Dashboard</h1><p>{str(e)}</p>"