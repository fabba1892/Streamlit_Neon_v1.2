# ⚡ NEON OPS COMMAND: DESIGN SYSTEM & ARCHITECTURE

## 1. DATA MAPPING (JSON PAYLOAD TO UI)
This maps exactly how `Phase1result.txt` feeds the Sidebar Engine (`aggregations.py`).

| Sidebar Metric | JSON Source Path | Extraction Logic |
| :--- | :--- | :--- |
| **Sites OOS** | `payload["metadata"]["total_oos_sites"]` | Direct pull from pre-calculated metadata. |
| **Hub Impacts** | `payload["metadata"]["total_hub_impacts"]` | Direct pull (Fallback: `total_incidents_shown`). |
| **P1 - P4 Priorities** | `payload["regional_data"][REGION]["Incidents"]["MSDP_Priority"]` | Loop through all regions. Tally occurrences using `collections.Counter`. |
| **RCA Distribution** | `payload["regional_data"][REGION]["Incidents"]["RCA"]` | Loop and extract text before the first colon/dash. Grab Top 5 using `most_common(5)`. |
| **Total Alarms** | `regional_data` (Incident Loop) | Raw count of every incident processed in the loop. |

---

## 2. THE NEON COLOR PALETTE
We use a strictly defined dark-mode palette to reduce eye strain during NOC shifts while highlighting critical network faults.

| Element | Hex Code | Visual Reference |
| :--- | :--- | :--- |
| **App Background** | `#0f172a` | Deep Slate (Main Screen & Sidebar Base) |
| **Component Box** | `#1e293b` | Lighter Slate (Metrics & Filter Containers) |
| **Input Fields** | `#0f172a` | Deep Slate (Inside the filter box for contrast) |
| **Text (Labels)** | `#94a3b8` | Muted Grey-Blue |
| **Text (Values)** | `#ffffff` | Crisp White |
| **Accent / Button** | `#3b82f6` | Tech Blue (RCA Badges, Form Submit) |
| **P1 / Hub Fault** | `#ef4444` | Critical Red |
| **P2 / Power** | `#f97316` | Warning Orange |
| **P3 / Warning** | `#eab308` | Alert Yellow |

---

## 3. COMPONENT ARCHITECTURE & SAFEGUARDS

### A. The HTML/CSS Injection Strategy
* **Why:** Streamlit's native metrics are too bulky and cannot be stacked tightly.
* **How:** We bypass `st.metric` and use `st.markdown(unsafe_allow_html=True)` to inject raw HTML `<div>` blocks styled perfectly by our `service/styling.py` engine.

### B. The Form Bypass (Version-Proofing)
* **The Problem:** Streamlit frequently updates its underlying React DOM, breaking CSS wrappers (`stVerticalBlockBorderWrapper`).
* **The Solution:** We wrap the Intelligent Filters in `st.sidebar.form("filter_panel")`. Forms generate an `stForm` HTML tag that is permanent across all Streamlit versions, guaranteeing our `#1e293b` background renders correctly.
* **Operational Benefit:** Using a form prevents the dashboard from recalculating on every single keystroke. Filters only apply when the NOC Engineer clicks "Apply Filters".

### C. Global Session State (`st.session_state`)
The sidebar controls the global state of the app. The following variables are registered and passed to the Main View:
* `search_query` (Text)
* `focus_filter` (Hub/Link focus)
* `rca_filter` (Dynamic Root Cause)
* `county_filter` (Location)
* `min_sites` (Integer threshold)
* `sort_type` (Rank vs. Time)