import streamlit as st

def render_top_cards(total_all, regional_data):
    """Renders regional cards: ALL -> Downdetector -> [Highest OOS Descending] -> Unknown"""
    
    if 'active_region' not in st.session_state:
        st.session_state.active_region = "ALL"

    st.markdown('<h3 style="color: #0f172a; margin-bottom: 15px; font-weight: 800;">🌍 Regional Impact Overview</h3>', unsafe_allow_html=True)

    # --- THE CASE-INSENSITIVE SORTING ALGORITHM ---
    raw_regions = list(regional_data.keys())
    ordered_regions = ["ALL"]
    
    # 1. Hunt for Downdetector (Case-Insensitive)
    dd_key = next((r for r in raw_regions if "down" in r.lower()), None)
    if dd_key:
        ordered_regions.append(dd_key)
        raw_regions.remove(dd_key)
        
    # 2. Hunt for Unknown (Case-Insensitive)
    unk_key = next((r for r in raw_regions if "unknown" in r.lower()), None)
    
    # 3. Extract standard regions and sort by OOS Count (Descending)
    standard_regions = [r for r in raw_regions if r != unk_key]
    standard_regions.sort(key=lambda r: regional_data.get(r, 0), reverse=True)
    ordered_regions.extend(standard_regions)
    
    # 4. Force Unknown to the very end
    if unk_key:
        ordered_regions.append(unk_key)

    # --- RENDER THE GRID ---
    cols = st.columns(len(ordered_regions))

    # ... (Inside render_top_cards grid loop)
    for i, col in enumerate(cols):
        reg = ordered_regions[i]
        
        # Determine the correct Icon
        icon = "🌍" if reg == "ALL" else "📉" if "down" in reg.lower() else "❓" if reg == "Unknown" else "📡"
        
        # Format explicitly for two lines with the icon
        if reg == "ALL":
            count = total_all
            label = f"{icon} ALL REGIONS\n{count}"
        else:
            count = regional_data.get(reg, 0)
            label = f"{icon} {reg}\n{count}"

        btn_type = "primary" if st.session_state.active_region == reg else "secondary"
        # ...

        with col:
            # use_container_width ensures it spans the column perfectly
            if st.button(label, key=f"card_{reg}", type=btn_type, use_container_width=True):
                st.session_state.active_region = reg
                st.rerun()

