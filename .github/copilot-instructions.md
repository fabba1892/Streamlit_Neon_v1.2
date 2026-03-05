# Streamlit MSDP Monitor - Workspace Instructions

## Project Overview

This is a **Streamlit-based operational dashboard** for network monitoring and incident management. The application ingests JSON data containing regional network incidents and provides an interactive interface for filtering, analyzing, and monitoring network issues by region, priority, and technology type (2G/3G/4G/5G).

**Key Purpose:** Real-time visualization and filtering of network incidents with priority-based alerts and regional KPI tracking.

## Architecture & Data Flow

### Core Modules

- **`Neon_Streamlit_App.py`** - Main application entry point; handles UI layout, sidebar filters, and data rendering
- **`data_engine.py`** - Data processing layer; parses JSON input, transforms incident data, applies filters
- **`ui_components.py`** - Reusable UI components; custom themes, KPI cards, accordions, sidebar statistics
- **`config/`** - Configuration files (if any)
- **`data/`** - Data files including regional mappings (`RAN_Region_County_Mapping_With_IDs.json`), outputs, and reference data

### Data Ingestion Flow

1. User uploads JSON file via Streamlit sidebar
2. `data_engine.load_and_prepare_neon_data()` parses the JSON
3. Regional data is normalized into a pandas DataFrame
4. Incidents are enriched with:
   - Region keys
   - County information
   - Technology counts (2G/3G/4G/5G)
   - Power and hub impact metrics
5. Filtered data is rendered in the main dashboard

### Filtering Pipeline

`apply_tactical_filters()` filters by:

- Selected regions (multiselect)
- Maximum priority level (P1-P5)
- Returns sorted DataFrame by Average_Rank

## Development Setup

### Python Version & Dependencies

- Python 3.8+ (check `requirements.txt` if exists)
- Key packages: `streamlit`, `pandas`, `json`

### Run Locally

```bash
streamlit run Neon_Streamlit_App.py
```

### Git Configuration

- Repository initialized with `git init -b main`
- Remote: `https://github.com/fabba1892/Streamlit_Neon_v1.2.git`
- `.gitignore` configured to exclude:
  - `*.xlsx` files
  - `data/Phase1result.txt`
  - `data/RAN_Region_County_Mapping_With_IDs.json`

## Code Conventions

### File Organization

- **App logic**: Single-file Streamlit app (follows Streamlit best practices)
- **Business logic**: Separated into `data_engine.py`
- **UI components**: Centralized in `ui_components.py`
- **Data**: Organized in `data/` directory

### Naming Conventions

- **Python variables**: snake_case
- **DataFrames**: Descriptive names (e.g., `filtered_df`, `regional_stats`)
- **Functions**: Verb-based (e.g., `load_`, `apply_`, `render_`, `get_`)
- **Columns**: Descriptive with underscores (e.g., `Average_Rank`, `MSDP_Priority`, `Region_Key`)

### Data Structures

- Regional data keyed by **region codes** (KZN, WES, CEN, EAS, LIM, MPU, NGA, SGS, SGC)
- Priority levels: P1 (critical) through P5 (lowest)
- Incidents contain: priority, rank, counties, technology counts, power locations, hub sites

## Common Development Tasks

### Adding a New Filter

1. Add filter widget in `Neon_Streamlit_App.py` sidebar
2. Update `apply_tactical_filters()` in `data_engine.py`
3. Test with sample JSON input

### Adding a New UI Component

1. Create function in `ui_components.py` following naming pattern `render_*()` or `inject_*()`
2. Update theme/styles if needed
3. Call from `Neon_Streamlit_App.py`

### Updating Data Processing

- Modify `load_and_prepare_neon_data()` for new data structure
- Update DataFrame column names
- Ensure backward compatibility with existing filters

## Potential Gotchas

- **JSON structure must match expected format** with "metadata" and "regional_data" keys
- **Region codes are case-sensitive** (e.g., "KZN" not "kzn")
- **Priority map hardcoded** in multiple places - update consistently if changed
- **Streamlit reruns entire script on interaction** - optimize data loading
- **OneDrive path**: Project resides in `OneDrive/Documents/Python/Streamlit` - may have sync issues

## Git Workflow

- All Python files are tracked (except those in `.gitignore`)
- Configuration and large data files are excluded
- Commit before pushing: `git add . && git commit -m "message" && git push`

## Next Steps for New AI Agent Context

When onboarding a new session:

1. Understand the JSON input structure by checking `data/Phase1result.txt` or referencing the load function
2. Verify region codes and priority mappings match current business rules
3. Test data flows with sample JSON
4. Validate filters work across all regions
