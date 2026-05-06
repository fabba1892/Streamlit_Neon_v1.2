"""
=============================================================================
DASHBOARD MAPPING LOGIC — Phase1result.json → Network Incident Dashboard
=============================================================================

ARCHITECTURE OVERVIEW
─────────────────────
This is a single-file, self-contained dashboard. There is no backend server,
no API calls at runtime, no database. The entire data pipeline is:

  Phase1result.txt  ──[Python]──>  Embedded PAYLOAD in HTML  ──[JS]──>  DOM

The Python script runs ONCE at build time to:
  1. Read and parse the JSON
  2. Pre-extract filter options (regions, RCAs, counties) for the <select> dropdowns
  3. Inject the raw JSON string directly into the HTML as a JS variable
  4. Write out the finished .html file

At runtime the browser's JavaScript reads PAYLOAD and builds everything
dynamically — no server needed.

=============================================================================
PART 1 — PYTHON BUILD-TIME LOGIC
=============================================================================
"""

import json

# ─── STEP 1: Read the raw payload ────────────────────────────────────────────
# We keep it as a raw string (not just the parsed dict) so we can inject the
# exact JSON text into the JS variable. This avoids re-serialising and any
# potential float/unicode drift.

with open('Phase1result.txt') as f:
    raw_json = f.read()                      # Raw string → goes into the HTML
    data = json.loads(raw_json)              # Parsed dict → used for pre-extraction


# ─── STEP 2: Understand the top-level structure ───────────────────────────────
#
# The payload looks like this:
#
# {
#   "metadata": {
#     "last_refreshed": "2026-04-15 12:13:57",
#     "total_regions": 9,
#     "min_avg_rank": 5064.0
#   },
#   "regional_data": {
#     "MPU": {
#       "Total_OOS_Count": 79,
#       "Incidents": [ {...}, {...} ]
#     },
#     "KZN": { ... },
#     "DOWNDETECTOR": {
#       "Total_OOS_Count": 9,
#       "metadata": { "TriggerData": {...}, "History": {...}, ... },
#       "Incidents": [ {...} ]
#     },
#     ... 7 more regions
#   }
# }
#
# KEY INSIGHT: Every region follows the same shape EXCEPT "DOWNDETECTOR",
# which has an extra nested "metadata" block containing sparkline history,
# indicator breakdowns, and geo device data. We handle it as a special case.

meta    = data['metadata']
regions = data['regional_data']


# ─── STEP 3: Pre-extract unique filter values ─────────────────────────────────
# We walk every incident in every region once and collect the unique set of
# RCA values and County names. These populate the sidebar <select> dropdowns.
# Doing this in Python means the HTML ships with the correct options already
# baked in — no JS needed to generate them.

all_rcas    = set()
all_counties = set()

for region_name, region_data in regions.items():
    for incident in region_data.get('Incidents', []):
        rca = incident.get('RCA', '')
        if rca:
            all_rcas.add(rca)
        for county in incident.get('County_List', []):
            if county:
                all_counties.add(county)

# Produces things like:
#   all_rcas    = {"Hubsite Failure - Power", "Link Issue - Transmission", ...}
#   all_counties = {"Nkangala", "eThekwini", "Aerotropolis", ...}

# Build HTML <option> strings for the dropdowns
region_options = '\n'.join(
    f'<option value="{r}">{r}</option>'
    for r in sorted(r for r in regions if r != 'DOWNDETECTOR') + ['DOWNDETECTOR']
)
rca_options    = '\n'.join(
    f'<option value="{r}">{r}</option>'
    for r in sorted(all_rcas)
)
county_options = '\n'.join(
    f'<option value="{c}">{c}</option>'
    for c in sorted(all_counties)
)


# ─── STEP 4: Inject everything into the HTML template ─────────────────────────
# The HTML is a Python f-string template. Key injection points:
#
#   {meta['last_refreshed']}    → topbar chip
#   {meta['total_regions']}     → topbar chip
#   {region_options}            → sidebar filter <select>
#   {rca_options}               → sidebar filter <select>
#   {county_options}            → sidebar filter <select>
#   {raw_json}                  → the JS line:  const PAYLOAD = {raw_json};
#
# The last one is the most important. It embeds the ENTIRE JSON payload
# (~530KB) directly into the script block. At parse time the browser treats
# it as a JS object literal — it's instantly available as PAYLOAD.
#
# Because the template is an f-string, all {{ and }} in the CSS/JS blocks
# are escaped as {{ }} to prevent Python from trying to interpolate them.
# Only the actual Python variables use single braces: {variable_name}.

html_template = f"""
...
<script>
const PAYLOAD = {raw_json};    // ← THE ENTIRE JSON IS HERE
...
</script>
"""

