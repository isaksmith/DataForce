# Branches — pages/1_Branches.py

## Overview

The **Branches** page provides a focused view of the bank's branch network. Users can filter by state and city, view summary statistics, download the filtered data, and explore visualizations of branch distribution.

## What it shows

| Section | Description |
|---|---|
| **Filters** | Multiselect for state and city |
| **Overview** | Row/column count and basic summary stats |
| **Download** | Export filtered data as `branches_filtered.csv` |
| **Data preview** | Scrollable table of filtered rows |
| **Branches by state** | Bar chart of branch count per state |
| **Top branch cities** | Horizontal bar chart of branch count per city |
| **R blurb** | Equivalent R/Shiny code snippet for reproducing the analysis |

## Data sources

- `Hack The Plains 2026 Datasets/branches.csv`

## Key columns

| Column | Description |
|---|---|
| `branch_code` | Unique branch identifier |
| `branch_state` | Two-letter state code |
| `branch_city` | City name |

## Filters

- **State** — multiselect; filters to selected states
- **City** — multiselect; filters to selected cities
