# Error Codes — pages/4_Error_Codes.py

## Overview

The **Error Codes** page cross-references the error code reference table with actual session data to show which errors are most impactful, which features drive them, and provides a searchable detailed reference.

## What it shows

| Section | Description |
|---|---|
| **Search** | Free-text search across all columns (description, code, etc.) |
| **Overview** | Row/column count and summary stats |
| **Download** | Export filtered data as `error_codes_filtered.csv` |
| **Error impact summary** | Sortable table: error code, description, session count, top feature |
| **Error code impact scatter** | Bubble chart: x = session count, y = error code, size = volume, color = top feature |
| **Feature → error treemap** | Treemap showing which features drive which error codes (top 20 combinations) |
| **Detailed reference** | Full data preview of the filtered error code table |
| **R blurb** | Equivalent R/Shiny code snippet |

## Data sources

- `Hack The Plains 2026 Datasets/error_codes.csv` — error code reference table
- `Hack The Plains 2026 Datasets/digital_sessions.csv` — joined to compute session counts and top features per error

## Key columns

| Column | Description |
|---|---|
| `error_code` | Error code identifier (e.g., ERR_AUTH, ERR_TIMEOUT) |
| `description` | Human-readable description of the error |
| `session_count` | Number of sessions that triggered this error (derived from sessions join) |
| `top_feature` | Most common feature associated with this error (derived) |
| `feature_count` | Session count for the top feature (derived) |

## Filters

- **Search** — free-text; matches any column value (case-insensitive)
