# Explorer — pages/0_Explorer.py

## Overview

The **Explorer** page is a general-purpose dataset browser. It lets users select any of the core DataForce datasets, optionally filter by a column value, view summary statistics, and explore a chart and data preview — mirroring the workflow of the companion Shiny app.

## What it shows

| Section | Description |
|---|---|
| **Dataset selector** | Dropdown to choose from all available datasets (Branches, Customers, Digital Sessions, Error Codes, Feature Costs, Support Interactions) |
| **Optional filter** | Select any column and filter to specific values (up to 100 unique options shown) |
| **Summary metrics** | Row count and column count for the filtered dataset |
| **Chart** | Dataset-specific chart (see below) |
| **Data preview** | First 500 rows of the filtered dataset |

## Dataset-specific charts

| Dataset | Chart type | Description |
|---|---|---|
| Branches | Bar chart | Branch count by state |
| Customers | Horizontal bar | Customer count by segment |
| Digital Sessions | Bar chart | Session outcome distribution |
| Error Codes | Bubble scatter | Error code impact by session volume, colored by top feature |
| Feature Costs | Grouped bar | Success vs. failure cost per feature |
| Support Interactions | Bar chart | Interaction count by type |

## Data sources

All datasets from `Hack The Plains 2026 Datasets/`:
- `branches.csv`
- `customers.csv`
- `digital_sessions.csv`
- `error_codes.csv`
- `feature_costs.csv`
- `support_interactions.csv`

## Filters

- **Dataset** — required selector
- **Filter column** — optional; any column in the selected dataset
- **Filter values** — optional multiselect; appears when a filter column is chosen
