# Customers — pages/2_Customers.py

## Overview

The **Customers** page explores the customer base. Users can filter by segment and churn flag, view summary stats, download filtered data, and examine visualizations of customer demographics and tenure.

## What it shows

| Section | Description |
|---|---|
| **Filters** | Multiselect for segment and churn flag |
| **Overview** | Row/column count and summary stats |
| **Download** | Export filtered data as `customers_filtered.csv` |
| **Data preview** | Scrollable table of filtered rows |
| **Customers by segment** | Bar chart of customer count per segment |
| **Tenure distribution** | Histogram of `tenure_months` (40 bins) |
| **Top home branches** | Horizontal bar chart of most common home branches |
| **R blurb** | Equivalent R/Shiny code snippet |

## Data sources

- `Hack The Plains 2026 Datasets/customers.csv`

## Key columns

| Column | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `segment` | Customer segment (e.g., retail, student, wealth, smb) |
| `churn_flag` | 1 if customer has churned, 0 otherwise |
| `tenure_months` | Months since account opening |
| `home_branch` | Customer's primary branch |
| `digital_enroll_ts` | Timestamp of digital banking enrollment |
| `product_count` | Number of products held |

## Filters

- **Segment** — multiselect; filters to selected customer segments
- **Churn flag** — multiselect; filters to churned (1) or active (0) customers
