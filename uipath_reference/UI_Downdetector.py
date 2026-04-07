from datetime import datetime

def get_html(inc):
    priority = inc.get("MSDP_Priority", "P2")
    reports = inc.get("OOS_Count", 0)
    ts = inc.get("start_ts", 0)
    dt_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    rca = inc.get("RCA", "Unknown")
    hub = inc.get("Hub_Name", "Unknown Provider")

    # Header as requested: P1 2026-04-02 07:23:33 150 Reports from DOWNDETECTOR
    header_text = f"{priority} {dt_str} {reports} Reports from DOWNDETECTOR"

    return f'''
    <div class="incident downdetector-incident">
        <div class="header" onclick="this.parentElement.classList.toggle('open')" style="border-left: 5px solid #f97316;">
            <div style="display:flex; align-items:center; gap:10px; flex-grow:1;">
                <span class="p-tag {priority}">{priority}</span>
                <span style="font-family:monospace; background:#fff7ed; padding:2px 6px;">{dt_str}</span>
                <span style="font-weight:800; color:#c2410c;">{reports} Reports from DOWNDETECTOR</span>
                <span style="color:#94a3b8;">|</span>
                <span style="font-weight:700;">RCA: {rca}</span>
            </div>
        </div>
        <div class="details" style="background:#fffaf5;">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; padding:10px;">
                <div style="background:white; border:1px solid #fed7aa; padding:15px; border-radius:8px;">
                    <h4 style="margin:0 0 10px 0; color:#ea580c;">📈 Sentiment Analytics</h4>
                    <div style="height:100px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; border-radius:4px; color:#94a3b8;">
                        [Placeholder: Call Heatmap/Graph function here]
                    </div>
                </div>
                <div style="background:white; border:1px solid #fed7aa; padding:15px; border-radius:8px;">
                    <h4 style="margin:0 0 10px 0; color:#ea580c;">Provider Info</h4>
                    <p><b>Target:</b> {hub}</p>
                    <p><b>Confidence:</b> {inc.get('Failure_Probability', '100%')}</p>
                    <p><b>Region:</b> National</p>
                </div>
            </div>
        </div>
    </div>
    '''