from datetime import datetime

def get_html(inc):
    w_obj = inc.get("Weather", {})
    curr = w_obj.get("current", {})
    fc = w_obj.get("forecast_8h", {})
    hub = inc.get("Hub_Name", "Weather Alert")
    rca = inc.get("RCA", "")

    return f'''
    <div class="incident weather-incident">
        <div class="header" onclick="this.parentElement.classList.toggle('open')" style="border-left: 5px solid #0ea5e9;">
            <div style="display:flex; align-items:center; gap:10px; flex-grow:1;">
                <span style="font-size:1.2rem;">{curr.get('icon', '☁️')}</span>
                <span style="font-weight:800; color:#0369a1;">{hub}</span>
                <span style="color:#94a3b8;">|</span>
                <span>{rca}</span>
            </div>
        </div>
        <div class="details" style="background:#f0f9ff;">
             <div style="display:flex; gap:20px; padding:10px;">
                <div style="flex:1; background:white; padding:10px; border-radius:5px; border:1px solid #bae6fd;">
                    <b>Current:</b> {curr.get('temp')} | Wind: {curr.get('wind')} | Rain: {curr.get('rain')}
                </div>
                <div style="flex:1; background:white; padding:10px; border-radius:5px; border:1px solid #bae6fd;">
                    <b>8H Forecast:</b> {fc.get('icon')} {fc.get('temp')} | Wind: {fc.get('wind')}
                </div>
             </div>
        </div>
    </div>
    '''