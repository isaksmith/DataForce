# Knowledge Graph — pages/9_Knowledge_Graph.py

## Overview

The **Knowledge Graph** page provides an interactive visual map of the relationships between DataForce datasets — showing primary keys, foreign key links, field descriptions, and downstream dependencies. It helps users understand how the datasets connect before exploring or joining them.

## What it shows

An interactive force-directed graph rendered with `streamlit-agraph`. Each dataset has its own graph tab showing:

| Node type | Color | Description |
|---|---|---|
| **Dataset** (blue) | `#2563eb` | The CSV file itself |
| **Key** (dark) | `#111827` | Primary or foreign key fields |
| **Field** (green) | `#059669` | Descriptive columns |
| **Related** (amber) | `#d97706` | Linked datasets (foreign key targets) |

Edges are labeled with relationship types (e.g., `contains`, `describes`, `links to`, `joins on`).

## Datasets covered

| Dataset | Key relationships shown |
|---|---|
| `customers.csv` | Links to `branches.csv` (home_branch), `digital_sessions.csv` (customer_id), `support_interactions.csv` (customer_id) |
| `digital_sessions.csv` | Links to `customers.csv`, `error_codes.csv`, `feature_costs.csv` |
| `branches.csv` | Links to `customers.csv` |
| `error_codes.csv` | Links to `digital_sessions.csv` |
| `feature_costs.csv` | Links to `digital_sessions.csv` |
| `support_interactions.csv` | Links to `customers.csv`, `digital_sessions.csv` |

## Interaction

- **Drag nodes** to rearrange the layout
- **Hover** over a node to see its description tooltip
- **Physics simulation** keeps the graph readable; nodes repel and edges act as springs
- Node size reflects importance: dataset nodes are largest, key nodes medium, field nodes smallest

## Dependencies

- `streamlit-agraph` — graph rendering library
- `dataforce_utils.apply_global_font` — consistent font styling