with open('network_dashboard.html', 'w') as f:
    f.write(html_template)


"""
=============================================================================
PART 2 — JAVASCRIPT RUNTIME LOGIC (annotated)
=============================================================================

Once the browser loads the HTML, PAYLOAD is a plain JS object. All rendering
is done by these key functions:

─────────────────────────────────────────────────────────────────────────────
FUNCTION: buildAllIncidents()
─────────────────────────────────────────────────────────────────────────────

  Flattens the nested structure into a single array of incident objects.
  This is the core "mapping" step.

  INPUT (PAYLOAD structure):
    PAYLOAD.regional_data = {
      "MPU": { Incidents: [{...}, {...}] },
      "KZN": { Incidents: [{...}, ...] },
      ...
    }

  WHAT IT DOES:
    - Iterates over every region
    - Iterates over every incident in that region
    - Spreads the incident fields into a new object
    - Adds a synthetic _region field (the region key) since individual
      incidents don't carry their own region name

  OUTPUT:
    ALL_INCIDENTS = [
      { _region: "MPU", Hub_Name: "ZEVENFONTEIN", OOS_Count: 4, RCA: "...", ... },
      { _region: "MPU", Hub_Name: "County_50",    OOS_Count: 5, RCA: "...", ... },
      { _region: "KZN", Hub_Name: "ELANDSKOP",    OOS_Count: 4, RCA: "...", ... },
      ... (22 total)
    ]

  CODE:
    function buildAllIncidents() {
      const incidents = [];
      for (const [region, rd] of Object.entries(PAYLOAD.regional_data)) {
        for (const inc of (rd.Incidents || [])) {
          incidents.push({ ...inc, _region: region });  // ← key move
        }
      }
      return incidents;
    }
    const ALL_INCIDENTS = buildAllIncidents();  // runs once on load

─────────────────────────────────────────────────────────────────────────────
FUNCTION: buildIncidentCard(inc, idx)
─────────────────────────────────────────────────────────────────────────────

  Maps a single flat incident object to an HTML string.
  Every field maps to a specific visual element:

  INCIDENT FIELD          → VISUAL ELEMENT
  ─────────────────────────────────────────
  MSDP_Priority           → .p-badge colour class (P1/P2/P3/P4)
  Hub_Name                → .inc-hub  (large bold title)
  _region                 → .region-tag (teal chip in subtitle)
  County_List[]           → .county-tag chips (purple, one per county)
  start_ts (unix)         → fmtDuration() → "2d ago" in subtitle
  OOS_Count               → .metric  coloured red/amber/white by threshold
  Failure_Probability     → .metric  coloured red/amber/green by threshold
  Average_Rank            → .metric  teal
  RCA                     → .rca-pill  styled by getRcaClass(rca)
  OOS_Location_Details{}  → nested .site-row accordion per site
    └─ .metadata.Site_Rank  → shown as "Rank #XXXX"
    └─ .alarms[]            → .alarm-table rows (Alarm, Summary, timestamp)

  COLOUR LOGIC:
    OOS_Count >= 20          → red
    OOS_Count >= 10          → amber
    else                     → white

    Failure_Prob >= 90%      → red
    Failure_Prob >= 70%      → amber
    else                     → green

    RCA contains "power"     → red pill  (rca-power class)
    RCA contains "trans/link"→ amber pill (rca-tx class)
    RCA contains "downdetector" → purple pill (rca-dd class)

─────────────────────────────────────────────────────────────────────────────
FUNCTION: applyFilters()
─────────────────────────────────────────────────────────────────────────────

  Called on every filter change, tab click, or search keystroke.
  Reads the current sidebar filter state, filters ALL_INCIDENTS,
  and calls renderIncidents() with the result.

  The filtering is purely in-memory — it never touches the DOM until
  it has the final list. This keeps it fast regardless of dataset size.

  FILTER CHAIN (all must pass for an incident to show):
    1. activeRegion tab (from region tabs at top)
    2. filterRegion dropdown (sidebar)
    3. filterPriority dropdown
    4. filterRCA dropdown
    5. filterCounty dropdown
    6. searchInput text (matches against Hub_Name, RCA, region,
                         OOS_Location_List[], County_List[])

  SPECIAL CASE — DOWNDETECTOR TAB:
    When activeRegion === 'DOWNDETECTOR', instead of renderIncidents()
    it calls buildDowndetectorPanel() which renders a completely different
    layout: sparkline charts + indicator breakdowns from the nested
    PAYLOAD.regional_data.DOWNDETECTOR.metadata block.

─────────────────────────────────────────────────────────────────────────────
FUNCTION: buildRegionTabs() and buildRegionBars()
─────────────────────────────────────────────────────────────────────────────

  Both read PAYLOAD.regional_data directly.

  buildRegionTabs():
    - Counts incidents per region: counts[r] = rd.Incidents.length
    - Sorts by count desc, pins ALL first, DOWNDETECTOR last
    - Renders a tab per region with a badge showing count

  buildRegionBars() (sidebar OOS bars):
    - Reads Total_OOS_Count per region (a pre-aggregated field in the JSON)
    - Sorts by OOS desc
    - Calculates width percentage relative to the max OOS region
    - Renders proportional fill bars

─────────────────────────────────────────────────────────────────────────────
FUNCTION: buildDowndetectorPanel()
─────────────────────────────────────────────────────────────────────────────

  DOWNDETECTOR has a completely different data structure:
    PAYLOAD.regional_data.DOWNDETECTOR.metadata = {
      TriggerData: { Baseline, Last15Min, Status },
      IndicatorDataVodacom: [ { indicator, amount, percentage }, ... ],
      IndicatorDataMTN:     [ ... ],
      History: {
        VodacomSouthAfrica: [ { total, point_in_time, tweets, indicators, other }, ... ],
        VodacomGlobal:      [ ... ],
        MTNSouthAfrica:     [ ... ]
      },
      GeoDeviceLocation: [ { device, location: {lat, lon}, ... }, ... ]
    }

  This function:
    - Renders TriggerData as 3 stat boxes (Last15Min, Baseline, Status)
    - Renders History arrays as canvas sparkline charts via drawSparkline()
    - Renders IndicatorData as breakdown pills (e.g. "66.7% Mobile Internet")
    - Still renders the 2 DOWNDETECTOR incidents via buildIncidentCard()

  drawSparkline(canvasId, data[], color, fillColor):
    - Takes a plain array of totals [2, 7, 3, 4, ...]
    - Draws a filled area chart on an HTML <canvas> element
    - Marks the peak with a dashed vertical line
    - Puts a dot on the last data point (current moment)

─────────────────────────────────────────────────────────────────────────────
FUNCTION: updateSidebarStats(list)
─────────────────────────────────────────────────────────────────────────────

  Walks the currently visible incident list and aggregates:
    - Total OOS (sum of OOS_Count)
    - Count by priority (P3, P4 etc.)
    - Power issues (RCA contains "power")
    - Transmission issues (RCA contains "transmission" or "link")

  Updates the sidebar stat boxes live. Called after every filter change
  so the sidebar always reflects what's currently on screen.

=============================================================================
PART 3 — DATA FIELD REFERENCE
=============================================================================

FIELD                   TYPE        USED FOR
─────────────────────────────────────────────────────────────────────────────
metadata.last_refreshed  string     Topbar "Last Refresh" chip
metadata.total_regions   int        Topbar chip
metadata.min_avg_rank    float      Topbar chip

regional_data[R].Total_OOS_Count   int     Sidebar OOS bar width + value
regional_data[R].Incidents[]       array   All incident cards

Incident fields:
  start_ts              unix int   Duration display ("2d ago") + sort by time
  Hub_Name              string     Card title (.inc-hub)
  County_List[]         string[]   Purple county chips in subtitle
  OOS_Count             int        Metric box + colour threshold
  Failure_Probability   string%    Metric box + colour threshold
  Average_Rank          float      Metric box (teal) + sort by rank
  Impact_15min_Count    int        Detail panel only
  VBS_Count             int        Detail panel only
  RAN_Risk_Count        int        Detail panel only
  RAN_Failed_Count      int        Detail panel only
  Potential_Failure     int        Detail panel only
  RCA                   string     RCA pill + filter + sidebar power/tx count
  MSDP_Priority         string     P-badge colour + filter
  OOS_Location_List[]   string[]   Site row headers (order/label)
  OOS_Location_Details  object     Nested per-site accordion:
    [siteName].metadata.Site_Rank  → rank display
    [siteName].alarms[]            → alarm table rows
      .Alarm                       → alarm name (amber)
      .Summary                     → alarm summary text
      .RawLastOccurrence           → unix ts → formatted time

DOWNDETECTOR-specific:
  metadata.TriggerData.Last15Min   int     Stat box
  metadata.TriggerData.Baseline    float   Stat box
  metadata.TriggerData.Status      string  Stat box (coloured)
  metadata.IndicatorDataVodacom[]  array   Breakdown pills
  metadata.IndicatorDataMTN[]      array   Breakdown pills
  metadata.History.VodacomSA[]     array   Sparkline chart data
  metadata.History.VodacomGlobal[] array   Sparkline chart data
  metadata.History.MTNSouthAfrica[]array   Sparkline chart data
  metadata.GeoDeviceLocation[]     array   Device location table in DD incidents

=============================================================================
"""