# Feature Costs — pages/5_Feature_Costs.py

## Overview

The **Feature Costs** page displays the cost model for each banking feature, comparing the cost of a successful transaction against the cost of a failed one. This data feeds directly into the friction score pipeline's risk weighting.

## What it shows

| Section | Description |
|---|---|
| **Filter** | Multiselect for specific features |
| **Overview** | Row/column count and summary stats |
| **Download** | Export filtered data as `feature_costs_filtered.csv` |
| **Data preview** | Scrollable table of filtered rows |
| **Success vs. failure cost** | Grouped bar chart comparing cost types per feature |
| **R blurb** | Equivalent R/Shiny code snippet |

## Data sources

- `Hack The Plains 2026 Datasets/feature_costs.csv`

## Key columns

| Column | Description |
|---|---|
| `feature_canonical` | Canonical feature name |
| `avg_cost_per_success_usd` | Average cost (USD) when the feature session succeeds |
| `avg_cost_per_failure_usd` | Average cost (USD) when the feature session fails |
| `failure_cost_premium` | Difference between failure and success cost; used as risk weight in friction scoring |

## How this data is used

The `failure_cost_premium` column is joined into the friction score pipeline (`friction_score_pipeline.py`) to weight each session's friction score by the financial risk of the feature being used. Higher-premium features contribute more to the overall friction score.

## Filters

- **Feature** — multiselect; filters to selected canonical feature names
