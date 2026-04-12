# Support Interactions — pages/6_Support_Interactions.py

## Overview

The **Support Interactions** page analyzes customer support contact data. It shows how customers reach out after digital friction events, what reasons drive support volume, and how well those interactions are resolved.

## What it shows

| Section | Description |
|---|---|
| **Filters** | Multiselect for interaction type and resolution status |
| **Overview** | Row/column count and summary stats |
| **Download** | Export filtered data as `support_interactions_filtered.csv` |
| **Data preview** | Scrollable table of filtered rows |
| **Interactions by type** | Bar chart of interaction count per type (call, chat, email, etc.) |
| **Top support reasons** | Horizontal bar chart of most common reason codes |
| **Resolution mix** | Pie chart of resolution status distribution |
| **R blurb** | Equivalent R/Shiny code snippet |

## Data sources

- `Hack The Plains 2026 Datasets/support_interactions.csv`

## Key columns

| Column | Description |
|---|---|
| `interaction_id` | Unique support interaction identifier |
| `customer_id` | Customer who initiated the interaction |
| `interaction_ts` | Timestamp of the interaction |
| `interaction_type` | Channel of support (call, chat, email, branch visit) |
| `reason_code` | Coded reason for the support contact |
| `resolution_status` | Whether the interaction was resolved, unresolved, or escalated |
| `session_id` | Linked digital session (if applicable) |

## How this data is used

Support interactions are joined to digital sessions in the friction score pipeline to compute `support_followup_24h` and `support_followup_72h` flags — indicating whether a customer contacted support within 24 or 72 hours of a session. These flags are friction score components.

## Filters

- **Interaction type** — multiselect; filters by support channel
- **Resolution status** — multiselect; filters by resolution outcome
