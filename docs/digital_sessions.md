# Digital Sessions — pages/3_Digital_Sessions.py

## Overview

The **Digital Sessions** page analyzes customer digital banking sessions. It includes channel, outcome, and feature breakdowns, a Sankey flow diagram showing the full session journey, and a top error codes chart.

## What it shows

| Section | Description |
|---|---|
| **Filters** | Multiselect for channel, session outcome, and feature used |
| **Overview** | Row/column count and summary stats |
| **Download** | Export filtered data as `digital_sessions_filtered.csv` |
| **Data preview** | Scrollable table of filtered rows |
| **Session outcomes** | Bar chart of outcome distribution |
| **Top features used** | Horizontal bar chart of most-used features |
| **Sessions by channel** | Bar chart of session count per channel |
| **Session flow Sankey** | Three-stage Sankey: Channel → Feature → Outcome (top 8 features shown; remainder grouped as "Other features") |
| **Top error codes** | Horizontal bar chart of the 15 most frequent error codes |
| **R blurb** | Equivalent R/Shiny code snippet |

## Data sources

- `Hack The Plains 2026 Datasets/digital_sessions.csv`

## Key columns

| Column | Description |
|---|---|
| `session_id` | Unique session identifier |
| `customer_id` | Customer who initiated the session |
| `session_ts` | Session timestamp |
| `channel` | Access channel (mobile, web, etc.) — canonicalized to `channel_canonical` |
| `feature_used` | Banking feature accessed — canonicalized to `feature_used_canonical` |
| `session_outcome` | Result of the session (success, failure, abandon) |
| `error_code` | Error code if the session failed |
| `prior_session_count` | Number of prior sessions for this customer |

## Filters

- **Channel** — multiselect; filters by canonicalized channel name
- **Session outcome** — multiselect; filters by outcome (success, failure, abandon)
- **Feature used** — multiselect; filters by canonicalized feature name (up to 50 options)
