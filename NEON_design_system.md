# ⚡ NEON OPS COMMAND: DESIGN SYSTEM & ARCHITECTURE (V2)

## 1. DATA MAPPING (JSON PAYLOAD TO UI)
Our Data Engine uses a "Hybrid Extraction" approach, trusting pre-calculated headers for speed, but falling back to manual line-by-line counting to guarantee blast-radius containment if a header fails.

| Metric / Component | JSON Source Path | Extraction Logic |
| :--- | :--- | :--- |
| **Global OOS Sites** | `metadata` -> `total_oos_sites` | Direct pull. Matches Sidebar exactly. |
| **Global Hub Impacts** | `metadata` -> `total_hub_impacts` | Direct pull (Fallback: `total_incidents_shown`). |
| **Regional Top Cards** | `regional_data` -> `[REGION]` -> `Total_OOS_Count` | **Hybrid:** Looks for pre-calculated regional header first. If missing, loops through `Incidents` and sums `OOS_Sites` line-by-line. |
| **P1 - P4 Priorities** | `regional_data` -> `Incidents` -> `MSDP_Priority` | Tally occurrences using `collections.Counter`. |
| **RCA Distribution** | `regional_data` -> `Incidents` -> `RCA` | Extract text before the first colon/dash. Grab Top 5 using `most_common(5)`. |
| **Last Sync** | `metadata` -> `last_refresh` | Injected into the bottom of the sidebar. |

---

## 2. THE NEON COLOR PALETTE
A strictly defined dark-mode palette for the Sidebar (reducing NOC eye strain) paired with a high-contrast Main Canvas to make active faults "pop."

| Element | Hex Code | Visual Reference |
| :--- | :--- | :--- |
| **Sidebar Base** | `#0f172a` | Deep Slate |
| **Sidebar Filter Box** | `#1e293b` | Lighter Slate |
| **Main Canvas Base** | `#f8fafc` | Off-White / Light Grey |
| **Interactive Cards**| `#ffffff` | Pure White (With drop shadow) |
| **Text (Labels)** | `#94a3b8` | Muted Grey-Blue |
| **Accent / Active** | `#3b82f6` | Tech Blue (RCA Badges, Form Submit, Active Card) |
| **P1 / Hub Fault** | `#ef4444` | Critical Red |
| **P2 / Power** | `#f97316` | Warning Orange |
| **P3 / Warning** | `#eab308` | Alert Yellow |

---

## 3. GAMIFICATION & SORTING ALGORITHMS
To align with NOC Gamification (Problem Children / Worst Offenders First), the UI actively overrides Streamlit's default alphabetical sorting.

* **Top Card Sequence:** `[ALL REGIONS]` -> `[DOWNDETECTOR]` -> `[Max OOS Region ... Min OOS Region]` -> `[UNKNOWN]`
* **The "Hunter" Algorithm:** Because JSON payload capitalization varies, the Python engine uses a case-insensitive hunter (`"down" in r.lower()`) to guarantee Downdetector and Unknown always lock into their specific strategic slots (Slot 2 and Last Slot), regardless of how they are spelled.

---

## 4. COMPONENT ARCHITECTURE & SAFEGUARDS

### A. The HTML/CSS Injection Strategy (Sidebar)
* **Why:** Streamlit's native metrics are too bulky.
* **How:** We bypass `st.metric` and use `st.markdown(unsafe_allow_html=True)` to inject raw HTML `<div>` blocks styled perfectly by our `service/styling.py` engine.

### B. The Form Bypass (Version-Proofing & Compact Layout)
* **The Problem:** Streamlit frequently updates its underlying React DOM, breaking standard CSS wrappers. Furthermore, updating the app on every keystroke in the Search bar slows down NOC performance.
* **The Solution:** Intelligent Filters are wrapped in `st.sidebar.form("filter_panel")`. 
* **Compact UX:** Dropdowns use embedded placeholders (e.g., "Root Cause" as the first list item). `st.columns(2)` is used inside the form to stack the "Sort Rank" and "Sort Time" buttons horizontally.

### C. The Main Canvas CSS Override
* **The Challenge:** Streamlit buttons natively hide multi-line text (`\n`) and take up too much vertical space.
* **The Fix:** Aggressive CSS targeting `[data-testid="stAppViewContainer"] [data-testid="stButton"] button`.
    * `line-height: 1.2 !important` forces both the Region Name and the Count to display.
    * `padding: 8px 5px` shrinks the button boundaries for a "snug" fit.
    * Hover states inject a `-3px translateY` lift and a drop shadow to create a 3D clickable card effect.

### D. Global Session State (`st.session_state`)
The following variables are registered and passed from the UI to the Data Engine:
* `active_region` (Triggered by Top Cards)
* `search_query` (Text input)
* `focus_filter` (Hub/Link focus)
* `rca_filter` (Dynamic Root Cause)
* `county_filter` (Location)
* `min_sites` (Integer threshold)
* `sort_type` (Rank vs. Time)